from dataclasses import dataclass

from domain.entities.verification_code import VerificationStatus
from application.interfaces.unit_of_work import UnitOfWork
from application.dtos.verification import VerifyCodeDTO, VerifyCodeResponseDTO
from application.exceptions import (
    VerificationCodeNotFoundError,
    VerificationCodeExpiredError,
    VerificationCodeAlreadyUsedError,
    VerificationCodeInvalidError,
    TooManyAttemptsError
)


@dataclass
class VerifyCodeUseCase:
    """Use case для подтверждения кода верификации"""
    
    uow: UnitOfWork
    
    async def execute(self, dto: VerifyCodeDTO) -> VerifyCodeResponseDTO:
        async with self.uow:
            # Получаем код из БД
            verification_code = await self.uow.verification.get_by_id(
                dto.verification_id
            )
            
            if not verification_code:
                raise VerificationCodeNotFoundError(
                    f"Verification code with id {dto.verification_id} not found"
                )
            
            # Проверяем статус
            if verification_code.status == VerificationStatus.EXPIRED:
                raise VerificationCodeExpiredError(
                    "Verification code has expired"
                )
            
            if verification_code.status == VerificationStatus.CONFIRMED:
                raise VerificationCodeAlreadyUsedError(
                    "Verification code has already been used"
                )
            
            # Проверяем количество попыток
            if verification_code.attempts_count >= verification_code.max_attempts:
                verification_code.status = VerificationStatus.EXPIRED
                await self.uow.verification_codes.save(verification_code)
                await self.uow.commit()
                raise TooManyAttemptsError(
                    "Too many failed attempts. Please request a new code."
                )
            
            # Проверяем код
            if verification_code.code != dto.code:
                verification_code.attempts_count += 1
                await self.uow.verification_codes.save(verification_code)
                await self.uow.commit()
                
                remaining_attempts = verification_code.max_attempts - verification_code.attempts_count
                raise VerificationCodeInvalidError(
                    f"Invalid verification code. {remaining_attempts} attempts remaining."
                )
            
            # Код верный - подтверждаем
            verification_code.status = VerificationStatus.CONFIRMED
            verification_code.confirmed_at = datetime.utcnow()
            
            await self.uow.verification_codes.save(verification_code)
            await self.uow.commit()
            
            return VerifyCodeResponseDTO(
                success=True,
                identifier=verification_code.identifier,
                type=verification_code.type.value,
                message="Verification successful"
            )