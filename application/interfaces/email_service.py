from abc import ABC, abstractmethod

class EmailService(ABC):
    """Интерфейс для отправки email"""
    
    @abstractmethod
    async def send_verification_code(self, to_email: str, code: str) -> None:
        pass
    
    @abstractmethod
    async def send_invitation(self, to_email: str, company_name: str, invite_link: str) -> None:
        pass
    
    @abstractmethod
    async def send_password_reset(self, to_email: str, reset_link: str) -> None:
        pass