from dataclasses import dataclass
from typing import Optional, List
from uuid import UUID
from datetime import datetime


@dataclass
class UserResponseDTO:
    id: UUID
    first_name: str
    last_name: str
    email: str
    phone: str | None
    role: str
    is_email_verified: bool
    is_phone_verified: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime