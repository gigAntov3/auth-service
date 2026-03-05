from enum import Enum
from dataclasses import dataclass

class UserTypeEnum(Enum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    MODERATOR = "moderator"
    USER = "user"
    GUEST = "guest"

@dataclass(frozen=True)
class UserType:
    """Value Object для типа пользователя"""
    type: UserTypeEnum

    def can_manage_roles(self) -> bool:
        """Пример бизнес-логики: кто может управлять ролями"""
        return self.type in {UserTypeEnum.SUPER_ADMIN, UserTypeEnum.ADMIN}

    def can_edit_content(self) -> bool:
        """Кто может редактировать контент"""
        return self.type in {UserTypeEnum.SUPER_ADMIN, UserTypeEnum.ADMIN, UserTypeEnum.MODERATOR}

    def can_view_content(self) -> bool:
        """Кто может просматривать контент"""
        return self.type in {UserTypeEnum.SUPER_ADMIN, UserTypeEnum.ADMIN, UserTypeEnum.MODERATOR, UserTypeEnum.USER}

    @classmethod
    def super_admin(cls) -> 'UserType':
        return cls(UserTypeEnum.SUPER_ADMIN)
    
    @classmethod
    def admin(cls) -> 'UserType':
        return cls(UserTypeEnum.ADMIN)
    
    @classmethod
    def moderator(cls) -> 'UserType':
        return cls(UserTypeEnum.MODERATOR)
    
    @classmethod
    def user(cls) -> 'UserType':
        return cls(UserTypeEnum.USER)
    
    @classmethod
    def guest(cls) -> 'UserType':
        return cls(UserTypeEnum.GUEST)