from pydantic import BaseModel


class RefreshRequestSchema(BaseModel):
    """Схема для входа"""
    refresh_token: str


class RefreshResponseSchema(BaseModel):
    """Схема для ответа с токенами"""
    access_token: str
    refresh_token: str
    expires_in: int