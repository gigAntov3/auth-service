from dataclasses import dataclass
from typing import Optional
from uuid import UUID
from datetime import datetime

@dataclass
class VerificationRequestDTO:
    """DTO для запроса кода верификации"""
    identifier: str  # email или телефон
    identifier_type: str  # "email" или "phone"

@dataclass
class VerificationRequestResponseDTO:
    """DTO для ответа на запрос верификации"""
    verification_id: UUID
    identifier: str
    identifier_type: str
    expires_at: datetime

@dataclass
class VerifyCodeDTO:
    """DTO для подтверждения кода"""
    verification_id: UUID
    code: str

@dataclass
class VerifyCodeResponseDTO:
    """DTO для ответа на подтверждение"""
    success: bool
    identifier: str
    type: str
    message: str

@dataclass
class VerifyEmailDTO:
    """DTO для верификации email при регистрации"""
    email: str
    code: str
    user_id: Optional[UUID] = None  # если нужно связать с пользователем

@dataclass
class VerifyPhoneDTO:
    """DTO для верификации телефона"""
    phone: str
    code: str
    user_id: Optional[UUID] = None