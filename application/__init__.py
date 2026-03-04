"""
Application Layer - сценарии использования и DTO.

Содержит:
- Use Cases для аутентификации, управления пользователями и ролями
- DTO для передачи данных между слоями
- Интерфейсы (порты) для внешних зависимостей
- Исключения application слоя
"""

from application.dtos.auth_dto import (
    LoginRequestDTO, LoginResponseDTO,
    RegisterRequestDTO, RegisterResponseDTO,
    TokenDTO,
    VerifyEmailRequestDTO, VerifyEmailResponseDTO,
    ForgotPasswordRequestDTO, ForgotPasswordResponseDTO,
    ResetPasswordRequestDTO, ResetPasswordResponseDTO,
    ChangePasswordRequestDTO, ChangePasswordResponseDTO,
    RefreshTokenRequestDTO, RefreshTokenResponseDTO
)

from application.dtos.user_dto import (
    UserDTO, UserCreateDTO, UserUpdateDTO,
    UserListDTO, UserPermissionsDTO
)

from application.dtos.role_dto import (
    RoleDTO, RoleCreateDTO, RoleAssignmentDTO,
    RoleRemovalDTO, RoleTypeDTO
)

from application.use_cases.auth_use_cases import (
    RegisterUseCase,
    LoginUseCase,
    VerifyEmailUseCase,
    ForgotPasswordUseCase,
    ResetPasswordUseCase,
    RefreshTokenUseCase,
    ChangePasswordUseCase,
    LogoutUseCase
)

from application.interfaces.repositories import (
    UserRepository, RoleRepository, BranchRepository
)

from application.interfaces.unit_of_work import UnitOfWork
from application.interfaces.password_hasher import PasswordHasher
from application.interfaces.token_service import TokenService
from application.interfaces.email_sender import EmailSender
from application.interfaces.cache_service import CacheService

from application.exceptions import (
    ApplicationError,
    AuthenticationError,
    AuthorizationError,
    UserNotFoundError,
    UserAlreadyExistsError,
    InvalidCredentialsError,
    InvalidTokenError,
    TokenExpiredError,
    EmailNotVerifiedError,
    UserNotActiveError,
    InsufficientPermissionsError,
    RoleAssignmentError,
    ValidationError
)

__all__ = [
    # DTOs
    'LoginRequestDTO',
    'LoginResponseDTO',
    'RegisterRequestDTO',
    'RegisterResponseDTO',
    'TokenDTO',
    'VerifyEmailRequestDTO',
    'VerifyEmailResponseDTO',
    'ForgotPasswordRequestDTO',
    'ForgotPasswordResponseDTO',
    'ResetPasswordRequestDTO',
    'ResetPasswordResponseDTO',
    'ChangePasswordRequestDTO',
    'ChangePasswordResponseDTO',
    'RefreshTokenRequestDTO',
    'RefreshTokenResponseDTO',
    'UserDTO',
    'UserCreateDTO',
    'UserUpdateDTO',
    'UserListDTO',
    'UserPermissionsDTO',
    'RoleDTO',
    'RoleCreateDTO',
    'RoleAssignmentDTO',
    'RoleRemovalDTO',
    'RoleTypeDTO',
    
    # Use Cases
    'RegisterUseCase',
    'LoginUseCase',
    'VerifyEmailUseCase',
    'ForgotPasswordUseCase',
    'ResetPasswordUseCase',
    'RefreshTokenUseCase',
    'ChangePasswordUseCase',
    'LogoutUseCase',
    
    # Interfaces
    'UserRepository',
    'RoleRepository',
    'BranchRepository',
    'UnitOfWork',
    'PasswordHasher',
    'TokenService',
    'EmailSender',
    'CacheService',
    
    # Exceptions
    'ApplicationError',
    'AuthenticationError',
    'AuthorizationError',
    'UserNotFoundError',
    'UserAlreadyExistsError',
    'InvalidCredentialsError',
    'InvalidTokenError',
    'TokenExpiredError',
    'EmailNotVerifiedError',
    'UserNotActiveError',
    'InsufficientPermissionsError',
    'RoleAssignmentError',
    'ValidationError'
]