from sqlalchemy import Column, String, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime, timezone

from infrastructure.database.base import Base


class RoleModel(Base):
    """Модель роли в БД"""
    __tablename__ = 'roles'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    role_type = Column(String(50), nullable=False)
    branch_id = Column(UUID(as_uuid=True), ForeignKey('branches.id', ondelete='CASCADE'), nullable=True)
    assigned_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    assigned_by = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    
    # Relationships - ИСПРАВЛЕНО
    user = relationship("UserModel", foreign_keys=[user_id], back_populates="roles")
    assigner = relationship("UserModel", foreign_keys=[assigned_by], back_populates="assigned_roles")
    branch = relationship("BranchModel", foreign_keys=[branch_id], back_populates="roles")