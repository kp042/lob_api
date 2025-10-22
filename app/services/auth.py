from typing import Optional
from fastapi import Depends, HTTPException, status
from app.core.security import verify_password, get_password_hash, verify_token
from app.models.user import User, UserCreate, UserInDB


# Временная "база данных" для демонстрации
# В РЕАЛЬНОМ ПРОЕКТЕ замените на настоящую базу данных!
fake_users_db = {
    "testuser": {
        "id": 1,
        "username": "testuser",
        "email": "test@example.com",
        "hashed_password": get_password_hash("testpassword"),
        "is_active": True,
    }
}

class AuthService:
    """
    Сервис для управления аутентификацией и пользователями.
    Содержит бизнес-логику работы с пользователями.
    """
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """
        Аутентифицирует пользователя по username и password.
        
        Args:
            username: Имя пользователя
            password: Пароль в чистом виде
        
        Returns:
            User object если аутентификация успешна, иначе None
        """
        # Ищем пользователя в "базе данных"
        user_dict = fake_users_db.get(username)
        if not user_dict:
            return None
            
        # Проверяем пароль
        if not verify_password(password, user_dict["hashed_password"]):
            return None
            
        # Возвращаем пользователя без хешированного пароля
        return User(**user_dict)
    
    def get_user(self, username: str) -> Optional[UserInDB]:
        """
        Получает пользователя из базы данных по username.
        
        Args:
            username: Имя пользователя
        
        Returns:
            UserInDB object если пользователь найден, иначе None
        """
        user_dict = fake_users_db.get(username)
        if user_dict:
            return UserInDB(**user_dict)
        return None
    
    def create_user(self, user: UserCreate) -> User:
        """
        Создает нового пользователя.
        
        Args:
            user: Данные для создания пользователя
        
        Returns:
            Созданный пользователь (без пароля)
        """
        # Преобразуем модель в словарь
        user_dict = user.model_dump()
        
        # Хешируем пароль перед сохранением
        user_dict["hashed_password"] = get_password_hash(user.password)
        user_dict["id"] = len(fake_users_db) + 1
        user_dict["is_active"] = True
        
        # Удаляем пароль в чистом виде из словаря
        user_dict.pop("password")
        
        # Сохраняем пользователя в "базу данных"
        fake_users_db[user.username] = user_dict
        
        # Возвращаем пользователя без хешированного пароля
        return User(**user_dict)


# Создаем экземпляр сервиса для использования в эндпоинтах
auth_service = AuthService()
