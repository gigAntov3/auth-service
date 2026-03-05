class ApplicationError(Exception):
    """Базовое исключение приложения"""
    pass

class ValidationError(ApplicationError):
    """Ошибка валидации"""
    def __init__(self, errors: list):
        self.errors = errors
        super().__init__(f"Validation failed: {', '.join(errors)}")

class AuthenticationError(ApplicationError):
    """Ошибка аутентификации"""
    pass

class AuthorizationError(ApplicationError):
    """Ошибка авторизации"""
    pass

class PermissionDeniedError(AuthorizationError):
    """Недостаточно прав"""
    pass

class UserAlreadyExistsError(ApplicationError):
    """Пользователь уже существует"""
    pass

class UserNotFoundError(ApplicationError):
    """Пользователь не найден"""
    pass

class CompanyNotFoundError(ApplicationError):
    """Компания не найдена"""
    pass

class AccountNotActiveError(ApplicationError):
    """Аккаунт не активен"""
    pass

class InvitationExpiredError(ApplicationError):
    """Приглашение истекло"""
    pass

class InvalidTokenError(ApplicationError):
    """Невалидный токен"""
    pass