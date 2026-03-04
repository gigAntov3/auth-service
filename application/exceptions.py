class ApplicationError(Exception):
    """Базовое исключение для application слоя"""
    pass


class AuthenticationError(ApplicationError):
    """Ошибка аутентификации"""
    pass


class AuthorizationError(ApplicationError):
    """Ошибка авторизации"""
    pass


class UserNotFoundError(ApplicationError):
    """Пользователь не найден"""
    pass


class UserAlreadyExistsError(ApplicationError):
    """Пользователь уже существует"""
    pass


class InvalidCredentialsError(AuthenticationError):
    """Неверные учетные данные"""
    pass


class TokenExpiredError(AuthenticationError):
    """Токен истек"""
    pass


class InvalidTokenError(AuthenticationError):
    """Неверный токен"""
    pass


class EmailNotVerifiedError(AuthorizationError):
    """Email не подтвержден"""
    pass


class UserNotActiveError(AuthorizationError):
    """Пользователь не активен"""
    pass


class InsufficientPermissionsError(AuthorizationError):
    """Недостаточно прав"""
    pass


class RoleAssignmentError(ApplicationError):
    """Ошибка при назначении роли"""
    pass


class ValidationError(ApplicationError):
    """Ошибка валидации"""
    pass