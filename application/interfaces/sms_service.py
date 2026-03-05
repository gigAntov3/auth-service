from abc import ABC, abstractmethod

class SmsService(ABC):
    """Интерфейс для отправки SMS"""
    
    @abstractmethod
    async def send_verification_code(self, to_phone: str, code: str) -> None:
        pass
    
    @abstractmethod
    async def send_notification(self, to_phone: str, message: str) -> None:
        pass