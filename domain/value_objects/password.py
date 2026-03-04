from dataclasses import dataclass
from typing import Tuple, List
import re


@dataclass(frozen=True)
class PasswordHash:
    """
    Value Object для хеша пароля.
    
    Содержит только хеш, никогда не содержит сам пароль.
    """
    value: str

    def __post_init__(self):
        """Базовая валидация хеша"""
        if not self.value or len(self.value) < 20:
            raise ValueError(f"Некорректный хеш пароля: {self.value}")


@dataclass(frozen=True)
class RawPassword:
    """
    Value Object для сырого пароля (только для создания/проверки).
    
    Существует только временно, никогда не сохраняется.
    """
    value: str

    def __post_init__(self):
        """Валидация сложности пароля"""
        errors = []
        
        if len(self.value) < 8:
            errors.append("минимум 8 символов")
        
        if not any(c.isupper() for c in self.value):
            errors.append("хотя бы одну заглавную букву")
        
        if not any(c.islower() for c in self.value):
            errors.append("хотя бы одну строчную букву")
        
        if not any(c.isdigit() for c in self.value):
            errors.append("хотя бы одну цифру")
        
        if not any(c in "!@#$%^&*" for c in self.value):
            errors.append("хотя бы один спецсимвол (!@#$%^&*)")
        
        if errors:
            raise ValueError(f"Пароль должен содержать: {', '.join(errors)}")

    def __str__(self) -> str:
        """Скрываем пароль при выводе"""
        return "********"