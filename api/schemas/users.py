from uuid import UUID
from typing import Optional
from datetime import datetime, date
from pydantic import BaseModel, ConfigDict, EmailStr, Field

from .base import TimestampSchema, UUIDMixin


class UserBaseSchema(BaseModel):
    """Базовая схема пользователя"""
    first_name: str = Field(..., description="Имя пользователя", examples=["Alice"])
    last_name: str = Field(..., description="Фамилия пользователя", examples=["Smith"])
    email: EmailStr = Field(..., description="Email пользователя", examples=["alice@example.com"])
    phone: Optional[str] = Field(None, description="Номер телефона пользователя", examples=["+1234567890"])
    birthday: Optional[date] = Field(None, description="Дата рождения пользователя", examples=["2000-01-01"])
    gender: Optional[str] = Field(None, description="Пол пользователя", examples=["male", "female"])
    role: str = Field(..., description="Роль пользователя в системе", examples=["user", "admin", "super_admin"])
    is_active: bool = Field(True, description="Активен ли пользователь")
    is_email_verified: bool = Field(False, description="Подтверждён ли email")
    is_phone_verified: bool = Field(False, description="Подтверждён ли номер телефона")


class UserUpdateSchema(BaseModel):
    """Схема для обновления пользователя"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    birthday: Optional[date] = None
    gender: Optional[str] = None
    
    class Config:
        extra = "forbid"
        

class UserSchema(UserBaseSchema, UUIDMixin, TimestampSchema):
    """Полная схема пользователя (ответ)"""
    pass


class UserPublicSchema(UUIDMixin, TimestampSchema):
    """Публичная информация о пользователе"""
    id: UUID = Field(..., description="Уникальный идентификатор")
    first_name: str = Field(..., description="Имя пользователя")
    last_name: str = Field(..., description="Фамилия пользователя")
    email: EmailStr = Field(..., description="Email пользователя")
    role: str = Field(..., description="Роль пользователя")
    
    model_config = ConfigDict(from_attributes=True)