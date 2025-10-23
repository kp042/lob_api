from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.models.user import User as UserModel
from app.models.roles import UserRole


class UserService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_all_users(self, skip: int = 0, limit: int = 100) -> List[UserModel]:
        return self.db.query(UserModel) \
            .order_by(UserModel.created_at.desc()) \
            .offset(skip) \
            .limit(limit) \
            .all()
    
    def get_user_by_id(self, user_id: int) -> Optional[UserModel]:
        return self.db.query(UserModel).filter(UserModel.id == user_id).first()
    
    def update_user_role(self, user_id: int, role: UserRole) -> Optional[UserModel]:
        user = self.get_user_by_id(user_id)
        if user:
            # print(f"DEBUG: Before update - User role: {user.role}")
            user.role = role
            self.db.commit()
            self.db.refresh(user)
            # print(f"DEBUG: After update - User role: {user.role}")
        return user
    
    def deactivate_user(self, user_id: int) -> Optional[UserModel]:
        user = self.get_user_by_id(user_id)
        if user:
            user.is_active = False
            self.db.commit()
            self.db.refresh(user)
        return user
   
