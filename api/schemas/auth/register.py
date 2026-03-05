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
    expires_in: int
    user: UserRegisterResponseSchema