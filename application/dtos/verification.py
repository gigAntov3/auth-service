from dataclasses import dataclass
from typing import Optional
from uuid import UUID
from datetime import datetime

@dataclass
class VerificationRequestDTO:
    """DTO для запроса кода верификации"""
    email: Optional[str] = None
    phone: Optional[str] = None

    def __post_init__(self):
        if not self.email and not self.phone:
            raise ValueError("Either email or phone must be provided")

@dataclass
class VerificationRequestResponseDTO:
    """DTO для ответа на запрос верификации"""
    expires_at: datetime
    email: Optional[str] = None
    phone: Optional[str] = None

    def __post_init__(self):
        if not self.email and not self.phone:
            raise ValueError("Either email or phone must be provided")



@dataclass
class VerifyRequestDTO:
    """DTO для подтверждения кода"""
    code: str
    email: Optional[str] = None
    phone: Optional[str] = None

    def __post_init__(self):
        if not self.email and not self.phone:
            raise ValueError("Either email or phone must be provided")


@dataclass
class VerifyResponseDTO:
    """DTO для ответа на подтверждение кода"""
    email: Optional[str] = None
    phone: Optional[str] = None

    def __post_init__(self):
        if not self.email and not self.phone:
            raise ValueError("Either email or phone must be provided")