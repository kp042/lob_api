from pydantic import BaseModel
from typing import Optional
from app.models.roles import UserRole


class UserBase(BaseModel):
    email: str
    username: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool
    role: UserRole
    
    class Config:
        from_attributes = True

class UserInDB(User):
    hashed_password: str

