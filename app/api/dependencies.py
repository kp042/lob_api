from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.core.security import verify_token
from app.db.session import get_db
from app.db.models.user import User as UserModel, UserRole
from app.services.auth import AuthService
from app.services.user_service import UserService


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(db)

def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(db)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service)
):    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
        
    username = verify_token(token)
    if username is None:
        raise credentials_exception
        
    user = auth_service.get_user(username)
    if user is None:
        raise credentials_exception

    return user

async def get_current_active_user(current_user = Depends(get_current_user)):    
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Inactive user"
        )
    return current_user

async def get_current_admin_user(current_user = Depends(get_current_active_user)):    
    if current_user.role.value != UserRole.ADMIN.value:        
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user
