from uuid import UUID

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


# Общие базовые классы
class MessageResponseSchema(BaseModel):
    success: bool
    message: str


class TimestampSchema(BaseModel):
    """Схема с временными метками"""
    created_at: datetime = Field(..., description="Дата и время создания")
    updated_at: datetime = Field(..., description="Дата и время последнего обновления")
    
    model_config = ConfigDict(from_attributes=True)


class UUIDMixin(BaseModel):
    """Mixin для UUID идентификатора"""
    id: UUID = Field(..., description="Уникальный идентификатор")
    
    model_config = ConfigDict(from_attributes=True)