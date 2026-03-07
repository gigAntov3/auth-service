from uuid import UUID

from application.dtos.verification import (
    VerificationRequestDTO,
    VerificationResponseDTO,
)
from api.schemas.verification import (
    VerificationRequestSchema,
    VerificationResponseSchema,
)


class VerificationSchemaMapper:
    def to_dto(self, schema: VerificationRequestSchema, current_user_id: UUID) -> VerificationRequestDTO:
        return VerificationRequestDTO(
            current_user_id=current_user_id,
            email=schema.email,
            phone=schema.phone
        )
    

    def to_schema(self, dto: VerificationResponseDTO) -> VerificationResponseSchema:
        return VerificationResponseSchema(
            success=True,
            email=dto.email,
            phone=dto.phone,
            expires_at=dto.expires_at,
            message="Verification code sent successfully"
        )