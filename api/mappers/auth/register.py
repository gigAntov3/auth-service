from api.schemas.auth import (
    RegisterRequestSchema,
    RegisterResponseSchema,
)
from api.schemas.users import UserPublicSchema
from application.dtos.auth import (
    RegisterRequestDTO,
    RegisterResponseDTO,
    DeviceInfoDTO,
)


class RegisterSchemaMapper:
    
    def to_dto(self, schema: RegisterRequestSchema, device_info: DeviceInfoDTO) -> RegisterRequestDTO:
        return RegisterRequestDTO(
            first_name=schema.first_name,
            last_name=schema.last_name,
            email=schema.email,
            password=schema.password,
            ip_address=device_info.ip_address,
            user_agent=device_info.user_agent,
            device_name=device_info.device_name,
            device_type=device_info.device_type
        )
    
    
    def to_schema(self, dto: RegisterResponseDTO) -> RegisterResponseSchema:
        return RegisterResponseSchema(
            access_token=dto.access_token,
            refresh_token=dto.refresh_token,
            token_type=dto.token_type,
            expires_in=dto.expires_in,
        )