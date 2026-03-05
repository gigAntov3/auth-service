from application.dtos.auth import (
    LogoutRequestDTO,
)
from api.schemas.auth.logout import (
    LogoutRequestSchema
)


class LogoutSchemaMapper:
    def to_dto(self, request: LogoutRequestSchema, ip_address: str, user_agent: str) -> LogoutRequestDTO:
        return LogoutRequestDTO(
            refresh_token=request.refresh_token,
            ip_address=ip_address,
            user_agent=user_agent
        )