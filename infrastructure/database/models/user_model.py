from sqlalchemy import Column, String, Boolean, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

import uuid
from typing import List

from infrastructure.database.base import Base, TimestampMixin


class UserModel(Base, TimestampMixin):
    """Модель пользователя в БД"""
    __tablename__ = 'users'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_email_verified = Column(Boolean, default=False)
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    home_branch_id = Column(UUID(as_uuid=True), ForeignKey('branches.id'), nullable=True)
    
    # Relationships - ИСПРАВЛЕНО: явно указываем foreign_keys
    roles = relationship(
        "RoleModel", 
        foreign_keys="[RoleModel.user_id]",
        back_populates="user", 
        cascade="all, delete-orphan"
    )
    assigned_roles = relationship(
        "RoleModel",
        foreign_keys="[RoleModel.assigned_by]",
        back_populates="assigner"
    )
    home_branch = relationship("BranchModel", foreign_keys=[home_branch_id])