from datetime import timedelta
from fastapi import APIRouter, Depends, Header, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.core.security import create_access_token
from app.core.config import settings
from app.models.token import Token
from app.models.user import User, UserCreate
from app.api.dependencies import get_auth_service, get_current_active_user
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.auth import AuthService

# Создаем роутер для аутентификации
# Префикс "/auth" будет добавлен ко всем эндпоинтам этого роутера
router = APIRouter()

@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    OAuth2 совместимый эндпоинт для получения JWT токена.
    
    Этот эндпоинт соответствует стандарту OAuth2 Password Flow.
    FastAPI автоматически генерирует форму ввода в Swagger UI.
    
    Args:
        form_data: Данные формы (username и password) от клиента
    
    Returns:
        JWT access token и его тип
    
    Raises:
        HTTPException: Если аутентификация не удалась
    """    
    # Аутентифицируем пользователя
    user = auth_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Создаем access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.username, 
        expires_delta=access_token_expires
    )
    
    # Возвращаем токен в стандартном формате OAuth2
    return {
        "access_token": access_token, 
        "token_type": "bearer"
    }

@router.post("/register", response_model=User)
async def register_user(
    user_data: UserCreate,
    x_registration_secret: str = Header(None),  # Секретный ключ в заголовке
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Эндпоинт для регистрации нового пользователя.
    Требует секретный ключ в заголовке X-Registration-Secret.

    Args:
        user_data: Данные нового пользователя
    
    Returns:
        Созданный пользователь (без пароля)
    
    Raises:
        HTTPException: Если пользователь уже существует
    """
    # Проверяем, включена ли регистрация
    if not settings.REGISTRATION_ENABLED:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Registration is disabled"
        )
    
    # Проверяем секретный ключ
    if x_registration_secret != settings.REGISTRATION_SECRET:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid registration secret"
        )

    # Проверяем, не существует ли уже пользователь с таким username
    if auth_service.get_user(user_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    # Создаем нового пользователя
    new_user = auth_service.create_user(user_data)
    

    return new_user

@router.get("/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """
    Защищенный эндпоинт для получения информации о текущем пользователе.
    
    Демонстрирует использование зависимостей для защиты эндпоинтов.
    Требует валидный JWT токен.
    
    Args:
        current_user: Текущий аутентифицированный пользователь (автоматически)
    
    Returns:
        Информация о текущем пользователе
    """
    return User(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        is_active=current_user.is_active
    )
