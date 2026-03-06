from abc import ABC, abstractmethod
from uuid import UUID

from domain.entities.verification_code import VerificationCodeEntity, VerificationType

class VerificationCodeRepository(ABC):
    """Интерфейс репозитория для Aggregate Root VerificationCode."""
    
    @abstractmethod
    async def save(self, verification_code: VerificationCodeEntity) -> VerificationCodeEntity:
        """Сохранить новый код."""
        pass
    
    @abstractmethod
    async def get_by_id(self, code_id: UUID) -> VerificationCodeEntity | None:
        """Получить код по ID."""
        pass
    
    @abstractmethod
    async def get_by_identifier_and_type(
        self, 
        identifier: str, 
        verification_type: VerificationType,
        exclude_expired: bool = True
    ) -> list[VerificationCodeEntity]:
        """Получить все коды для email/телефона (обычно сортируем по created_at DESC)."""
        pass
    
    @abstractmethod
    async def get_last_pending(
        self, 
        identifier: str, 
        verification_type: VerificationType
    ) -> VerificationCodeEntity | None:
        """Получить последний ожидающий код."""
        pass
    
    @abstractmethod
    async def delete_expired(self) -> int:
        """Удалить истекшие коды (для cleanup задач)."""
        pass