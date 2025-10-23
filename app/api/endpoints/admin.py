from fastapi import APIRouter, Depends, Query, HTTPException
from typing import List, Optional
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.models.user import User
from app.models.roles import UserRole
from app.api.dependencies import get_current_admin_user, get_user_service, get_current_active_user
from app.services.user_service import UserService
from app.db.session import get_db
from app.db.models.api_log import ApiLog

router = APIRouter()

class RoleUpdate(BaseModel):
    role: UserRole


@router.get("/users", response_model=List[User])
async def get_all_users(
    skip: int = Query(0, ge=0, description="Number of users to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of users to return"),
    user_service: UserService = Depends(get_user_service),
    current_user = Depends(get_current_admin_user)
):
    users = user_service.get_all_users(skip=skip, limit=limit)
    return users

@router.get("/users/{user_id}", response_model=User)
async def get_user_by_id(
    user_id: int,
    user_service: UserService = Depends(get_user_service),
    current_user = Depends(get_current_admin_user)
):
    user = user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(404, detail="User not found")
    return user

@router.put("/users/{user_id}/role")
async def update_user_role(
    user_id: int,
    role_update: RoleUpdate,
    user_service: UserService = Depends(get_user_service),
    current_user = Depends(get_current_admin_user)
):   
    updated_user = user_service.update_user_role(user_id, role_update.role)
    if not updated_user:
        raise HTTPException(404, detail="User not found")
    
    return User(
        id=updated_user.id,
        username=updated_user.username,
        email=updated_user.email,
        is_active=updated_user.is_active,
        role=updated_user.role
    )

@router.get("/logs")
async def get_api_logs(
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    skip: int = Query(0, ge=0, description="Number of logs to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of logs to return"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):    
    query = db.query(ApiLog)
    
    if user_id is not None:
        query = query.filter(ApiLog.user_id == user_id)
    
    logs = query.order_by(ApiLog.created_at.desc())\
               .offset(skip)\
               .limit(limit)\
               .all()
    
    return {
        "logs": logs,
        "total": query.count(),
        "skip": skip,
        "limit": limit
    }

@router.get("/stats")
async def get_admin_stats(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):    
    from sqlalchemy import func
    from app.db.models.user import User
    
    # User's stats
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    admin_users = db.query(User).filter(User.role == UserRole.ADMIN).count()
    
    # Log stats
    total_logs = db.query(ApiLog).count()
    today_logs = db.query(ApiLog).filter(
        func.date(ApiLog.created_at) == func.current_date()
    ).count()
    
    return {
        "users": {
            "total": total_users,
            "active": active_users,
            "admins": admin_users
        },
        "logs": {
            "total": total_logs,
            "today": today_logs
        }
    }

@router.get("/my-role")
async def get_my_role(current_user = Depends(get_current_active_user)):
    return {
        "username": current_user.username,
        "role": current_user.role,
        "is_admin": current_user.role == UserRole.ADMIN
    }

