from uuid import UUID

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class GetUserResponseSchema(BaseModel):
    id: UUID = Field(..., description="Уникальный идентификатор пользователя")
    first_name: str = Field(..., description="Имя пользователя")
    last_name: str = Field(..., description="Фамилия пользователя")
    email: EmailStr = Field(..., description="Email пользователя")
    phone: str | None = Field(None, description="Номер телефона пользователя")
    role: str = Field(..., description="Роль пользователя в системе")
    is_email_verified: bool = Field(..., description="Подтверждён ли email")
    is_phone_verified: bool = Field(..., description="Подтверждён ли номер телефона")
    is_active: bool = Field(..., description="Активен ли пользователь")
    created_at: datetime = Field(..., description="Дата и время создания пользователя")
    updated_at: datetime = Field(..., description="Дата и время последнего обновления")