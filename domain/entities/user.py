from dataclasses import dataclass
from datetime import datetime, date
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
    birthday: Optional[date]
    gender: Optional[str]
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
        password_hash: Optional[str] = None,
        birthday: Optional[date] = None,
        gender: Optional[str] = None
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
            birthday=birthday,
            gender=gender,
            role=UserType(
                type=UserTypeEnum.USER
            ),
            is_email_verified=False,
            is_phone_verified=False,
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
    
    def update_profile(
        self,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        birthday: Optional[date] = None,
        gender: Optional[str] = None,
    ) -> None:
        """Обновление только профильных данных (без sensitive информации)"""
        is_updated = False

        if first_name is not None and first_name != self.first_name:
            if not first_name.strip():
                raise ValueError("First name cannot be empty")
            self.first_name = first_name.strip()
            is_updated = True
            
        if last_name is not None and last_name != self.last_name:
            if not last_name.strip():
                raise ValueError("Last name cannot be empty")
            self.last_name = last_name.strip()
            is_updated = True
            
        if birthday is not None and birthday != self.birthday:
            self._validate_birthday(birthday)
            self.birthday = birthday
            is_updated = True
            
        if gender is not None and gender != self.gender:
            self._validate_gender(gender)
            self.gender = gender
            is_updated = True

        if is_updated:
            self.updated_at = datetime.utcnow()
    
    def change_email(self, new_email: str) -> None:
        """Смена email с обязательной повторной верификацией"""
        if not new_email:
            raise ValueError("Email cannot be empty")
        
        email_obj = Email(new_email)
        
        if self.email == email_obj:
            return  # Email не изменился
            
        self.email = email_obj
        self.is_email_verified = False
        self.updated_at = datetime.utcnow()

    
    def change_phone(self, new_phone: str) -> None:
        """Смена телефона с обязательной повторной верификацией"""
        phone_obj = Phone(new_phone)
        
        if self.phone == phone_obj:
            return
            
        self.phone = phone_obj
        self.is_phone_verified = False
        self.updated_at = datetime.utcnow()
    
    def verify_email(self) -> None:
        """Подтверждение email"""
        if self.is_email_verified:
            return
        self.is_email_verified = True
        self.updated_at = datetime.utcnow()
    
    def verify_phone(self) -> None:
        """Подтверждение телефона"""
        if self.is_phone_verified:
            return
        self.is_phone_verified = True
        self.updated_at = datetime.utcnow()
    
    def _validate_birthday(self, birthday: date) -> None:
        """Бизнес-валидация даты рождения"""
        if birthday > datetime.utcnow().date():
            raise ValueError("Birthday cannot be in the future")
    
    def _validate_gender(self, gender: str) -> None:
        """Валидация гендера"""
        allowed_genders = ['male', 'female', 'other']
        if gender.lower() not in allowed_genders:
            raise ValueError(f"Gender must be one of: {allowed_genders}")