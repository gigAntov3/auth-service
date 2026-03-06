from uuid import UUID

from application.dtos.verification import (
    VerificationRequestDTO,
    VerificationRequestResponseDTO,
)
from api.schemas.verification import (
    VerificationRequestSchema,
    VerificationResponseSchema,
)


class VerificationSchemaMapper:
    def to_dto(self, schema: VerificationRequestSchema) -> VerificationRequestDTO:
        return VerificationRequestDTO(
            email=schema.email,
            phone=schema.phone
        )
    

    def to_schema(self, dto: VerificationRequestResponseDTO) -> VerificationResponseSchema:
        return VerificationResponseSchema(
            success=True,
            email=dto.email,
            phone=dto.phone,
            expires_at=dto.expires_at,
            message="Verification code sent successfully"
        )