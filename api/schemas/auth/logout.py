from pydantic import BaseModel


class LogoutRequestSchema(BaseModel):
    """Схема для входа"""
    refresh_token: str

