from datetime import datetime, timedelta
from typing import Any, Union
from jose import jwt
from passlib.context import CryptContext
from app.core.config import settings

# Создаем контекст для хеширования паролей
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
"""
pbkdf2_sha256 преимущества:
- Нет ограничений по длине пароля
- Не требует внешних зависимостей (чистый Python)
- Достаточно безопасен для большинства приложений
- Встроен в Python (через hashlib)
"""

def create_access_token(
    subject: Union[str, Any], 
    expires_delta: timedelta = None
) -> str:
    """
    Создает JWT токен доступа.
    
    Args:
        subject: Идентификатор пользователя (обычно username или user_id)
        expires_delta: Время жизни токена. Если None, используется настройка по умолчанию
    
    Returns:
        Закодированный JWT токен
    """
    # Определяем время истечения токена
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    # Создаем payload (полезную нагрузку) токена
    to_encode = {
        "exp": expire,        # Время истечения (expiration)
        "sub": str(subject)   # Subject (идентификатор пользователя)
    }
    
    # Кодируем токен с использованием секретного ключа
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.SECRET_KEY, 
        algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Проверяет, соответствует ли plain_password хешу.
    
    Args:
        plain_password: Пароль в чистом виде
        hashed_password: Хешированный пароль из базы данных
    
    Returns:
        True если пароль верный, иначе False
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    Создает хеш пароля для безопасного хранения.
    
    Args:
        password: Пароль в чистом виде
    
    Returns:
        Хешированный пароль
    """
    return pwd_context.hash(password)

def verify_token(token: str) -> Union[str, None]:
    """
    Проверяет JWT токен и извлекает username из него.
    
    Args:
        token: JWT токен
    
    Returns:
        username если токен валиден, иначе None
    """
    try:
        # Декодируем токен и проверяем подпись
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        
        # Извлекаем username из payload
        username: str = payload.get("sub")
        if username is None:
            return None
            
        return username
        
    except jwt.JWTError:
        # Если токен невалиден (истек, неправильная подпись и т.д.)
        return None
