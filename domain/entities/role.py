from dataclasses import dataclass
from enum import Enum
from typing import Optional, Set
from uuid import UUID, uuid4
from datetime import datetime, timezone


class RoleType(Enum):
    """
    Типы ролей в системе.
    
    Иерархия:
    - SUPER_ADMIN: полный доступ ко всему
    - ADMIN: администратор системы
    - OWNER: владелец филиала/бизнеса
    - DIRECTOR: директор филиала
    - MANAGER: менеджер
    - ACCOUNTANT: бухгалтер
    - CALL_CENTER: оператор кол-центра
    - USER: обычный пользователь
    """
    # Системные роли (глобальные)
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    
    # Бизнес-роли (привязаны к филиалам)
    OWNER = "owner"
    DIRECTOR = "director"
    MANAGER = "manager"
    ACCOUNTANT = "accountant"
    CALL_CENTER = "call_center"
    
    # Пользовательские роли
    USER = "user"

    @classmethod
    def get_system_roles(cls) -> Set['RoleType']:
        """Возвращает системные роли (глобальные)"""
        return {cls.SUPER_ADMIN, cls.ADMIN}

    @classmethod
    def get_business_roles(cls) -> Set['RoleType']:
        """Возвращает бизнес-роли (привязанные к филиалам)"""
        return {
            cls.OWNER, cls.DIRECTOR, cls.MANAGER,
            cls.ACCOUNTANT, cls.CALL_CENTER
        }

    def is_system_role(self) -> bool:
        """Проверяет, является ли роль системной"""
        return self in self.get_system_roles()

    def is_business_role(self) -> bool:
        """Проверяет, является ли роль бизнес-ролью"""
        return self in self.get_business_roles()


@dataclass
class Role:
    """
    Сущность Роли пользователя.
    
    Роль может быть:
    - Глобальной (branch_id = None) - для системных ролей
    - Привязанной к филиалу - для бизнес-ролей
    """
    id: UUID
    user_id: UUID
    role_type: RoleType
    assigned_at: datetime
    assigned_by: Optional[UUID]  # ID пользователя, который назначил роль
    branch_id: Optional[UUID] = None  # None для глобальных ролей

    @classmethod
    def create(
        cls,
        user_id: UUID,
        role_type: RoleType,
        assigned_by: Optional[UUID] = None,
        branch_id: Optional[UUID] = None
    ) -> 'Role':
        """Фабричный метод для создания новой роли"""
        # Валидация правил назначения ролей
        if role_type.is_system_role() and branch_id is not None:
            raise ValueError("Системные роли не могут быть привязаны к филиалу")
        
        if role_type.is_business_role() and branch_id is None:
            raise ValueError("Бизнес-роли должны быть привязаны к филиалу")
        
        return cls(
            id=uuid4(),
            user_id=user_id,
            role_type=role_type,
            branch_id=branch_id,
            assigned_at=datetime.now(timezone.utc),
            assigned_by=assigned_by
        )

    @property
    def is_global(self) -> bool:
        """Роль глобальная (не привязана к филиалу)"""
        return self.branch_id is None

    def __hash__(self):
        """Для использования в множествах"""
        return hash((self.user_id, self.role_type, self.branch_id))

    def __eq__(self, other):
        """Сравнение ролей"""
        if not isinstance(other, Role):
            return False
        return (
            self.user_id == other.user_id and
            self.role_type == other.role_type and
            self.branch_id == other.branch_id
        )