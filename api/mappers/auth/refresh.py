from application.dtos.auth import (
    RefreshRequestDTO,
    RefreshResponseDTO,
)
from api.schemas.auth.refresh import (
    RefreshRequestSchema,
    RefreshResponseSchema,
)


class RefreshSchemaMapper:
    def to_dto(self, request: RefreshRequestSchema, ip_address: str, user_agent: str) -> RefreshRequestDTO:
        return RefreshRequestDTO(
            refresh_token=request.refresh_token,
            ip_address=ip_address,
            user_agent=user_agent
        )
    

    def to_schema(self, response: RefreshResponseDTO) -> RefreshResponseSchema:
        return RefreshResponseSchema(
            access_token=response.access_token,
            refresh_token=response.refresh_token,
            expires_in=response.expires_in,
        )