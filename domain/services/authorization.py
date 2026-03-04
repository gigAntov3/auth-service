from typing import Optional, List, Set
from uuid import UUID

from domain.entities.user import UserEntity
from domain.entities.role import RoleType, Role
from domain.exceptions.domain_exceptions import (
    InsufficientPermissionsError,
    RoleAssignmentError
)


class AuthorizationService:
    """
    Доменный сервис для проверки прав и авторизации.
    
    Содержит бизнес-логику, которая не вписывается в отдельные сущности.
    """

    @staticmethod
    def can_manage_user(manager: UserEntity, target_user: UserEntity) -> bool:
        """
        Проверяет, может ли manager управлять target_user.
        
        ПРАВИЛА (утвержденные):
        1. SUPER_ADMIN может управлять любыми пользователями.
        2. ADMIN может управлять всеми, кроме SUPER_ADMIN.
        3. OWNER может управлять только теми пользователями, у которых есть
        ХОТЯ БЫ ОДНА ЛОКАЛЬНАЯ РОЛЬ в его филиале.
        4. Обычные пользователи (только USER) не могут управлять другими.
        """
        # 1. SUPER_ADMIN
        if manager.has_role(RoleType.SUPER_ADMIN):
            return True

        # 2. ADMIN
        if manager.has_role(RoleType.ADMIN):
            return not target_user.has_role(RoleType.SUPER_ADMIN)

        # 3. OWNER
        owner_branches = {
            role.branch_id for role in manager.roles
            if role.role_type == RoleType.OWNER and role.branch_id
        }

        if owner_branches:
            for branch_id in owner_branches:
                # Ищем у target_user ЛОКАЛЬНЫЕ роли в этом филиале
                target_has_local_role = any(
                    not role.is_global and role.branch_id == branch_id
                    for role in target_user.roles
                )
                if target_has_local_role:
                    return True
            return False

        # 4. Обычный пользователь
        return False

    @staticmethod
    def can_assign_role(assigner: UserEntity, target_user: UserEntity, new_role: RoleType) -> bool:
        """
        Проверяет, может ли assigner назначить роль target_user.
        
        Более строгая проверка, чем can_manage_user.
        """
        # SUPER_ADMIN может назначать любые роли
        if assigner.has_role(RoleType.SUPER_ADMIN):
            return True

        # ADMIN может назначать любые роли, кроме SUPER_ADMIN
        if assigner.has_role(RoleType.ADMIN):
            return new_role != RoleType.SUPER_ADMIN

        # OWNER может назначать только бизнес-роли в своих филиалах
        if assigner.has_role(RoleType.OWNER) and new_role.is_business_role():
            # Получаем филиалы assigner
            assigner_branches = {
                role.branch_id
                for role in assigner.roles
                if role.role_type == RoleType.OWNER and role.branch_id
            }
            
            # Получаем филиалы target_user
            target_branches = {
                role.branch_id
                for role in target_user.roles
                if role.branch_id
            }
            
            return bool(assigner_branches & target_branches)

        # Обычные пользователи не могут назначать роли
        return False

    @staticmethod
    def filter_accessible_branches(user: UserEntity, all_branches: List) -> List:
        """
        Фильтрует список филиалов, оставляя только доступные пользователю.
        
        Args:
            user: Пользователь
            all_branches: Список всех филиалов (объекты с атрибутом id)
        
        Returns:
            Список доступных филиалов
        """
        # SUPER_ADMIN и ADMIN видят всё
        if user.has_any_role([RoleType.SUPER_ADMIN, RoleType.ADMIN]):
            return all_branches

        # OWNER видит свои филиалы
        if user.has_role(RoleType.OWNER):
            owner_branches = {
                role.branch_id
                for role in user.roles
                if role.role_type == RoleType.OWNER and role.branch_id
            }
            return [
                branch for branch in all_branches
                if branch.id in owner_branches
            ]

        # Для остальных - только филиалы, где есть другие роли
        accessible_branch_ids = {
            role.branch_id
            for role in user.roles
            if role.branch_id
        }

        return [
            branch for branch in all_branches
            if branch.id in accessible_branch_ids
        ]

    @staticmethod
    def validate_role_assignment(
        assigner: UserEntity,
        target_user: UserEntity,
        role_type: RoleType,
        branch_id: Optional[UUID] = None
    ) -> None:
        """
        Комплексная проверка возможности назначения роли.
        Выбрасывает исключение, если назначение невозможно.
        """
        # Проверяем активность пользователей
        assigner.ensure_active()
        target_user.ensure_active()

        # Проверяем права на назначение
        if not AuthorizationService.can_assign_role(assigner, target_user, role_type):
            raise InsufficientPermissionsError(
                f"Нет прав для назначения роли {role_type.value}"
            )

        # Дополнительные проверки для бизнес-ролей
        if role_type.is_business_role() and not branch_id:
            raise RoleAssignmentError(
                "Для бизнес-роли необходимо указать филиал"
            )

        if role_type.is_system_role() and branch_id:
            raise RoleAssignmentError(
                "Системные роли не могут быть привязаны к филиалу"
            )


class PasswordValidationService:
    """
    Сервис для валидации и генерации паролей.
    """

    @staticmethod
    def validate_password_strength(password: str) -> tuple[bool, list[str]]:
        """
        Проверяет сложность пароля.
        
        Returns:
            (is_valid, list_of_issues)
        """
        issues = []
        
        if len(password) < 8:
            issues.append("минимум 8 символов")
        
        if not any(c.isupper() for c in password):
            issues.append("хотя бы одну заглавную букву")
        
        if not any(c.islower() for c in password):
            issues.append("хотя бы одну строчную букву")
        
        if not any(c.isdigit() for c in password):
            issues.append("хотя бы одну цифру")
        
        if not any(c in "!@#$%^&*" for c in password):
            issues.append("хотя бы один спецсимвол (!@#$%^&*)")
        
        return len(issues) == 0, issues

    @staticmethod
    def generate_temporary_password(length: int = 12) -> str:
        """
        Генерирует временный пароль.
        
        Args:
            length: Длина пароля (минимум 8)
        
        Returns:
            Сгенерированный пароль
        """
        import secrets
        import string
        
        if length < 8:
            length = 8
        
        # Гарантируем наличие всех типов символов
        alphabet = (
            string.ascii_uppercase +
            string.ascii_lowercase +
            string.digits +
            "!@#$%^&*"
        )
        
        while True:
            password = ''.join(secrets.choice(alphabet) for _ in range(length))
            # Проверяем, что пароль соответствует требованиям
            is_valid, _ = PasswordValidationService.validate_password_strength(password)
            if is_valid:
                return password