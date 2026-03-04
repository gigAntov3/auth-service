from sqlalchemy import Column, String, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from infrastructure.database.base import Base, TimestampMixin


class BranchModel(Base, TimestampMixin):
    """Модель филиала в БД"""
    __tablename__ = 'branches'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    code = Column(String(50), unique=True, nullable=False)
    address = Column(String(500), nullable=True)
    phone = Column(String(50), nullable=True)
    email = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Relationships - ИСПРАВЛЕНО
    users = relationship("UserModel", foreign_keys="[UserModel.home_branch_id]", back_populates="home_branch")
    roles = relationship("RoleModel", foreign_keys="[RoleModel.branch_id]", back_populates="branch")