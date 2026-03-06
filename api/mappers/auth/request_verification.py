from application.dtos.verification import (
    VerificationRequestDTO,
    VerificationRequestResponseDTO
)
from api.schemas.auth.verification import (
    VerificationRequestSchema,
    VerificationRequestResponseSchema
)


class VerificationRequestSchemaMapper:
    def to_dto(self, request: VerificationRequestSchema) -> VerificationRequestDTO:
        return VerificationRequestDTO(
            identifier=request.identifier,
            identifier_type=request.identifier_type
        )
    
    def to_schema(self, response: VerificationRequestResponseDTO) -> VerificationRequestResponseSchema:
        return VerificationRequestResponseSchema(
            verification_id=response.verification_id,
            identifier=response.identifier,
            identifier_type=response.identifier_type,
            expires_at=response.expires_at
        )