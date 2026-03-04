import bcrypt
from uuid import uuid4
from domain.entities.user import UserEntity
from domain.entities.role import Role, RoleType
from domain.value_objects.email import Email
from domain.value_objects.password import PasswordHash


def create_test_user(email: str = "test@example.com", 
                    full_name: str = "Test UserEntity",
                    password: str = "Test123!@#") -> UserEntity:
    """
    Создает тестового пользователя с правильным хешем пароля.
    """
    # Генерируем настоящий bcrypt хеш
    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    return UserEntity.create(
        email=email,
        full_name=full_name,
        password_hash=password_hash
    )


def create_test_user_with_role(role_type: RoleType, 
                              branch_id=None,
                              email: str = None) -> UserEntity:
    """
    Создает тестового пользователя с указанной ролью.
    """
    if email is None:
        email = f"{role_type.value}@example.com"
    
    user = create_test_user(email=email)
    user.add_role(role_type, branch_id=branch_id, assigned_by=uuid4())
    return user


def get_valid_password_hash(password: str = "Test123!@#") -> str:
    """
    Возвращает валидный bcrypt хеш для тестов.
    """
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


# Константы для тестов
TEST_PASSWORD = "Test123!@#"
TEST_PASSWORD_HASH = get_valid_password_hash(TEST_PASSWORD)