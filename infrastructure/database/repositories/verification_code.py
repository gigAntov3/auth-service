from datetime import datetime
from uuid import UUID

from sqlalchemy import select, desc, and_
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities.verification_code import VerificationCodeEntity, VerificationStatus, VerificationType
from application.interfaces.repositories.verification_code import VerificationCodeRepository
from infrastructure.database.models.verification_code import VerificationCodeModel
from infrastructure.database.mappers.verification_code import VerificationCodeMapper


class SqlAlchemyVerificationCodeRepository(VerificationCodeRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
        self.mapper = VerificationCodeMapper()
    
    async def save(self, verification_code: VerificationCodeEntity) -> VerificationCodeEntity:
        """
        Сохраняет или обновляет сущность кода верификации.
        
        Args:
            verification_code: Сущность кода верификации для сохранения
            
        Returns:
            VerificationCodeEntity: Сохраненная сущность
        """
        existing_model = await self.session.get(
            VerificationCodeModel, 
            verification_code.id
        )
        
        if existing_model:
            model = self.mapper.update_model_from_entity(existing_model, verification_code)
        else:
            model = self.mapper.to_model(verification_code)
            
            self.session.add(model)
        
        await self.session.flush()

        return self.mapper.to_entity(model)
        
    
    async def get_by_id(self, code_id: UUID) -> VerificationCodeEntity | None:
        model = await self.session.get(VerificationCodeModel, code_id)
        return self.mapper.to_entity(model)
    
    async def get_last_pending(
        self, 
        identifier: str, 
        verification_type: VerificationType
    ) -> VerificationCodeEntity | None:
        result = await self.session.execute(
            select(VerificationCodeModel)
            .where(
                and_(
                    VerificationCodeModel.identifier == identifier,
                    VerificationCodeModel.type == verification_type,
                    VerificationCodeModel.status == VerificationStatus.PENDING,
                    VerificationCodeModel.expires_at > datetime.utcnow()
                )
            )
            .order_by(desc(VerificationCodeModel.created_at))
            .limit(1)
        )
        model = result.scalar_one_or_none()
        return self.mapper.to_entity(model) if model else None
    
    async def get_by_identifier_and_type(
        self, 
        identifier: str, 
        verification_type: VerificationType,
        exclude_expired: bool = True
    ) -> list[VerificationCodeEntity]:
        result = await self.session.execute(
            select(VerificationCodeModel)
            .where(
                and_(
                    VerificationCodeModel.identifier == identifier,
                    VerificationCodeModel.type == verification_type,
                    VerificationCodeModel.status != VerificationStatus.EXPIRED if exclude_expired else None,
                )
            )
            .order_by(desc(VerificationCodeModel.created_at))
        )
        models = result.scalars().all()
        return [self.mapper.to_entity(model) for model in models]
    
    async def delete_expired(self) -> int:
        result = await self.session.execute(
            select(VerificationCodeModel)
            .where(VerificationCodeModel.expires_at < datetime.utcnow())
            .delete()
        )
        return result.rowcount