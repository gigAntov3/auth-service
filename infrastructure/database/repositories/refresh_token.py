from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, delete, update
from datetime import datetime

from domain.entities.refresh_token import RefreshTokenEntity
from infrastructure.database.models.refresh_token import RefreshTokenModel
from infrastructure.database.mappers.refresh_token import RefreshTokenMapper

class SQLAlchemyRefreshTokenRepository:
    """Репозиторий для refresh токенов"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.mapper = RefreshTokenMapper()
    
    async def save(self, token: RefreshTokenEntity) -> None:
        """Сохранить токен"""
        existing = await self.get_by_id(token.id)
        
        if existing:
            model = await self.session.get(RefreshTokenModel, token.id)
            if model:
                model.token_hash = token.token_hash.value
                model.revoked_at = token.revoked_at
                model.expires_at = token.expires_at
        else:
            model = self.mapper.to_model(token)
            self.session.add(model)
        
        await self.session.flush()
    
    async def get_by_id(self, token_id: UUID) -> Optional[RefreshTokenEntity]:
        """Получить токен по ID"""
        model = await self.session.get(RefreshTokenModel, token_id)
        return self.mapper.to_entity(model) if model else None
    
    async def get_by_hash(self, token_hash: str) -> Optional[RefreshTokenEntity]:
        """Получить токен по хешу"""
        result = await self.session.execute(
            select(RefreshTokenModel)
            .where(RefreshTokenModel.token_hash == token_hash)
        )
        model = result.scalar_one_or_none()
        return self.mapper.to_entity(model) if model else None
    
    async def get_active_by_user(self, user_id: UUID) -> List[RefreshTokenEntity]:
        """Получить активные токены пользователя"""
        result = await self.session.execute(
            select(RefreshTokenModel)
            .where(
                and_(
                    RefreshTokenModel.user_id == user_id,
                    RefreshTokenModel.revoked_at.is_(None),
                    RefreshTokenModel.expires_at > datetime.utcnow()
                )
            )
        )
        models = result.scalars().all()
        return [self.mapper.to_entity(m) for m in models]
    
    async def revoke_all_user_tokens(self, user_id: UUID) -> None:
        """Отозвать все токены пользователя"""
        await self.session.execute(
            update(RefreshTokenModel)
            .where(
                and_(
                    RefreshTokenModel.user_id == user_id,
                    RefreshTokenModel.revoked_at.is_(None)
                )
            )
            .values(revoked_at=datetime.utcnow())
        )
    
    async def cleanup_expired(self) -> int:
        """Удалить истекшие токены"""
        result = await self.session.execute(
            delete(RefreshTokenModel)
            .where(RefreshTokenModel.expires_at < datetime.utcnow())
        )
        return result.rowcount