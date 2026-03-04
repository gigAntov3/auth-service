from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from uuid import UUID
from datetime import datetime
from enum import Enum


class RoleTypeDTO(str, Enum):
    """DTO для типов ролей"""
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    OWNER = "owner"
    DIRECTOR = "director"
    MANAGER = "manager"
    ACCOUNTANT = "accountant"
    CALL_CENTER = "call_center"
    USER = "user"


class RoleBaseDTO(BaseModel):
    """Базовый DTO роли"""
    role_type: RoleTypeDTO
    branch_id: Optional[UUID] = None


class RoleCreateDTO(RoleBaseDTO):
    """DTO для создания роли"""
    user_id: UUID
    assigned_by: Optional[UUID] = None


class RoleDTO(RoleBaseDTO):
    """DTO для ответа с данными роли"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    user_id: UUID
    assigned_at: datetime
    assigned_by: Optional[UUID] = None
    branch_name: Optional[str] = None  # для отображения


class RoleAssignmentDTO(BaseModel):
    """DTO для назначения роли"""
    user_id: UUID
    role_type: RoleTypeDTO
    branch_id: Optional[UUID] = None
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "role_type": "manager",
                "branch_id": "123e4567-e89b-12d3-a456-426614174001"
            }
        }
    }


class RoleRemovalDTO(BaseModel):
    """DTO для удаления роли"""
    user_id: UUID
    role_type: RoleTypeDTO
    branch_id: Optional[UUID] = None