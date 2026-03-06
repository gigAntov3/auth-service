from uuid import UUID
from pydantic import BaseModel, EmailStr, Field

from .users import UserPublicSchema


class LoginRequestSchema(BaseModel):
    """Схема для входа"""
    email: EmailStr = Field(..., description="Email пользователя", examples=["alice@example.com"])
    password: str = Field(..., description="Пароль пользователя", examples=["StrongP@ssw0rd!"])


class RegisterRequestSchema(BaseModel):
    """Схема для регистрации"""
    first_name: str = Field(..., description="Имя пользователя", examples=["Alice"])
    last_name: str = Field(..., description="Фамилия пользователя", examples=["Smith"])
    email: EmailStr = Field(..., description="Email пользователя", examples=["alice@example.com"])
    password: str = Field(..., min_length=8, description="Пароль", examples=["StrongP@ssw0rd!"])


class TokenResponseSchema(BaseModel):
    """Базовая схема для ответа с токенами"""
    access_token: str = Field(..., description="JWT токен доступа")
    refresh_token: str = Field(..., description="JWT токен обновления")
    token_type: str = Field(..., description="Тип токена", examples=["Bearer"])
    expires_in: int = Field(..., description="Время жизни токена в секундах", examples=[3600])


class LoginResponseSchema(TokenResponseSchema):
    """Схема для ответа при входе"""
    pass


class RegisterResponseSchema(TokenResponseSchema):
    """Схема для ответа при регистрации"""
    pass


class RefreshResponseSchema(TokenResponseSchema):
    """Схема для ответа при обновлении токена"""
    pass


class ChangePasswordRequestSchema(BaseModel):
    """Схема для смены пароля"""
    old_password: str = Field(..., description="Текущий пароль")
    new_password: str = Field(..., min_length=8, description="Новый пароль")