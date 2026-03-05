from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from domain.value_objects.email import Email
from domain.value_objects.phone import Phone
from domain.value_objects.password import PasswordHash
from domain.value_objects.user_type import UserType, UserTypeEnum

@dataclass
class UserEntity:
    id: UUID
    email: Email
    phone: Optional[Phone]
    password_hash: PasswordHash
    first_name: str
    last_name: str
    role: UserType
    is_email_verified: bool
    is_phone_verified: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    @classmethod
    def create(
        cls,
        first_name: str,
        last_name: str,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        password_hash: Optional[str] = None
    ) -> 'UserEntity':
        """Фабричный метод для создания нового пользователя"""
        if not email and not phone:
            raise ValueError("Either email or phone must be provided")
        
        return cls(
            id=uuid4(),
            email=Email(email),
            phone=Phone(phone) if phone else None,
            password_hash=PasswordHash(password_hash),
            first_name=first_name,
            last_name=last_name,
            role=UserType(
                type=UserTypeEnum.USER
            ),
            is_email_verified=False,
            is_phone_verified=False,
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
    
    def verify_email(self) -> None:
        self.is_email_verified = True
        self.updated_at = datetime.utcnow()
    
    def verify_phone(self) -> None:
        self.is_phone_verified = True
        self.updated_at = datetime.utcnow()
    
    def deactivate(self) -> None:
        self.is_active = False
        self.updated_at = datetime.utcnow()
    
    def get_full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"