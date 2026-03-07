from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from typing import Optional

from domain.entities.verification_code import VerificationType


class VerificationRequestSchema(BaseModel):
    """Схема для запроса верификации"""
    email: Optional[EmailStr] = Field(
        default=None, 
        description="Email для отправки кода верификации", 
        examples=["alice@example.com"]
    )
    phone: Optional[str] = Field(
        default=None, 
        description="Номер телефона для отправки кода верификации", 
        examples=["+79999999999"]
    )

class VerificationResponseSchema(BaseModel):
    """Схема для ответа на запрос верификации"""
    success: bool = Field(..., description="Статус верификации")
    email: Optional[EmailStr] = Field(..., description="Идентификатор пользователя", examples=["alice@example.com"])
    phone: Optional[str] = Field(..., description="Идентификатор пользователя", examples=["+79999999999"])
    expires_at: datetime = Field(..., description="Время истечения верификации")
    message: str = Field(..., description="Сообщение об успехе")


class VerifyRequestSchema(BaseModel):
    """Схема для подтверждения верификации"""
    email: Optional[EmailStr] = Field(default=None, description="Идентификатор пользователя", examples=["alice@example.com"])
    phone: Optional[str] = Field(default=None, description="Идентификатор пользователя", examples=["+79999999999"])
    code: str = Field(..., description="Код верификации", examples=["123456"], min_length=6, max_length=6)


class VerifyResponseSchema(BaseModel):
    """Схема для ответа при успешной верификации"""
    success: bool = Field(..., description="Статус верификации")
    email: Optional[EmailStr] = Field(..., description="Идентификатор пользователя", examples=["alice@example.com"])
    phone: Optional[str] = Field(..., description="Идентификатор пользователя", examples=["+79999999999"])
    message: str = Field(..., description="Сообщение об успехе")