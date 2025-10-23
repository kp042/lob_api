from datetime import datetime, timedelta
from typing import Any, Union
from jose import jwt
from passlib.context import CryptContext
from app.core.config import settings

# Context for pass hashing
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def create_access_token(
    subject: Union[str, Any], 
    expires_delta: timedelta = None
) -> str:
    """
    Generates a JWT access token

    Args:
        subject: User ID
        expires_delta: Token lifetime. If None, the default setting is used.

    Returns:
        Encoded JWT token
    """    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    # Token's payload
    to_encode = {
        "exp": expire,        # expiration
        "sub": str(subject)   # subject (user_id)
    }    
    # Encrypting a token using a secret key
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.SECRET_KEY, 
        algorithm=settings.ALGORITHM
    )    
    return encoded_jwt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Checks if plain_password matches the hash
    
    Args:
        plain_password: Unencrypted password
        hashed_password: Hashed password
    
    Returns:
        True if the password is correct, otherwise False
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    Creates a password hash for secure storage
    
    Args:
        password: Unencrypted password
    
    Returns:
        Hashed password
    """
    return pwd_context.hash(password)

def verify_token(token: str) -> Union[str, None]:
    """
    Validates the JWT token and extracts the username from it
    
    Args:
        token: JWT token
    
    Returns:
        username if the token is valid, otherwise None
    """
    try:
        # Decode the token and verify the signature
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )        
        # Extract the username from the payload
        username: str = payload.get("sub")
        if username is None:
            return None
        return username
    except jwt.JWTError:
        # If the token is invalid (expired, invalid signature, etc.)
        return None
