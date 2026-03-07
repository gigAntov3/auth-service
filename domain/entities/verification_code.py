from dataclasses import dataclass
from random import randint
from datetime import datetime, timedelta
from uuid import UUID, uuid4
from enum import Enum
from pydantic import BaseModel, Field
from domain.exceptions import DomainException

class VerificationType(str, Enum):
    EMAIL = "email"
    PHONE = "phone"

class VerificationStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    EXPIRED = "expired"


@dataclass
class VerificationCodeEntity(BaseModel):
    """Сущность для хранения кода верификации в рамках DDD."""
    
    # --- Идентичность (Identity) ---
    id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    
    # --- Атрибуты ---
    identifier: str  # Email или номер телефона
    type: VerificationType
    code: str
    status: VerificationStatus = VerificationStatus.PENDING
    
    # --- Метаданные ---
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime
    confirmed_at: datetime | None = None
    
    # --- Попытки (защита от брутфорса) ---
    attempts_count: int = 0
    max_attempts: int = 5

    
    def __init__(self, **data):
        # Если expires_at не передан, устанавливаем по умолчанию (например, +15 минут)
        if 'expires_at' not in data and 'created_at' in data:
            data['expires_at'] = data['created_at'] + timedelta(minutes=15)
        elif 'expires_at' not in data:
            data['expires_at'] = datetime.utcnow() + timedelta(minutes=15)
        super().__init__(**data)

    @classmethod
    def create(
        cls,
        user_id: UUID,
        identifier: str,
        type: VerificationType,
        max_attempts: int = 5,
    ) -> "VerificationCodeEntity":
        return cls(
            id=uuid4(),
            user_id=user_id,
            identifier=identifier,
            type=type,
            code=cls._generate_verification_code(),
            expires_at=datetime.utcnow() + timedelta(minutes=15),
            created_at=datetime.utcnow(),
            status=VerificationStatus.PENDING,
            confirmed_at=None,
            attempts_count=0,
            max_attempts=max_attempts,
        )
    
    # --- Методы домена (бизнес-логика) ---
    
    def is_expired(self) -> bool:
        """Проверка, истек ли срок действия кода."""
        return datetime.utcnow() > self.expires_at or self.status == VerificationStatus.EXPIRED
    
    def is_used(self) -> bool:
        """Проверка, использован ли код."""
        return self.status == VerificationStatus.CONFIRMED
    
    def increment_attempts_count(self):
        self.attempts_count += 1
        
    def can_attempt(self) -> bool:
        """Можно ли попробовать ввести код (не превышен ли лимит попыток)."""
        return self.attempts_count < self.max_attempts and not self.is_expired() and not self.is_used()
    
    def verify(self, input_code: str) -> None:
        """
        Проверка введенного кода.
        Содержит бизнес-правила: проверка попыток, срока действия, совпадения кода.
        Выбрасывает исключения при ошибках.
        """
        # Проверка на использование
        if self.is_used():
            raise DomainException("Код уже был использован")
        
        # Проверка на истечение срока
        if self.is_expired():
            self.status = VerificationStatus.EXPIRED
            raise DomainException("Срок действия кода истек")
        
        # Проверка на превышение попыток
        if not self.can_attempt():
            raise DomainException("Превышено количество попыток ввода")
        
        # Увеличиваем счетчик попыток
        self.attempts_count += 1
        
        # Проверка кода
        if self.code != input_code:
            raise DomainException("Неверный код верификации")
        
        # Код верный - подтверждаем
        self.status = VerificationStatus.CONFIRMED
        self.confirmed_at = datetime.utcnow()
    
    @staticmethod
    def _generate_verification_code() -> str:
        return str(randint(100000, 999999))
    
    def refresh(self):
        """Обновить код (например, при повторной отправке)."""
        if self.is_used():
            raise DomainException("Нельзя обновить уже подтвержденный код")
        
        self.code = self._generate_verification_code()
        self.expires_at = datetime.utcnow() + timedelta(minutes=15)
        self.attempts_count = 0
        self.status = VerificationStatus.PENDING
        self.created_at = datetime.utcnow()  # Обновляем время создания