from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
from enum import Enum


class TokenType(str, Enum):
    """Типы токенов"""
    ACCESS = "access"
    REFRESH = "refresh"
    EMAIL_VERIFICATION = "email_verification"
    PASSWORD_RESET = "password_reset"


class TokenDTO(BaseModel):
    """DTO для токена"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds
    refresh_expires_in: int  # seconds


class LoginRequestDTO(BaseModel):
    """Запрос на вход"""
    email: EmailStr
    password: str = Field(..., min_length=1)
    remember_me: bool = False
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "user@example.com",
                "password": "StrongP@ssw0rd",
                "remember_me": False
            }
        }
    }


class LoginResponseDTO(BaseModel):
    """Ответ после успешного входа"""
    user_id: UUID
    email: EmailStr
    full_name: str
    tokens: TokenDTO
    permissions: Dict[str, List[str]]
    
    model_config = ConfigDict(from_attributes=True)


class RegisterRequestDTO(BaseModel):
    """Запрос на регистрацию"""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    full_name: str = Field(..., min_length=2, max_length=255)
    invite_code: Optional[str] = None
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Дополнительная валидация пароля"""
        if not any(c.isupper() for c in v):
            raise ValueError('Пароль должен содержать хотя бы одну заглавную букву')
        if not any(c.isdigit() for c in v):
            raise ValueError('Пароль должен содержать хотя бы одну цифру')
        if not any(c in "!@#$%^&*" for c in v):
            raise ValueError('Пароль должен содержать хотя бы один спецсимвол (!@#$%^&*)')
        return v
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "newuser@example.com",
                "password": "StrongP@ssw0rd",
                "full_name": "John Doe",
                "invite_code": None
            }
        }
    }


class RegisterResponseDTO(BaseModel):
    """Ответ после регистрации"""
    user_id: UUID
    email: EmailStr
    full_name: str
    message: str = "Регистрация успешна. Подтвердите email."
    requires_verification: bool = True
    
    model_config = ConfigDict(from_attributes=True)


class RefreshTokenRequestDTO(BaseModel):
    """Запрос на обновление токена"""
    refresh_token: str


class RefreshTokenResponseDTO(BaseModel):
    """Ответ с новым токеном"""
    access_token: str
    expires_in: int


class VerifyEmailRequestDTO(BaseModel):
    """Запрос на подтверждение email"""
    token: str


class VerifyEmailResponseDTO(BaseModel):
    """Ответ на подтверждение email"""
    message: str = "Email подтвержден успешно"
    email: EmailStr


class ForgotPasswordRequestDTO(BaseModel):
    """Запрос на сброс пароля"""
    email: EmailStr


class ForgotPasswordResponseDTO(BaseModel):
    """Ответ на запрос сброса пароля"""
    message: str = "Если email существует, ссылка для сброса отправлена"


class ResetPasswordRequestDTO(BaseModel):
    """Запрос на сброс пароля с токеном"""
    token: str
    new_password: str = Field(..., min_length=8, max_length=100)
    
    @field_validator('new_password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not any(c.isupper() for c in v):
            raise ValueError('Пароль должен содержать хотя бы одну заглавную букву')
        if not any(c.isdigit() for c in v):
            raise ValueError('Пароль должен содержать хотя бы одну цифру')
        if not any(c in "!@#$%^&*" for c in v):
            raise ValueError('Пароль должен содержать хотя бы один спецсимвол (!@#$%^&*)')
        return v


class ResetPasswordResponseDTO(BaseModel):
    """Ответ на сброс пароля"""
    message: str = "Пароль успешно изменен"


class ChangePasswordRequestDTO(BaseModel):
    """Запрос на изменение пароля"""
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)
    
    @field_validator('new_password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not any(c.isupper() for c in v):
            raise ValueError('Пароль должен содержать хотя бы одну заглавную букву')
        if not any(c.isdigit() for c in v):
            raise ValueError('Пароль должен содержать хотя бы одну цифру')
        if not any(c in "!@#$%^&*" for c in v):
            raise ValueError('Пароль должен содержать хотя бы один спецсимвол (!@#$%^&*)')
        return v


class ChangePasswordResponseDTO(BaseModel):
    """Ответ на изменение пароля"""
    message: str = "Пароль успешно изменен"


class LogoutResponseDTO(BaseModel):
    """Ответ на выход"""
    message: str = "Успешный выход"