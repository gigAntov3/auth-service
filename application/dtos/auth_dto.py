from dataclasses import dataclass
from typing import Optional, List
from uuid import UUID
from datetime import datetime

from domain.entities.user import UserEntity

@dataclass
class RegisterRequestDTO:
    first_name: str
    last_name: str
    email: str
    password: str
    ip_address: str
    user_agent: str


@dataclass
class RegisterResponseDTO:
    access_token: str
    refresh_token: str
    expires_in: int
    user_id: UUID
    first_name: str
    last_name: str
    email: str
    role: Optional[str] = None




@dataclass
class LoginDTO:
    email: str
    password: str

@dataclass
class TokenResponseDTO:
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
    user_id: UUID
    company_id: Optional[UUID] = None
    role: Optional[str] = None

@dataclass
class AuthResponseDTO:
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
    user_id: UUID
    company_id: Optional[UUID] = None
    role: Optional[str] = None

@dataclass
class RefreshTokenDTO:
    refresh_token: str

@dataclass
class VerifyEmailDTO:
    email: str
    code: str

@dataclass
class VerifyPhoneDTO:
    phone: str
    code: str

@dataclass
class UserDTO:
    id: UUID
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None
    is_email_verified: bool = False
    is_phone_verified: bool = False
    
    @classmethod
    def from_entity(cls, user: UserEntity) -> 'UserDTO':
        """Создать DTO из сущности пользователя"""
        return cls(
            id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            phone=user.phone,
            is_email_verified=user.is_email_verified,
            is_phone_verified=user.is_phone_verified
        )
    
    @classmethod
    def from_entity_list(cls, users: List[UserEntity]) -> List['UserDTO']:
        """Создать список DTO из списка сущностей"""
        return [cls.from_entity(user) for user in users]