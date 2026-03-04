class DomainError(Exception):
    """Базовое исключение для всех доменных ошибок"""
    pass


class UserNotFoundError(DomainError):
    """Пользователь не найден"""
    pass


class InvalidCredentialsError(DomainError):
    """Неверные учетные данные"""
    pass


class UserAlreadyExistsError(DomainError):
    """Пользователь уже существует"""
    pass


class UserNotActiveError(DomainError):
    """Пользователь не активен"""
    pass


class InsufficientPermissionsError(DomainError):
    """Недостаточно прав"""
    pass


class EmailNotVerifiedError(DomainError):
    """Email не подтвержден"""
    pass


class InvalidTokenError(DomainError):
    """Неверный или просроченный токен"""
    pass


class RoleAssignmentError(DomainError):
    """Ошибка при назначении роли"""
    pass