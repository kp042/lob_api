from datetime import timedelta
from fastapi import APIRouter, Depends, Header, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.core.security import create_access_token
from app.core.config import settings
from app.models.token import Token
from app.models.user import User, UserCreate, UserRole
from app.api.dependencies import get_auth_service, get_current_active_user
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.auth import AuthService


router = APIRouter()

@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    OAuth2 endpoint to get JWT token.
    
    Args:
        form_data: Form data (username and password) from the client
    
    Returns:
        JWT access token and its type
    
    Raises:
        HTTPException: If authentication failed
    """    
    user = auth_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )    
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.username, 
        expires_delta=access_token_expires
    )
    
    # Return the token in the OAuth2 format
    return {
        "access_token": access_token, 
        "token_type": "bearer"
    }

@router.post("/register", response_model=User)
async def register_user(
    user_data: UserCreate,
    x_registration_secret: str = Header(None),  # Secret key to create user
    x_admin_secret: str = Header(None),         # Secret key to create admin
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Endpoint for registering a new user.
    Requires a secret key in the X-Registration-Secret (User) and X-Admin-Secret (Admin).

    Args:
        user_data: New user details
    
    Returns:
        Created user (no password)
    
    Raises:
        HTTPException: If the user already exists
    """
    # Checking if registration is enabled
    if not settings.REGISTRATION_ENABLED:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Registration is disabled"
        )
    
    # Checking the X-Registration-Secret key
    if x_registration_secret != settings.REGISTRATION_SECRET:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid registration secret"
        )
    
    
    is_admin = False

    if x_admin_secret and x_admin_secret == settings.ADMIN_SECRET:
        is_admin = True
    # if x_admin_secret and hasattr(settings, 'ADMIN_SECRET') and settings.ADMIN_SECRET:    
    #     if x_admin_secret.strip() == settings.ADMIN_SECRET.strip():
    #         is_admin = True
    #         print("DEBUG: Admin user will be created")

    # Check if a user with this username already exists
    if auth_service.get_user(user_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    # Create a new user
    new_user = auth_service.create_user(user_data, is_admin)

    # DEBUG: Check which role has been installed
    print(f"DEBUG: Created user role = '{new_user.role}'")

    return new_user

@router.get("/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """
    Endpoint to get information about current user
    
    Args:
        current_user: Current authenticated user
    
    Returns:
        User object with information about the current user
    """
    return User(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        is_active=current_user.is_active,
        role=current_user.role
    )
