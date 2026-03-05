from typing import Optional
from datetime import datetime
from uuid import UUID

from domain.entities.user import UserEntity
from domain.value_objects.email import Email
from domain.value_objects.password import PasswordHash

from domain.entities.refresh_token import RefreshTokenEntity
from domain.value_objects.user_type import UserType, UserTypeEnum

from infrastructure.database.models.user import UserModel
from infrastructure.database.models.refresh_token import RefreshTokenModel


class UserMapper:
    """Mapper between User entity and UserModel"""
    
    @staticmethod
    def to_entity(model: UserModel) -> UserEntity:
        """Convert ORM model to domain entity"""
        if not model:
            return None
            
        return UserEntity(
            id=model.id,
            email=Email(model.email),
            phone=model.phone,
            password_hash=PasswordHash(model.password_hash),
            first_name=model.first_name,
            last_name=model.last_name,
            role=UserType(UserTypeEnum(model.role)),
            is_email_verified=model.is_email_verified,
            is_phone_verified=model.is_phone_verified,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at
        )
    
    @staticmethod
    def to_model(entity: UserEntity) -> UserModel:
        """Convert domain entity to ORM model"""
        if not entity:
            return None
            
        return UserModel(
            id=entity.id,
            email=entity.email.value,
            phone=entity.phone,
            password_hash=entity.password_hash.value,
            first_name=entity.first_name,
            last_name=entity.last_name,
            role=entity.role.type.value,
            is_email_verified=entity.is_email_verified,
            is_phone_verified=entity.is_phone_verified,
            is_active=entity.is_active,
            created_at=entity.created_at,
            updated_at=entity.updated_at
        )
    
    @staticmethod
    def update_model(entity: UserEntity, model: UserModel) -> UserModel:
        """Update existing ORM model with entity data"""
        if not entity or not model:
            return model
            
        model.email = entity.email
        model.phone = entity.phone
        model.password_hash = entity.password_hash
        model.first_name = entity.first_name
        model.last_name = entity.last_name
        model.is_email_verified = entity.is_email_verified
        model.is_phone_verified = entity.is_phone_verified
        model.is_active = entity.is_active
        model.updated_at = entity.updated_at
        
        return model


class RefreshTokenMapper:
    """Mapper between RefreshToken entity and RefreshTokenModel"""
    
    @staticmethod
    def to_entity(model: RefreshTokenModel) -> RefreshTokenEntity:
        """Convert ORM model to domain entity"""
        if not model:
            return None
            
        token = RefreshTokenEntity(
            id=model.id,
            user_id=model.user_id,
            token_hash=model.token_hash,
            expires_at=model.expires_at,
            created_at=model.created_at,
            revoked_at=model.revoked_at,
            ip_address=model.ip_address,
            user_agent=model.user_agent
        )
        
        # Восстанавливаем состояние (не через __init__, а через атрибуты)
        # Так как у нас нет сеттеров, используем прямой доступ к атрибутам
        object.__setattr__(token, 'id', model.id)
        object.__setattr__(token, 'user_id', model.user_id)
        object.__setattr__(token, 'token_hash', model.token_hash)
        object.__setattr__(token, 'expires_at', model.expires_at)
        object.__setattr__(token, 'created_at', model.created_at)
        object.__setattr__(token, 'revoked_at', model.revoked_at)
        object.__setattr__(token, 'ip_address', model.ip_address)
        object.__setattr__(token, 'user_agent', model.user_agent)
        
        return token
    
    @staticmethod
    def to_model(entity: RefreshTokenEntity) -> RefreshTokenModel:
        """Convert domain entity to ORM model"""
        if not entity:
            return None
            
        return RefreshTokenModel(
            id=entity.id,
            user_id=entity.user_id,
            token_hash=entity.token_hash.value,
            expires_at=entity.expires_at,
            created_at=entity.created_at,
            revoked_at=entity.revoked_at,
            ip_address=entity.ip_address,
            user_agent=entity.user_agent
        )
    
    @staticmethod
    def update_model(entity: RefreshTokenEntity, model: RefreshTokenModel) -> RefreshTokenModel:
        """Update existing ORM model with entity data"""
        if not entity or not model:
            return model
            
        model.revoked_at = entity.revoked_at
        model.expires_at = entity.expires_at
        
        return model