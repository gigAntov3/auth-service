from pydantic import BaseModel


class DatabaseSettings(BaseModel):
    """Database settings"""

    driver: str = "sqlite+aiosqlite"

    host: str = "localhost"
    port: int = 5432
    name: str = "auth_db"
    user: str = "postgres"
    password: str = "postgres"

    sqlite_path: str = "./auth_service.db"

    echo: bool = False

    @property
    def url(self) -> str:
        """Build database URL"""

        if "sqlite" in self.driver:
            return f"{self.driver}:///{self.sqlite_path}"

        return (
            f"{self.driver}://"
            f"{self.user}:{self.password}"
            f"@{self.host}:{self.port}"
            f"/{self.name}"
        )