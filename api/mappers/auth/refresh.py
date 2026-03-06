from application.dtos.auth import (
    RefreshRequestDTO,
    RefreshResponseDTO,
)
from api.schemas.auth import (
    RefreshResponseSchema,
)


class RefreshSchemaMapper:
    def to_dto(self, refresh_token: str) -> RefreshRequestDTO:
        return RefreshRequestDTO(
            refresh_token=refresh_token,
        )
    

    def to_schema(self, dto: RefreshResponseDTO) -> RefreshResponseSchema:
        return RefreshResponseSchema(
            access_token=dto.access_token,
            refresh_token=dto.refresh_token,
            token_type=dto.token_type,
            expires_in=dto.expires_in,
        )