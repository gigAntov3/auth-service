from pydantic import BaseModel


class EnvironmentSettings(BaseModel):
    """Environment settings"""

    environment: str = "development"

    debug: bool = False
    testing: bool = False

    log_level: str = "INFO"

    app_name: str = "auth-service"
    app_version: str = "1.0.0"