from dataclasses import dataclass
from datetime import datetime, timedelta
from uuid import UUID, uuid4
from typing import Optional

from domain.value_objects.password import PasswordHash

@dataclass
class RefreshTokenEntity:
    id: UUID
    user_id: UUID
    token_hash: PasswordHash
    expires_at: datetime
    created_at: datetime
    revoked_at: Optional[datetime]
    ip_address: str
    user_agent: str
    device_name: str
    device_type: str
    
    @classmethod
    def create(
        cls,
        user_id: UUID,
        token_hash: str,
        ip_address: str,
        user_agent: str,
        device_name: str,
        device_type: str,
        expires_in_days: int = 30,
    ) -> 'RefreshTokenEntity':
        return cls(
            id=uuid4(),
            user_id=user_id,
            token_hash=PasswordHash(token_hash),
            expires_at=datetime.utcnow() + timedelta(days=expires_in_days),
            created_at=datetime.utcnow(),
            revoked_at=None,
            ip_address=ip_address,
            user_agent=user_agent,
            device_name=device_name,
            device_type=device_type
        )
    
    def revoke(self) -> None:
        self.revoked_at = datetime.utcnow()
    
    def is_valid(self) -> bool:
        return (
            self.revoked_at is None and
            self.expires_at > datetime.utcnow()
        )