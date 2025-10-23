from typing import Optional
from fastapi import Depends, HTTPException, status
from app.core.security import verify_password, get_password_hash, verify_token
from app.db.models.user import User as UserModel
from app.models.user import User as UserSchema, UserCreate, UserInDB
from sqlalchemy.orm import Session


class AuthService:
    """
    Сервис для управления аутентификацией и пользователями.
    Содержит бизнес-логику работы с пользователями.
    """
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_by_username(self, username: str):
        """Получает пользователя из базы данных по username"""
        return self.db.query(UserModel).filter(UserModel.username == username).first()
    
    def get_user(self, username: str):
        """Получает пользователя для внутреннего использования"""
        db_user = self.get_user_by_username(username)
        if db_user:
            return UserInDB(
                id=db_user.id,
                username=db_user.username,
                email=db_user.email,
                is_active=db_user.is_active,
                hashed_password=db_user.hashed_password
            )
        return None
    
    def authenticate_user(self, username: str, password: str):
        """Аутентифицирует пользователя"""
        db_user = self.get_user_by_username(username)
        if not db_user:
            return None
            
        if not verify_password(password, db_user.hashed_password):
            return None
            
        return UserSchema(
            id=db_user.id,
            username=db_user.username,
            email=db_user.email,
            is_active=db_user.is_active
        )
    
    def create_user(self, user_data: UserCreate):
        """Создает нового пользователя в базе данных"""
        # Проверяем, не существует ли уже пользователь
        if self.get_user_by_username(user_data.username):
            return None
        
        # Создаем нового пользователя
        hashed_password = get_password_hash(user_data.password)
        db_user = UserModel(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password,
            is_active=True
        )
        
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        
        return UserSchema(
            id=db_user.id,
            username=db_user.username,
            email=db_user.email,
            is_active=db_user.is_active
        )
    