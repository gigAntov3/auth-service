from domain.entities.refresh_token import RefreshTokenEntity

from infrastructure.database.models.refresh_token import RefreshTokenModel


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