from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class LoginRequestSchema(BaseModel):
    """Схема для входа"""
    email: EmailStr = Field(..., example="alice@example.com", min_length=1)
    password: str = Field(..., example="StrongP@ssw0rd!", min_length=1)



class UserLoginResponseSchema(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    email: EmailStr
    role: str


class LoginResponseSchema(BaseModel):
    """Схема для ответа с токенами"""
    access_token: str
    refresh_token: str
    expires_in: int
    user: UserLoginResponseSchema