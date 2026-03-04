from abc import ABC, abstractmethod


class PasswordHasher(ABC):
    """Интерфейс для хеширования паролей"""
    
    @abstractmethod
    def hash(self, password: str) -> str:
        """Хешировать пароль"""
        pass
    
    @abstractmethod
    def verify(self, plain_password: str, hashed_password: str) -> bool:
        """Проверить пароль"""
        pass