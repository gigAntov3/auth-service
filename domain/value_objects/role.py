from enum import Enum
from dataclasses import dataclass
from typing import Set

class RoleType(Enum):
    OWNER = "owner"
    ADMIN = "admin"
    MANAGER = "manager"
    STAFF = "staff"
    CLIENT = "client"

@dataclass(frozen=True)
class Role:
    """Value Object для роли с правами"""
    type: RoleType
    
    def get_permissions(self) -> Set[str]:
        """Права доступа определяются здесь, а не в БД"""
        permissions_map = {
            RoleType.OWNER: {
                "company.manage",
                "company.delete",
                "membership.manage",
                "schedule.full_access",
                "finance.full_access",
                "reports.full_access",
                "staff.manage",
                "clients.manage",
                "services.manage"
            },
            RoleType.ADMIN: {
                "schedule.full_access",
                "finance.view",
                "reports.view",
                "staff.manage",
                "clients.manage",
                "services.manage",
                "membership.invite"
            },
            RoleType.MANAGER: {
                "schedule.manage",
                "clients.view",
                "services.view",
                "staff.view"
            },
            RoleType.STAFF: {
                "schedule.view",
                "schedule.edit_own",
                "clients.view"
            },
            RoleType.CLIENT: {
                "schedule.view",
                "schedule.book",
                "schedule.cancel_own",
                "profile.view_own"
            }
        }
        return permissions_map.get(self.type, set())
    
    def has_permission(self, permission: str) -> bool:
        return permission in self.get_permissions()
    
    @classmethod
    def owner(cls) -> 'Role':
        return cls(RoleType.OWNER)
    
    @classmethod
    def admin(cls) -> 'Role':
        return cls(RoleType.ADMIN)
    
    @classmethod
    def manager(cls) -> 'Role':
        return cls(RoleType.MANAGER)
    
    @classmethod
    def staff(cls) -> 'Role':
        return cls(RoleType.STAFF)
    
    @classmethod
    def client(cls) -> 'Role':
        return cls(RoleType.CLIENT)