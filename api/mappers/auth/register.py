from api.schemas.auth.register import (
    RegisterRequestSchema,
    UserRegisterResponseSchema,
    RegisterResponseSchema,
)

from application.dtos.auth import (
    RegisterRequestDTO,
    RegisterResponseDTO,
)


class RegisterSchemaMapper:
    
    def to_dto(self, request: RegisterRequestSchema, ip_address: str, user_agent: str) -> RegisterRequestDTO:
        return RegisterRequestDTO(
            first_name=request.first_name,
            last_name=request.last_name,
            email=request.email,
            password=request.password,
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    def to_schema(self, response: RegisterResponseDTO) -> RegisterResponseSchema:
        return RegisterResponseSchema(
            access_token=response.access_token,
            refresh_token=response.refresh_token,
            expires_in=response.expires_in,
            user=UserRegisterResponseSchema(
                id=response.user_id,
                first_name=response.first_name,
                last_name=response.last_name,
                email=response.email,
                role=response.role,
            )
        )