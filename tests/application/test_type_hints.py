"""
Тесты для проверки типизации.
Запускается с mypy или pyright.
"""
from uuid import UUID, uuid4
from datetime import datetime
from typing import List, Optional, Dict, Any
from unittest.mock import AsyncMock, Mock

from domain.entities.user import UserEntity
from domain.entities.role import Role, RoleType
from domain.value_objects.email import Email
from domain.value_objects.password import PasswordHash

from application.dtos.auth_dto import (
    LoginRequestDTO, LoginResponseDTO, TokenDTO,
    RegisterRequestDTO, RegisterResponseDTO
)
from application.dtos.user_dto import UserEntityDTO, UserEntityCreateDTO
from application.dtos.role_dto import RoleDTO, RoleAssignmentDTO, RoleTypeDTO

from application.use_cases.auth_use_cases import (
    RegisterUseCase, LoginUseCase, VerifyEmailUseCase
)
from application.interfaces.repositories import UserEntityRepository, RoleRepository
from application.interfaces.unit_of_work import UnitOfWork
from application.interfaces.password_hasher import PasswordHasher
from application.interfaces.token_service import TokenService


def test_dto_type_hints():
    """Проверка типов в DTO"""
    
    # LoginRequestDTO
    login_request = LoginRequestDTO(
        email="test@example.com",
        password="password"
    )
    assert isinstance(login_request.email, str)
    assert isinstance(login_request.password, str)
    assert isinstance(login_request.remember_me, bool)
    
    # LoginResponseDTO
    token = TokenDTO(
        access_token="access",
        refresh_token="refresh",
        expires_in=3600,
        refresh_expires_in=86400
    )
    login_response = LoginResponseDTO(
        user_id=UUID('12345678-1234-5678-1234-567812345678'),
        email="test@example.com",
        full_name="Test UserEntity",
        tokens=token,
        permissions={"global": ["user"]}
    )
    assert isinstance(login_response.user_id, UUID)
    assert isinstance(login_response.email, str)
    assert isinstance(login_response.tokens, TokenDTO)
    assert isinstance(login_response.permissions, dict)
    
    # RegisterRequestDTO
    register_request = RegisterRequestDTO(
        email="test@example.com",
        password="StrongP@ssw0rd",
        full_name="Test UserEntity"
    )
    assert isinstance(register_request.email, str)
    assert isinstance(register_request.password, str)
    assert isinstance(register_request.full_name, str)
    
    # RoleAssignmentDTO
    role_assignment = RoleAssignmentDTO(
        user_id=UUID('12345678-1234-5678-1234-567812345678'),
        role_type=RoleTypeDTO.MANAGER,
        branch_id=UUID('12345678-1234-5678-1234-567812345679')
    )
    assert isinstance(role_assignment.user_id, UUID)
    assert isinstance(role_assignment.role_type, RoleTypeDTO)
    assert isinstance(role_assignment.branch_id, UUID)


def test_use_case_type_hints():
    """Проверка типов в Use Cases"""
    
    # Проверяем, что use cases принимают правильные типы
    async def check_register_use_case(use_case: RegisterUseCase):
        request = RegisterRequestDTO(
            email="test@example.com",
            password="StrongP@ssw0rd",
            full_name="Test UserEntity"
        )
        response = await use_case.execute(request)
        assert isinstance(response, RegisterResponseDTO)
    
    async def check_login_use_case(use_case: LoginUseCase):
        request = LoginRequestDTO(
            email="test@example.com",
            password="StrongP@ssw0rd"
        )
        response = await use_case.execute(request)
        assert isinstance(response, LoginResponseDTO)


def test_repository_type_hints():
    """Проверка типов в интерфейсах репозиториев"""
    
    # Создаем конкретную реализацию для теста
    class TestUserEntityRepository(UserEntityRepository):
        """Тестовая реализация для проверки типов"""
        
        async def get_by_id(self, user_id: UUID) -> Optional[UserEntity]:
            return None
        
        async def get_by_email(self, email: str) -> Optional[UserEntity]:
            return None
        
        async def save(self, user: UserEntity) -> None:
            pass
        
        async def update(self, user: UserEntity) -> None:
            pass
        
        async def delete(self, user_id: UUID) -> None:
            pass
        
        async def list(self, skip: int = 0, limit: int = 100, 
                       branch_id: Optional[UUID] = None) -> List[UserEntity]:
            return []
        
        async def count(self, branch_id: Optional[UUID] = None) -> int:
            return 0
    
    # Проверяем, что все методы реализованы с правильными типами
    repo = TestUserEntityRepository()
    assert isinstance(repo, UserEntityRepository)


def test_unit_of_work_type_hints():
    """Проверка типов в Unit of Work"""
    
    # Создаем конкретные реализации для теста
    class TestUserEntityRepository(UserEntityRepository):
        async def get_by_id(self, user_id: UUID) -> Optional[UserEntity]:
            return None
        async def get_by_email(self, email: str) -> Optional[UserEntity]:
            return None
        async def save(self, user: UserEntity) -> None:
            pass
        async def update(self, user: UserEntity) -> None:
            pass
        async def delete(self, user_id: UUID) -> None:
            pass
        async def list(self, skip: int = 0, limit: int = 100, 
                       branch_id: Optional[UUID] = None) -> List[UserEntity]:
            return []
        async def count(self, branch_id: Optional[UUID] = None) -> int:
            return 0
    
    class TestRoleRepository(RoleRepository):
        async def get_by_id(self, role_id: UUID) -> Optional[Role]:
            return None
        async def get_by_user(self, user_id: UUID) -> List[Role]:
            return []
        async def add(self, role: Role) -> None:
            pass
        async def remove(self, user_id: UUID, role_type: RoleType, 
                         branch_id: Optional[UUID] = None) -> None:
            pass
        async def get_users_by_role(self, role_type: RoleType, 
                                     branch_id: Optional[UUID] = None) -> List[UUID]:
            return []
        async def user_has_role(self, user_id: UUID, role_type: RoleType,
                                branch_id: Optional[UUID] = None) -> bool:
            return False
    
    class TestUnitOfWork(UnitOfWork):
        """Тестовая реализация для проверки типов"""
        
        def __init__(self):
            self._users = TestUserEntityRepository()
            self._roles = TestRoleRepository()
            self._branches = Mock()
        
        async def __aenter__(self):
            return self
        
        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass
        
        async def commit(self):
            pass
        
        async def rollback(self):
            pass
        
        @property
        def users(self) -> UserEntityRepository:
            return self._users
        
        @property
        def roles(self) -> RoleRepository:
            return self._roles
        
        @property
        def branches(self):
            return self._branches
    
    # Проверяем, что все свойства имеют правильные типы
    uow = TestUnitOfWork()
    assert isinstance(uow.users, UserEntityRepository)
    assert isinstance(uow.roles, RoleRepository)