from pydantic import BaseModel


class EmailSettings(BaseModel):
    """SMTP settings"""

    host: str = "localhost"
    port: int = 1025

    username: str | None = None
    password: str | None = None

    from_email: str = "noreply@example.com"
    from_name: str = "Auth Service"

    use_tls: bool = False
    use_ssl: bool = False

    timeout: int = 10

    starttls: bool = False

    email_enabled: bool = True