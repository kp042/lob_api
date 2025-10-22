from pydantic import BaseModel
from typing import Optional

class Token(BaseModel):
    """
    Модель ответа при успешной аутентификации.
    Возвращает access_token и его тип.
    """
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """
    Модель данных, которые хранятся внутри JWT токена.
    Обычно содержит идентификатор пользователя (username).
    """
    username: Optional[str] = None
    