from sqlalchemy import Column, String, DateTime, Integer, Enum, Boolean, select, and_, desc
from sqlalchemy.dialects.postgresql import UUID
import uuid

from datetime import datetime

from domain.entities.verification_code import VerificationType, VerificationStatus

from .base import Base


class VerificationCodeModel(Base):
    __tablename__ = "verification_codes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    identifier = Column(String(255), nullable=False, index=True)
    type = Column(Enum(VerificationType), nullable=False)
    code = Column(String(10), nullable=False)
    status = Column(Enum(VerificationStatus), default=VerificationStatus.PENDING)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    confirmed_at = Column(DateTime, nullable=True)
    attempts_count = Column(Integer, default=0)
    max_attempts = Column(Integer, default=5)