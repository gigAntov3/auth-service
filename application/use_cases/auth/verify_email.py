from dataclasses import dataclass
from uuid import UUID

from application.interfaces.unit_of_work import UnitOfWork
from application.dtos.verification import VerifyEmailDTO
from application.dtos.auth import UserResponseDTO
from application.exceptions import (
    UserNotFoundError,
    VerificationCodeInvalidError,
    VerificationCodeExpiredError
)


@dataclass
class VerifyEmailUseCase:
    """Use case для верификации email пользователя"""
    
    uow: UnitOfWork
    
    async def execute(self, dto: VerifyEmailDTO) -> UserResponseDTO:
        async with self.uow:
            # Находим пользователя
            if dto.user_id:
                user = await self.uow.users.get_by_id(dto.user_id)
            else:
                user = await self.uow.users.get_by_email(dto.email)
            
            if not user:
                raise UserNotFoundError(f"User with email {dto.email} not found")
            
            # Находим последний pending код для этого email
            verification_code = await self.uow.verification_codes.get_last_pending(
                identifier=dto.email,
                type=VerificationType.EMAIL
            )
            
            if not verification_code:
                raise VerificationCodeInvalidError(
                    "No pending verification code found. Please request a new code."
                )
            
            # Проверяем код (используем доменную логику)
            try:
                verification_code.verify(dto.code)
            except Exception as e:
                await self.uow.verification_codes.save(verification_code)
                await self.uow.commit()
                raise e
            
            # Обновляем статус верификации email у пользователя
            user.verify_email()
            
            # Сохраняем изменения
            await self.uow.users.save(user)
            await self.uow.verification_codes.save(verification_code)
            await self.uow.commit()
            
            return UserResponseDTO(
                id=user.id,
                email=user.email.value,
                first_name=user.first_name,
                last_name=user.last_name,
                is_email_verified=user.is_email_verified,
                role=user.role.type.value,
                created_at=user.created_at
            )