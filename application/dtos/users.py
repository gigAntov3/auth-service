from dataclasses import dataclass
from typing import Optional, List
from uuid import UUID
from datetime import datetime, date


@dataclass
class UserResponseDTO:
    user_id: UUID
    first_name: str
    last_name: str
    email: str
    phone: str | None
    birthday: date | None
    gender: str | None
    role: str
    is_email_verified: bool
    is_phone_verified: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime


@dataclass
class UserPublicDTO:
    user_id: UUID
    first_name: str
    last_name: str
    email: str
    role: str
    created_at: datetime
    updated_at: datetime


@dataclass
class UserUpdateDTO:
    user_id: UUID
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    birthday: Optional[date] = None
    gender: Optional[str] = None