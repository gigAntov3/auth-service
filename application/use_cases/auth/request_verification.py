from dataclasses import dataclass

from domain.entities.verification_code import (
    VerificationCodeEntity,
    VerificationType,
)
from application.interfaces.unit_of_work import UnitOfWork
from application.interfaces.services.email_service import EmailService
from application.interfaces.services.sms_service import SmsService
from application.dtos.verification import (
    VerificationRequestDTO,
    VerificationRequestResponseDTO
)
from application.exceptions import ValidationError
from config import settings


@dataclass
class RequestVerificationUseCase:
    """Use case для запроса кода верификации"""
    
    uow: UnitOfWork
    email_service: EmailService
    sms_service: SmsService
    
    async def execute(self, dto: VerificationRequestDTO) -> VerificationRequestResponseDTO:
        async with self.uow:
            verification_code = VerificationCodeEntity.create(
                identifier=dto.identifier,
                type=dto.identifier_type,
            )
            
            saved_code = await self.uow.verification.save(verification_code)
            
            if dto.identifier_type == VerificationType.EMAIL:
                await self.email_service.send_verification_code(
                    to_email=dto.identifier,
                    code=saved_code.code
                )
            elif dto.identifier_type == VerificationType.PHONE:
                await self.sms_service.send_verification_code(
                    to_phone=dto.identifier,
                    code=saved_code.code
                )
            else:
                raise ValidationError(f"Invalid verification type: {dto.identifier_type}")
            
            await self.uow.commit()
            
            return VerificationRequestResponseDTO(
                verification_id=saved_code.id,
                identifier=saved_code.identifier,
                identifier_type=saved_code.type.value,
                expires_at=saved_code.expires_at,
            )