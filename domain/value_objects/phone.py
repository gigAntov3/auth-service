from dataclasses import dataclass
import re
from typing import Optional


@dataclass(frozen=True)
class Phone:
    """
    Value Object для email адреса.
    
    Immutable: после создания изменить нельзя.
    Содержит логику валидации email.
    """
    value: str

    def __post_init__(self):
        if not self._is_valid():
            raise ValueError(f"Некорректный номер телефона: {self.value}")
        
    def _is_valid(self) -> bool:
        # Удаляем все нецифровые символы кроме +
        normalized = re.sub(r'[^\d+]', '', self.value)
        # Проверяем что это +7 и 10 цифр после
        pattern = r'^\+7\d{10}$'
        return bool(re.match(pattern, normalized))
