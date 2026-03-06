from enum import Enum

from domain.entities.verification_code import (
    VerificationCodeEntity,
    VerificationType,
    VerificationStatus,
)
from infrastructure.database.models.verification_code import VerificationCodeModel


class VerificationCodeMapper:
    """Mapper between VerificationCodeEntity and VerificationCodeModel"""
    
    @staticmethod
    def to_entity(model: VerificationCodeModel) -> VerificationCodeEntity:
        """Convert database model to domain entity."""
        return VerificationCodeEntity(
            id=model.id,
            identifier=model.identifier,
            type=VerificationType(model.type.value) if isinstance(model.type, Enum) else VerificationType(model.type),
            code=model.code,
            status=VerificationStatus(model.status.value) if isinstance(model.status, Enum) else VerificationStatus(model.status),
            created_at=model.created_at,
            expires_at=model.expires_at,
            confirmed_at=model.confirmed_at,
            attempts_count=model.attempts_count,
            max_attempts=model.max_attempts,
        )
    
    @staticmethod
    def to_model(entity: VerificationCodeEntity) -> VerificationCodeModel:
        """Convert domain entity to database model."""
        return VerificationCodeModel(
            id=entity.id,
            identifier=entity.identifier,
            type=entity.type.value,
            code=entity.code,
            status=entity.status.value,
            created_at=entity.created_at,
            expires_at=entity.expires_at,
            confirmed_at=entity.confirmed_at,
            attempts_count=entity.attempts_count,
            max_attempts=entity.max_attempts,
        )
    
    @staticmethod
    def update_model_from_entity(model: VerificationCodeModel, entity: VerificationCodeEntity) -> VerificationCodeModel:
        """Update existing database model with entity data."""
        model.identifier = entity.identifier
        model.type = entity.type.value
        model.code = entity.code
        model.status = entity.status.value
        model.expires_at = entity.expires_at
        model.confirmed_at = entity.confirmed_at
        model.attempts_count = entity.attempts_count
        model.max_attempts = entity.max_attempts
            
        return model