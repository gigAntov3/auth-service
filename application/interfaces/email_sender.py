from abc import ABC, abstractmethod


class EmailSender(ABC):
    """Интерфейс для отправки email"""
    
    @abstractmethod
    async def send_verification_email(self, to_email: str, full_name: str, 
                                      verification_token: str) -> None:
        """Отправить письмо для подтверждения email"""
        pass
    
    @abstractmethod
    async def send_password_reset_email(self, to_email: str, full_name: str,
                                       reset_token: str) -> None:
        """Отправить письмо для сброса пароля"""
        pass
    
    @abstractmethod
    async def send_welcome_email(self, to_email: str, full_name: str) -> None:
        """Отправить приветственное письмо"""
        pass