from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from application.interfaces.unit_of_work import UnitOfWork
from application.dtos.verification import (
    VerifyRequestDTO,
    VerifyResponseDTO,
)
from application.exceptions import (
    UserNotFoundError,
    VerificationCodeInvalidError,
    VerificationCodeExpiredError
)
from domain.entities.verification_code import VerificationCodeEntity, VerificationType
from domain.entities.user import UserEntity


@dataclass
class VerifyUseCase:
    """Use case для верификации email или телефона пользователя"""
    
    uow: UnitOfWork
    
    async def execute(self, dto: VerifyRequestDTO) -> VerifyResponseDTO:
        async with self.uow:
            user = await self._get_user(dto)
            verification_code = await self._get_verification_code(dto)
            
            await self._verify_code(verification_code, dto.code)
            await self._update_user_verification(user, dto.identifier, dto.identifier_type)
            
            await self._save_changes(user, verification_code)
            
            return self._create_response(user)
    
    async def _get_user(self, dto: VerifyRequestDTO) -> UserEntity:
        """Получение пользователя по ID или идентификатору"""
        if dto.user_id:
            user = await self.uow.users.get_by_id(dto.user_id)
        elif dto.identifier_type == VerificationType.EMAIL:
            user = await self.uow.users.get_by_email(dto.identifier)
        else:
            user = await self.uow.users.get_by_phone(dto.identifier)
        
        if not user:
            error_msg = f"User with {dto.identifier_type.value} {dto.identifier} not found"
            raise UserNotFoundError(error_msg)
        
        return user
    
    async def _get_verification_code(self, dto: VerifyRequestDTO) -> VerificationCodeEntity:
        """Получение последнего ожидающего кода верификации"""
        verification_code = await self.uow.verification.get_last_pending(
            identifier=dto.identifier,
            verification_type=dto.identifier_type
        )
        
        if not verification_code:
            raise VerificationCodeInvalidError(
                "No pending verification code found. Please request a new code."
            )
        
        return verification_code
    
    async def _verify_code(self, verification_code: VerificationCodeEntity, code: str) -> None:
        """Проверка кода верификации с сохранением состояния в случае ошибки"""
        try:
            verification_code.verify(code)
        except Exception as e:
            await self.uow.verification.save(verification_code)
            await self.uow.commit()
            raise e
    
    async def _update_user_verification(self, user: UserEntity, identifier: str, verification_type: VerificationType) -> None:
        """Обновление статуса верификации пользователя"""
        if verification_type == VerificationType.EMAIL:
            user.verify_email(identifier)
        else:
            user.verify_phone(identifier)
    
    async def _save_changes(self, user: UserEntity, verification_code: VerificationCodeEntity) -> None:
        """Сохранение всех изменений"""
        await self.uow.users.save(user)
        await self.uow.verification.save(verification_code)
        await self.uow.commit()
    
    def _create_response(self, user: UserEntity) -> VerifyResponseDTO:
        """Создание DTO ответа"""
        return VerifyResponseDTO(
            user_id=user.id,
            email=user.email.value if user.email else None,
            phone=user.phone.value if user.phone else None,
            first_name=user.first_name,
            last_name=user.last_name,
            is_email_verified=user.is_email_verified,
            is_phone_verified=user.is_phone_verified,
            is_active=user.is_active,
            role=user.role.type.value,
            created_at=user.created_at,
            updated_at=user.updated_at
        )