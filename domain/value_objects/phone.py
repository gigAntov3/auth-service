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
        pattern = r'^\+7 \(\d{3}\) \d{3}-\d{2}-\d{2}$'
        return bool(re.match(pattern, self.value))
