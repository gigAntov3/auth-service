from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List
from uuid import UUID
from datetime import datetime

from application.dtos.role_dto import RoleDTO


class UserBaseDTO(BaseModel):
    """Базовый DTO пользователя"""
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=255)
    is_active: bool = True


class UserCreateDTO(UserBaseDTO):
    """DTO для создания пользователя"""
    password: str = Field(..., min_length=8, max_length=100)
    home_branch_id: Optional[UUID] = None


class UserUpdateDTO(BaseModel):
    """DTO для обновления пользователя"""
    full_name: Optional[str] = Field(None, min_length=2, max_length=255)
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None


class UserDTO(UserBaseDTO):
    """DTO для ответа с данными пользователя"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    is_email_verified: bool
    created_at: datetime
    updated_at: datetime
    last_login_at: Optional[datetime] = None
    roles: List[RoleDTO] = []


class UserListDTO(BaseModel):
    """DTO для списка пользователей"""
    items: List[UserDTO]
    total: int
    page: int
    size: int
    pages: int


class UserPermissionsDTO(BaseModel):
    """DTO для разрешений пользователя"""
    user_id: UUID
    email: EmailStr
    permissions: dict  # branch_id -> list of roles