from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class Credentials:
    """Value Object для учетных данных"""
    email: Optional[str] = None
    phone: Optional[str] = None
    password: Optional[str] = None
    
    def __post_init__(self):
        if not self.email and not self.phone:
            raise ValueError("Either email or phone must be provided")