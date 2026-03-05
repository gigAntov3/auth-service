from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from uuid import UUID
from datetime import datetime
import re


class RegisterRequestSchema(BaseModel):
    first_name: str = Field(..., example="Alice")
    last_name: str = Field(..., example="Smith")
    email: EmailStr = Field(..., example="alice@example.com")
    password: str = Field(..., example="StrongP@ssw0rd!")
    ip_address: str = Field(..., example="192.168.0.1")
    user_agent: str = Field(..., example="Mozilla/5.0 (Windows NT 10.0; Win64; x64)")


class UserRegisterResponseSchema(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    email: EmailStr
    role: str


class RegisterResponseSchema(BaseModel):
    """Схема для ответа с токенами"""
    access_token: str
    refresh_token: str
    user: UserRegisterResponseSchema




class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
    user_id: UUID
    company_id: Optional[UUID] = None
    role: Optional[str] = None

class MessageResponse(BaseModel):
    message: str
    details: Optional[dict] = None

    
class UserLoginRequest(BaseModel):
    """Схема для входа"""
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    password: str = Field(..., min_length=1)
    
    @validator('email', 'phone', always=True)
    def validate_contact(cls, v, values):
        if 'email' in values and values['email'] is None and 'phone' in values and values['phone'] is None:
            raise ValueError('Either email or phone must be provided')
        return v


class RefreshTokenRequest(BaseModel):
    """Схема для обновления токена"""
    refresh_token: str

class UserResponse(BaseModel):
    """Схема для ответа с данными пользователя"""
    id: UUID
    email: Optional[EmailStr]
    phone: Optional[str]
    first_name: str
    last_name: str
    is_email_verified: bool
    is_phone_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class VerifyEmailRequest(BaseModel):
    """Схема для верификации email"""
    email: EmailStr
    code: str = Field(..., min_length=6, max_length=6)

class VerifyPhoneRequest(BaseModel):
    """Схема для верификации телефона"""
    phone: str
    code: str = Field(..., min_length=6, max_length=6)
    
    @validator('phone')
    def validate_phone(cls, v):
        pattern = r'^\+7[0-9]{10}$'
        if not re.match(pattern, v):
            raise ValueError('Phone must be in format +79991234567')
        return v

class MessageResponse(BaseModel):
    """Простой ответ с сообщением"""
    message: str
    details: Optional[dict] = None