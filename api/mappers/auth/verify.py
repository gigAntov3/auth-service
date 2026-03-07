from uuid import UUID

from application.dtos.verification import (
    VerifyRequestDTO,
    VerifyResponseDTO
)
from api.schemas.verification import (
    VerifyRequestSchema,
    VerifyResponseSchema,
)


class VerifySchemaMapper:
    def to_dto(self, schema: VerifyRequestSchema, current_user_id: UUID) -> VerifyRequestDTO:
        return VerifyRequestDTO(
            current_user_id=current_user_id,
            email=schema.email,
            phone=schema.phone,
            code=schema.code
        )
    
    def to_schema(self, dto: VerifyResponseDTO) -> VerifyResponseSchema:
        return VerifyResponseSchema(
            success=True,
            email=dto.email,
            phone=dto.phone,
            message="Email or phone verified successfully"
        )