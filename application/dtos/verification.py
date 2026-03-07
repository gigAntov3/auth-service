from dataclasses import dataclass
from typing import Optional
from uuid import UUID
from datetime import datetime

@dataclass
class VerificationRequestDTO:
    """DTO для запроса кода верификации"""
    current_user_id: UUID
    email: Optional[str] = None
    phone: Optional[str] = None

    def __post_init__(self):
        if not self.email and not self.phone:
            raise ValueError("Either email or phone must be provided")
        if self.email and self.phone:
            raise ValueError("Both email and phone cannot be provided")

@dataclass
class VerificationResponseDTO:
    """DTO для ответа на запрос верификации"""
    expires_at: datetime
    email: Optional[str] = None
    phone: Optional[str] = None

    def __post_init__(self):
        if not self.email and not self.phone:
            raise ValueError("Either email or phone must be provided")
        if self.email and self.phone:
            raise ValueError("Both email and phone cannot be provided")



@dataclass
class VerifyRequestDTO:
    """DTO для подтверждения кода"""
    current_user_id: UUID
    code: str
    email: Optional[str] = None
    phone: Optional[str] = None

    def __post_init__(self):
        if not self.email and not self.phone:
            raise ValueError("Either email or phone must be provided")
        if self.email and self.phone:
            raise ValueError("Both email and phone cannot be provided")


@dataclass
class VerifyResponseDTO:
    """DTO для ответа на подтверждение кода"""
    email: Optional[str] = None
    phone: Optional[str] = None

    def __post_init__(self):
        if not self.email and not self.phone:
            raise ValueError("Either email or phone must be provided")
        if self.email and self.phone:
            raise ValueError("Both email and phone cannot be provided")