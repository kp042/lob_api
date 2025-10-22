from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.core.security import verify_token
from app.services.auth import auth_service

# Создаем экземпляр OAuth2PasswordBearer
# Этот класс автоматически извлекает токен из заголовка Authorization
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")
"""
OAuth2PasswordBearer - это схема безопасности FastAPI для OAuth2 Password Flow.
- tokenUrl: URL эндпоинта, где клиент может получить токен (наш /auth/token)
- Автоматически проверяет заголовок Authorization: Bearer <token>
"""

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Зависимость (Dependency) для получения текущего пользователя из JWT токена.
    
    Эта функция будет автоматически вызываться FastAPI для защищенных эндпоинтов.
    
    Args:
        token: JWT токен, автоматически извлеченный из заголовка
    
    Returns:
        Объект пользователя
    
    Raises:
        HTTPException: Если токен невалиден или пользователь не найден
    """
    # Создаем стандартное исключение для невалидных учетных данных
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},  # Согласно стандарту OAuth2
    )
    
    # Проверяем токен и получаем username
    username = verify_token(token)
    if username is None:
        raise credentials_exception
    
    # Ищем пользователя в базе данных
    user = auth_service.get_user(username)
    if user is None:
        raise credentials_exception
        
    return user

async def get_current_active_user(current_user = Depends(get_current_user)):
    """
    Зависимость для проверки, что пользователь активен.
    
    Наследует от get_current_user и добавляет проверку активности.
    
    Args:
        current_user: Пользователь из get_current_user
    
    Returns:
        Активный пользователь
    
    Raises:
        HTTPException: Если пользователь неактивен
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Inactive user"
        )
    return current_user
