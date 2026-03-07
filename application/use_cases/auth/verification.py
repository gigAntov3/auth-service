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
    VerificationResponseDTO
)
from application.exceptions import ValidationError
from config import settings


@dataclass
class VerificationUseCase:
    """Use case для запроса кода верификации"""
    
    uow: UnitOfWork
    email_service: EmailService
    sms_service: SmsService
    
    async def execute(self, dto: VerificationRequestDTO) -> VerificationResponseDTO:
        async with self.uow:

            if dto.email:
                user = await self.uow.users.get_by_email(dto.email)
                if user.is_email_verified:
                    raise ValidationError("Email already verified")
                
                verification_code = VerificationCodeEntity.create(
                    user_id=dto.current_user_id,
                    identifier=dto.email,
                    type=VerificationType.EMAIL,
                )
            elif dto.phone:
                user = await self.uow.users.get_by_phone(dto.phone)
                if user.is_phone_verified:
                    raise ValidationError("Phone already verified")
                
                verification_code = VerificationCodeEntity.create(
                    user_id=dto.current_user_id,
                    identifier=dto.phone,
                    type=VerificationType.PHONE,
                )
            
            saved_code = await self.uow.verification.save(verification_code)
    
            if saved_code.type == VerificationType.EMAIL:
                await self.email_service.send_verification_code(
                    to_email=saved_code.identifier,
                    code=saved_code.code
                )
            elif saved_code.type == VerificationType.PHONE:
                await self.sms_service.send_verification_code(
                    to_phone=saved_code.identifier,
                    code=saved_code.code
                )
            
            await self.uow.commit()
            
            return VerificationResponseDTO(
                expires_at=saved_code.expires_at,
                email=saved_code.identifier if saved_code.type == VerificationType.EMAIL else None,
                phone=saved_code.identifier if saved_code.type == VerificationType.PHONE else None
            )