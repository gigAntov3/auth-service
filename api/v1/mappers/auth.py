from dataclasses import dataclass
from typing import final

from application.dtos.auth_dto import RegisterResponseDTO
from api.v1.schemas.auth import (
    RegisterResponseSchema
)


@final
@dataclass(frozen=True, slots=True)
class RegisterSchemaMapper:
    """Mapper for converting Application DTOs to Presentation Response models.

    This mapper isolates the Presentation layer from direct dependencies on Application DTOs,
    following Clean Architecture principles.
    """

    def to_response(self, dto: RegisterResponseDTO) -> RegisterResponseSchema:
        """Convert Application DTO to API Response model."""
        return RegisterResponseSchema(
            user_id=dto.user_id,
            email=dto.email,
            full_name=dto.full_name,
            message=dto.message,
            requires_verification=dto.requires_verification
        )