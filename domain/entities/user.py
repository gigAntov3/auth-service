from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional, Set, List
from uuid import UUID, uuid4

from domain.value_objects.email import Email
from domain.value_objects.password import PasswordHash
from domain.entities.role import Role, RoleType
from domain.exceptions.domain_exceptions import (
    UserNotActiveError,
    InsufficientPermissionsError,
    EmailNotVerifiedError
)


@dataclass
class UserEntity:
    """
    Агрегат - Пользователь системы.
    
    Содержит всю бизнес-логику, связанную с пользователем.
    Является корнем агрегата (содержит роли).
    """
    id: UUID
    email: Email
    full_name: str
    password_hash: PasswordHash
    is_active: bool = True
    is_email_verified: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_login_at: Optional[datetime] = None
    _roles: Set[Role] = field(default_factory=set, repr=False)

    @classmethod
    def create(cls, email: str, full_name: str, password_hash: str) -> 'User':
        """Фабричный метод для создания нового пользователя"""
        user = cls(
            id=uuid4(),
            email=Email(email),
            full_name=full_name.strip(),
            password_hash=PasswordHash(password_hash),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        # Автоматически назначаем базовую роль USER
        user.add_role(
            role_type=RoleType.USER,
            assigned_by=None  # Система
        )
        
        return user

    # ========== Управление ролями ==========

    @property
    def roles(self) -> Set[Role]:
        """Возвращает копию множества ролей"""
        return self._roles.copy()

    def add_role(
        self,
        role_type: RoleType,
        assigned_by: Optional[UUID] = None,
        branch_id: Optional[UUID] = None
    ) -> None:
        """
        Добавляет роль пользователю.
        
        Проверяет:
        - Нельзя добавить дубликат роли
        - Правила привязки к филиалу
        - Для глобальной роли USER нельзя создать локальную копию
        """
        # Специальная проверка для роли USER
        if role_type == RoleType.USER:
            # Проверяем, есть ли уже глобальная роль USER
            has_global_user = any(
                r.role_type == RoleType.USER and r.is_global 
                for r in self._roles
            )
            
            if has_global_user and branch_id is not None:
                raise ValueError("Нельзя добавить локальную роль USER, так как глобальная уже существует")
            
            # Если пытаемся добавить глобальную USER, а она уже есть
            if has_global_user and branch_id is None:
                raise ValueError("Роль USER уже существует")
        
        new_role = Role.create(
            user_id=self.id,
            role_type=role_type,
            assigned_by=assigned_by,
            branch_id=branch_id
        )
        
        # Проверяем, нет ли уже такой роли
        if new_role in self._roles:
            raise ValueError(f"Роль {role_type.value} уже назначена")
        
        self._roles.add(new_role)
        self._update_timestamp()

    def remove_role(self, role_type: RoleType, branch_id: Optional[UUID] = None) -> None:
        """
        Удаляет роль у пользователя.
        
        Нельзя удалить базовую роль USER.
        """
        # Защищаем от удаления базовой роли
        if role_type == RoleType.USER and branch_id is None:
            raise ValueError("Нельзя удалить базовую роль USER")
        
        role_to_remove = None
        for role in self._roles:
            if role.role_type == role_type and role.branch_id == branch_id:
                role_to_remove = role
                break
        
        if role_to_remove:
            self._roles.remove(role_to_remove)
            self._update_timestamp()

    def has_role(self, role_type: RoleType, branch_id: Optional[UUID] = None) -> bool:
        """
        Проверяет наличие конкретной роли.
        
        Args:
            role_type: Тип роли
            branch_id: Для бизнес-ролей - филиал, для системных - игнорируется
        """
        print(f"    DEBUG has_role: checking {role_type.value}, branch={branch_id}")
        for role in self._roles:
            print(f"      Comparing with: {role.role_type.value}, branch={role.branch_id}, is_global={role.is_global}")
            if role.role_type == role_type:
                # Для системных ролей branch_id игнорируем
                if role_type.is_system_role():
                    print(f"        Found system role {role_type.value} -> True")
                    return True
                # Для бизнес-ролей проверяем филиал
                if role.branch_id == branch_id:
                    print(f"        Found business role {role_type.value} in branch {branch_id} -> True")
                    return True
        print(f"      Role {role_type.value} not found -> False")
        return False

    def has_any_role(self, role_types: List[RoleType], branch_id: Optional[UUID] = None) -> bool:
        """Проверяет наличие хотя бы одной из указанных ролей"""
        return any(self.has_role(rt, branch_id) for rt in role_types)

    def has_all_roles(self, role_types: List[RoleType], branch_id: Optional[UUID] = None) -> bool:
        """Проверяет наличие всех указанных ролей"""
        return all(self.has_role(rt, branch_id) for rt in role_types)

    def get_roles_in_branch(self, branch_id: UUID) -> Set[RoleType]:
        """
        Возвращает все роли пользователя в конкретном филиале.
        
        Включает:
        - Роли, явно привязанные к этому филиалу
        - Глобальные роли (системные), которые действуют во всех филиалах
        
        Args:
            branch_id: ID филиала
            
        Returns:
            Set[RoleType]: Множество ролей
        """
        roles_in_branch = set()
        
        for role in self._roles:
            # Добавляем роли, привязанные к этому филиалу
            if role.branch_id == branch_id:
                roles_in_branch.add(role.role_type)
                print(f"    DEBUG: Добавлена локальная роль {role.role_type.value} для филиала {branch_id}")
            
            # Добавляем глобальные роли (они действуют во всех филиалах)
            elif role.is_global:
                roles_in_branch.add(role.role_type)
                print(f"    DEBUG: Добавлена глобальная роль {role.role_type.value}")
        
        return roles_in_branch

    def get_all_permissions(self) -> dict:
        """
        Возвращает словарь всех разрешений пользователя.
        
        Формат: {
            "global": ["super_admin", "admin"],
            "branch_id_1": ["owner", "manager"],
            "branch_id_2": ["accountant"]
        }
        """
        permissions = {"global": []}
        
        for role in self._roles:
            if role.is_global:
                permissions["global"].append(role.role_type.value)
            else:
                branch_key = str(role.branch_id)
                if branch_key not in permissions:
                    permissions[branch_key] = []
                permissions[branch_key].append(role.role_type.value)
        
        return permissions

    # ========== Управление статусом ==========

    def activate(self) -> None:
        """Активирует пользователя"""
        if not self.is_active:
            self.is_active = True
            self._update_timestamp()

    def deactivate(self) -> None:
        """Деактивирует пользователя"""
        if self.is_active:
            self.is_active = False
            self._update_timestamp()

    def verify_email(self) -> None:
        """Подтверждает email"""
        if not self.is_email_verified:
            self.is_email_verified = True
            self._update_timestamp()

    def update_last_login(self) -> None:
        """Обновляет время последнего входа"""
        self.last_login_at = datetime.now(timezone.utc)
        self._update_timestamp()
    
    def _update_timestamp(self) -> None:
        """Обновляет время изменения"""
        self.updated_at = datetime.now(timezone.utc)

    # ========== Проверки безопасности ==========

    def ensure_active(self) -> None:
        """Проверяет, активен ли пользователь"""
        if not self.is_active:
            raise UserNotActiveError("Пользователь деактивирован")

    def ensure_email_verified(self) -> None:
        """Проверяет, подтвержден ли email"""
        if not self.is_email_verified:
            raise EmailNotVerifiedError("Email не подтвержден")

    def require_role(self, role_type: RoleType, branch_id: Optional[UUID] = None) -> None:
        """
        Требует наличие конкретной роли.
        Если роли нет - выбрасывает исключение.
        """
        if not self.has_role(role_type, branch_id):
            role_name = role_type.value
            branch_info = f" в филиале {branch_id}" if branch_id else ""
            raise InsufficientPermissionsError(
                f"Требуется роль {role_name}{branch_info}"
            )

    def require_any_role(self, role_types: List[RoleType], branch_id: Optional[UUID] = None) -> None:
        """Требует наличие хотя бы одной из указанных ролей"""
        if not self.has_any_role(role_types, branch_id):
            roles_str = ", ".join(rt.value for rt in role_types)
            branch_info = f" в филиале {branch_id}" if branch_id else ""
            raise InsufficientPermissionsError(
                f"Требуется одна из ролей: {roles_str}{branch_info}"
            )