from application.dtos.auth import (
    LoginRequestDTO, 
    LoginResponseDTO,
)
from api.schemas.auth.login import (
    LoginRequestSchema, 
    LoginResponseSchema, 
    UserLoginResponseSchema,
)


class LoginSchemaMapper:
    def to_dto(self, request: LoginRequestSchema, ip_address: str, user_agent: str) -> LoginRequestDTO:
        return LoginRequestDTO(
            email=request.email,
            password=request.password,
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    def to_schema(self, response: LoginResponseDTO) -> LoginResponseSchema:
        return LoginResponseSchema(
            access_token=response.access_token,
            refresh_token=response.refresh_token,
            expires_in=response.expires_in,
            user=UserLoginResponseSchema(
                id=response.user_id,
                first_name=response.first_name,
                last_name=response.last_name,
                email=response.email,
                role=response.role,
            )
        )