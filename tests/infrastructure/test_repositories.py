import pytest
from uuid import uuid4
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from domain.entities.user import UserEntity
from domain.entities.role import Role, RoleType
from domain.value_objects.email import Email
from domain.value_objects.password import PasswordHash

from infrastructure.database.models.user_model import UserEntityModel
from infrastructure.database.models.role_model import RoleModel
from infrastructure.database.models.branch_model import BranchModel
from infrastructure.database.base import Base
from infrastructure.database.repositories.user_repository import SQLAlchemyUserEntityRepository
from infrastructure.database.repositories.role_repository import SQLAlchemyRoleRepository

from tests.helpers import get_valid_password_hash


TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture
async def engine():
    """Фикстура для создания движка БД"""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    
    # Создаем таблицы
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Удаляем таблицы
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture
async def session(engine):
    """Фикстура для создания сессии БД"""
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    
    async with async_session() as session:
        yield session
        await session.rollback()
        await session.close()


@pytest.fixture
def user_repo(session: AsyncSession):
    """Фикстура для репозитория пользователей"""
    return SQLAlchemyUserEntityRepository(session)


@pytest.fixture
def role_repo(session: AsyncSession):
    """Фикстура для репозитория ролей"""
    return SQLAlchemyRoleRepository(session)


class TestUserEntityRepository:
    """Интеграционные тесты для репозитория пользователей"""

    @pytest.mark.asyncio
    async def test_save_and_get_by_id(self, user_repo, session):
        """Тест сохранения и получения пользователя по ID"""
        # Создаем пользователя
        user_id = uuid4()
        user = UserEntity(
            id=user_id,
            email=Email("test@example.com"),
            full_name="Test UserEntity",
            password_hash=PasswordHash(get_valid_password_hash()),
            is_active=True,
            is_email_verified=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        # Сохраняем
        await user_repo.save(user)
        await session.commit()
        
        # Получаем по ID
        found = await user_repo.get_by_id(user_id)
        
        assert found is not None
        assert found.id == user_id
        assert found.email.value == "test@example.com"
        assert found.full_name == "Test UserEntity"
        assert found.is_active is True

    @pytest.mark.asyncio
    async def test_get_by_email(self, user_repo, session):
        """Тест получения пользователя по email"""
        user_id = uuid4()
        email = "unique@example.com"
        
        user = UserEntity(
            id=user_id,
            email=Email(email),
            full_name="Test UserEntity",
            password_hash=PasswordHash(get_valid_password_hash()),
            is_active=True,
            is_email_verified=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        await user_repo.save(user)
        await session.commit()
        
        found = await user_repo.get_by_email(email)
        
        assert found is not None
        assert found.id == user_id
        assert found.email.value == email

    @pytest.mark.asyncio
    async def test_update_user(self, user_repo, session):
        """Тест обновления пользователя"""
        user_id = uuid4()
        
        user = UserEntity(
            id=user_id,
            email=Email("test@example.com"),
            full_name="Old Name",
            password_hash=PasswordHash(get_valid_password_hash()),
            is_active=True,
            is_email_verified=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        await user_repo.save(user)
        await session.commit()
        
        # Обновляем
        user.full_name = "New Name"
        user.is_email_verified = True
        user.updated_at = datetime.now(timezone.utc)
        
        await user_repo.update(user)
        await session.commit()
        
        # Получаем обновленного пользователя
        updated = await user_repo.get_by_id(user_id)
        assert updated is not None
        assert updated.full_name == "New Name"
        assert updated.is_email_verified is True

    @pytest.mark.asyncio
    async def test_delete_user(self, user_repo, session):
        """Тест удаления пользователя"""
        user_id = uuid4()
        
        user = UserEntity(
            id=user_id,
            email=Email("test@example.com"),
            full_name="Test UserEntity",
            password_hash=PasswordHash(get_valid_password_hash()),
            is_active=True,
            is_email_verified=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        await user_repo.save(user)
        await session.commit()
        
        # Проверяем, что пользователь есть
        found = await user_repo.get_by_id(user_id)
        assert found is not None
        
        # Удаляем
        await user_repo.delete(user_id)
        await session.commit()
        
        # Проверяем, что пользователь удален
        found = await user_repo.get_by_id(user_id)
        assert found is None


class TestRoleRepository:
    """Интеграционные тесты для репозитория ролей"""

    @pytest.mark.asyncio
    async def test_add_and_get_by_user(self, user_repo, role_repo, session):
        """Тест добавления роли и получения по пользователю"""
        # Создаем пользователя
        user_id = uuid4()
        user = UserEntity(
            id=user_id,
            email=Email("test@example.com"),
            full_name="Test UserEntity",
            password_hash=PasswordHash(get_valid_password_hash()),
            is_active=True,
            is_email_verified=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        await user_repo.save(user)
        await session.commit()
        
        # Создаем роль
        role = Role.create(
            user_id=user_id,
            role_type=RoleType.MANAGER,
            assigned_by=uuid4(),
            branch_id=uuid4()
        )
        
        # Добавляем роль
        await role_repo.add(role)
        await session.commit()
        
        # Получаем роли пользователя
        roles = await role_repo.get_by_user(user_id)
        
        assert len(roles) == 1
        assert roles[0].role_type == RoleType.MANAGER
        assert roles[0].user_id == user_id

    @pytest.mark.asyncio
    async def test_remove_role(self, user_repo, role_repo, session):
        """Тест удаления роли"""
        user_id = uuid4()
        branch_id = uuid4()
        
        # Создаем пользователя
        user = UserEntity(
            id=user_id,
            email=Email("test@example.com"),
            full_name="Test UserEntity",
            password_hash=PasswordHash(get_valid_password_hash()),
            is_active=True,
            is_email_verified=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        await user_repo.save(user)
        await session.commit()
        
        # Создаем роль
        role = Role.create(
            user_id=user_id,
            role_type=RoleType.MANAGER,
            assigned_by=uuid4(),
            branch_id=branch_id
        )
        
        # Добавляем роль
        await role_repo.add(role)
        await session.commit()
        
        # Проверяем, что роль есть
        roles_before = await role_repo.get_by_user(user_id)
        assert len(roles_before) == 1
        
        # Удаляем роль
        await role_repo.remove(user_id, RoleType.MANAGER, branch_id)
        await session.commit()
        
        # Проверяем, что роль удалена
        roles_after = await role_repo.get_by_user(user_id)
        assert len(roles_after) == 0

    @pytest.mark.asyncio
    async def test_user_has_role(self, user_repo, role_repo, session):
        """Тест проверки наличия роли у пользователя"""
        user_id = uuid4()
        branch_id = uuid4()
        
        # Создаем пользователя
        user = UserEntity(
            id=user_id,
            email=Email("test@example.com"),
            full_name="Test UserEntity",
            password_hash=PasswordHash(get_valid_password_hash()),
            is_active=True,
            is_email_verified=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        await user_repo.save(user)
        await session.commit()
        
        # Добавляем роль
        role = Role.create(
            user_id=user_id,
            role_type=RoleType.MANAGER,
            assigned_by=uuid4(),
            branch_id=branch_id
        )
        await role_repo.add(role)
        await session.commit()
        
        # Проверяем
        has_role = await role_repo.user_has_role(user_id, RoleType.MANAGER, branch_id)
        assert has_role is True
        
        has_role_wrong = await role_repo.user_has_role(user_id, RoleType.ADMIN, branch_id)
        assert has_role_wrong is False