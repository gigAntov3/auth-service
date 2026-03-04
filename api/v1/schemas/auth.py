from uuid import UUID
from pydantic import BaseModel, EmailStr


class RegisterRequestSchema(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    password: str


class RegisterResponseSchema(BaseModel):
    user_id: UUID
    email: EmailStr
    full_name: str
    message: str = "Регистрация успешна. Подтвердите email."
    requires_verification: bool = True