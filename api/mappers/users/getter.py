from application.dtos.users import (
    UserResponseDTO,
)
from api.schemas.users import (
    GetUserResponseSchema
)


class UserGetterSchemaMapper:

    def to_schema(self, user: UserResponseDTO) -> GetUserResponseSchema:
        return GetUserResponseSchema(
            id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            phone=user.phone,
            role=user.role,
            is_email_verified=user.is_email_verified,
            is_phone_verified=user.is_phone_verified,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )