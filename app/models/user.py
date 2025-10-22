from pydantic import BaseModel, EmailStr
from typing import Optional

class UserBase(BaseModel):
    """
    Базовая модель пользователя с общими полями.
    Pydantic модель обеспечивает валидацию данных.
    """
    email: str
    username: str

class UserCreate(UserBase):
    """
    Модель для создания нового пользователя.
    Добавляем поле password, которое нужно при регистрации.
    """
    password: str

class User(UserBase):
    """
    Модель пользователя для возврата из API.
    Не включает пароль для безопасности.
    """
    id: int
    is_active: bool
    
    class Config:
        from_attributes = True
        """
        Ранее называлось 'orm_mode'. Позволяет создавать модели Pydantic 
        из ORM объектов (например, из SQLAlchemy).
        """

class UserInDB(User):
    """
    Модель пользователя для внутреннего использования в базе данных.
    Включает хешированный пароль.
    """
    hashed_password: str

