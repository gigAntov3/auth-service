"""
Domain Layer - ядро бизнес-логики системы авторизации.

Содержит:
- Сущности: UserEntity, Role
- Value Objects: Email, PasswordHash
- Сервисы: AuthorizationService, PasswordValidationService
- Интерфейсы репозиториев
- Доменные исключения
"""

from domain.entities.user import UserEntity
from domain.entities.role import Role, RoleType
from domain.value_objects.email import Email
from domain.value_objects.password import PasswordHash, RawPassword
from domain.services.authorization import AuthorizationService, PasswordValidationService
from domain.repositories.interfaces import UserEntityRepository, RoleRepository, UnitOfWork
from domain.exceptions.domain_exceptions import (
    DomainError,
    UserNotFoundError,
    InvalidCredentialsError,
    UserAlreadyExistsError,
    UserNotActiveError,
    InsufficientPermissionsError,
    EmailNotVerifiedError,
    InvalidTokenError,
    RoleAssignmentError
)

__all__ = [
    # Entities
    'UserEntity',
    'Role',
    'RoleType',
    
    # Value Objects
    'Email',
    'PasswordHash',
    'RawPassword',
    
    # Services
    'AuthorizationService',
    'PasswordValidationService',
    
    # Repository Interfaces
    'UserEntityRepository',
    'RoleRepository',
    'UnitOfWork',
    
    # Exceptions
    'DomainError',
    'UserEntityNotFoundError',
    'InvalidCredentialsError',
    'UserEntityAlreadyExistsError',
    'UserEntityNotActiveError',
    'InsufficientPermissionsError',
    'EmailNotVerifiedError',
    'InvalidTokenError',
    'RoleAssignmentError'
]