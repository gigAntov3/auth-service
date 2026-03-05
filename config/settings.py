from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict

from config.environment import EnvironmentSettings
from config.database import DatabaseSettings
from config.jwt import JWTSettings
from config.email import EmailSettings
from config.cors import CorsSettings

class Settings(BaseSettings):
    """Application settings"""
    
    environment: EnvironmentSettings = EnvironmentSettings()
    database: DatabaseSettings = DatabaseSettings()
    jwt: JWTSettings = JWTSettings()
    email: EmailSettings = EmailSettings()
    cors: CorsSettings = CorsSettings()

    model_config = SettingsConfigDict(
        env_file=(".env.template", ".env"),
        case_sensitive=False,
        env_nested_delimiter="__",
        env_prefix="CONFIG__",
    )


settings = Settings()