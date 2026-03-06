from uuid import UUID
from application.dtos.users import UserResponseDTO, UserUpdateDTO
from api.schemas.users import UserSchema, UserUpdateSchema

class UserUpdateSchemaMapper:
    
    def to_dto(self, schema: UserUpdateSchema, current_user_id: UUID) -> UserUpdateDTO:
        update_data = schema.model_dump(exclude_unset=True)

        print(update_data)

        return UserUpdateDTO(
            user_id=current_user_id,
            **update_data
        )
    
    def to_schema(self, dto: UserResponseDTO) -> UserSchema:
        return UserSchema(
            id=dto.user_id,
            first_name=dto.first_name,
            last_name=dto.last_name,
            email=dto.email,
            phone=dto.phone,
            birthday=dto.birthday,
            gender=dto.gender,
            role=dto.role,
            is_email_verified=dto.is_email_verified,
            is_phone_verified=dto.is_phone_verified,
            is_active=dto.is_active,
            created_at=dto.created_at,
            updated_at=dto.updated_at,
        )