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
            # Получение пользователя по ID или идентификатору
            if dto.current_user_id:
                user = await self.uow.users.get_by_id(dto.current_user_id)
            elif dto.email:
                user = await self.uow.users.get_by_email(dto.email)
            elif dto.phone:
                user = await self.uow.users.get_by_phone(dto.phone)
            else:
                user = None
            
            if not user:
                error_msg = f"User with {dto.email or dto.phone} not found"
                raise UserNotFoundError(error_msg)
            
            # Получение последнего ожидающего кода верификации
            verification_code = await self.uow.verification.get_last_pending(
                identifier=dto.email or dto.phone,
                verification_type=VerificationType.EMAIL if dto.email else VerificationType.PHONE
            )
            
            if not verification_code:
                raise VerificationCodeInvalidError(
                    "No pending verification code found. Please request a new code."
                )
            
            # Сохраняем текущее количество попыток для проверки
            attempts_before = verification_code.attempts_count
            
            # Проверяем код (метод verify сам должен увеличить счетчик попыток)
            try:
                verification_code.verify(dto.code)
            except Exception as e:
                # Если метод verify уже увеличил счетчик, сохраняем изменения
                if verification_code.attempts_count == attempts_before:
                    # Если метод verify не увеличил счетчик, увеличиваем его здесь
                    verification_code.increment_attempts_count()
                
                await self.uow.verification.save(verification_code)
                await self.uow.commit()
                raise e
            
            # Если код верный, проверяем что счетчик попыток увеличился
            if verification_code.attempts_count == attempts_before:
                # Если метод verify не увеличил счетчик при успехе, увеличиваем здесь
                verification_code.increment_attempts_count()
            
            verification_type = VerificationType.EMAIL if dto.email else VerificationType.PHONE
            
            if verification_type == VerificationType.EMAIL:
                user.verify_email()
            else:
                user.verify_phone()
            
            # Сохранение всех изменений
            await self.uow.users.save(user)
            await self.uow.verification.save(verification_code)
            await self.uow.commit()

            if verification_type == VerificationType.EMAIL:
                return VerifyResponseDTO(
                    email=user.email.value if user.email else None,
                )
            else:
                return VerifyResponseDTO(
                    phone=user.phone.value if user.phone else None,
                )