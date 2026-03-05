from typing import List
from pydantic import BaseModel


class CorsSettings(BaseModel):
    """CORS settings"""

    # Разрешённые источники
    origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
    ]

    # Разрешённые HTTP методы
    allow_methods: List[str] = [
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE",
        "OPTIONS"
    ]

    # Разрешённые заголовки
    allow_headers: List[str] = [
        "Authorization",
        "Content-Type",
        "Accept",
        "Origin",
        "User-Agent",
    ]

    # Можно ли отправлять cookies / credentials
    allow_credentials: bool = True

    # Какие заголовки браузер может читать
    expose_headers: List[str] = [
        "Content-Length",
        "Content-Type"
    ]

    # Кэш preflight запроса (в секундах)
    max_age: int = 600