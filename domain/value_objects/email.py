from dataclasses import dataclass
import re
from typing import Optional


@dataclass(frozen=True)
class Email:
    """
    Value Object для email адреса.
    
    Immutable: после создания изменить нельзя.
    Содержит логику валидации email.
    """
    value: str

    def __post_init__(self):
        """Валидация при создании"""
        if not self._is_valid():
            raise ValueError(f"Некорректный email адрес: {self.value}")

    def _is_valid(self) -> bool:
        """
        Проверка корректности email.
        Используем упрощенную, но достаточную валидацию.
        """
        if not self.value or len(self.value) > 254:
            return False
        
        # Базовый паттерн для email
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, self.value))

    @property
    def domain(self) -> str:
        """Возвращает домен email (часть после @)"""
        parts = self.value.split('@')
        return parts[1] if len(parts) > 1 else ''

    @property
    def local_part(self) -> str:
        """Возвращает локальную часть email (часть до @)"""
        parts = self.value.split('@')
        return parts[0] if len(parts) > 0 else ''

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return f"Email('{self.value}')"