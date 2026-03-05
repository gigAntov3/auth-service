from pydantic import BaseModel


class JWTSettings(BaseModel):
    """JWT settings"""

    secret_key: str = "super-secret-key-for-development-change-it"
    algorithm: str = "HS256"
    
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 30