from domain.entities.user import UserEntity
from domain.value_objects.email import Email

from domain.value_objects.phone import Phone
from domain.value_objects.password import PasswordHash

from domain.value_objects.user_type import UserType, UserTypeEnum

from infrastructure.database.models.user import UserModel


class UserMapper:
    """Mapper between User entity and UserModel"""
    
    @staticmethod
    def to_entity(model: UserModel) -> UserEntity:
        return UserEntity(
            id=model.id,
            email=Email(model.email),
            phone=Phone(model.phone) if model.phone else None,
            password_hash=PasswordHash(model.password_hash),
            first_name=model.first_name,
            last_name=model.last_name,
            role=UserType(UserTypeEnum(model.role)),
            is_email_verified=model.is_email_verified,
            is_phone_verified=model.is_phone_verified,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at
        )
    
    @staticmethod
    def to_model(entity: UserEntity) -> UserModel:
        return UserModel(
            id=entity.id,
            email=entity.email.value,
            phone=entity.phone.value if entity.phone else None,
            password_hash=entity.password_hash.value,
            first_name=entity.first_name,
            last_name=entity.last_name,
            role=entity.role.type.value,
            is_email_verified=entity.is_email_verified,
            is_phone_verified=entity.is_phone_verified,
            is_active=entity.is_active,
            created_at=entity.created_at,
            updated_at=entity.updated_at
        )
    
    @staticmethod
    def update_model(entity: UserEntity, model: UserModel) -> UserModel:
        model.email = entity.email.value
        model.phone = entity.phone
        model.password_hash = entity.password_hash.value
        model.first_name = entity.first_name
        model.last_name = entity.last_name
        model.role = entity.role.type.value
        model.is_email_verified = entity.is_email_verified
        model.is_phone_verified = entity.is_phone_verified
        model.is_active = entity.is_active
        model.updated_at = entity.updated_at
        
        return model
