from application.dtos.auth import (
    LoginRequestDTO, 
    LoginResponseDTO,
    DeviceInfoDTO,
)
from api.schemas.auth import (
    LoginRequestSchema, 
    LoginResponseSchema,
)
from api.schemas.users import UserPublicSchema


class LoginSchemaMapper:
    def to_dto(self, schema: LoginRequestSchema, device_info: DeviceInfoDTO) -> LoginRequestDTO:
        return LoginRequestDTO(
            email=schema.email,
            password=schema.password,
            ip_address=device_info.ip_address,
            user_agent=device_info.user_agent,
            device_name=device_info.device_name,
            device_type=device_info.device_type
        )
    
    def to_schema(self, dto: LoginResponseDTO) -> LoginResponseSchema:
        return LoginResponseSchema(
            access_token=dto.access_token,
            refresh_token=dto.refresh_token,
            token_type=dto.token_type,
            expires_in=dto.expires_in,
        )