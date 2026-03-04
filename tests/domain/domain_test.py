# test.py - полные исправленные функции

from uuid import uuid4
from datetime import datetime

# Импортируем все необходимые классы
from domain.entities.user import UserEntity
from domain.entities.role import Role, RoleType
from domain.value_objects.email import Email
from domain.value_objects.password import PasswordHash, RawPassword
from domain.services.authorization import AuthorizationService, PasswordValidationService
from domain.exceptions.domain_exceptions import (
    UserEntityNotActiveError,
    InsufficientPermissionsError,
    EmailNotVerifiedError,
    RoleAssignmentError
)

from ..helpers import (
    create_test_user,
    create_test_user_with_role,
    get_valid_password_hash,
    TEST_PASSWORD_HASH,
    TEST_PASSWORD
)


def test_user_creation():
    """Тест создания пользователя"""
    print("\n=== Тест создания пользователя ===")
    
    # Используем правильный хеш
    user = UserEntity.create(
        email="test@example.com",
        full_name="Test UserEntity",
        password_hash=TEST_PASSWORD_HASH
    )
    
    print(f"UserEntity ID: {user.id}")
    print(f"Email: {user.email}")
    print(f"Full name: {user.full_name}")
    print(f"Active: {user.is_active}")
    print(f"Email verified: {user.is_email_verified}")
    print(f"Created at: {user.created_at}")
    
    # Проверяем базовую роль
    roles = list(user.roles)
    print(f"Roles: {[r.role_type.value for r in roles]}")
    
    assert user.email.value == "test@example.com"
    assert user.full_name == "Test UserEntity"
    assert user.is_active is True
    assert len(roles) == 1
    assert roles[0].role_type == RoleType.USER
    
    print("✅ Тест создания пользователя пройден")
    return user


def test_role_management(user):
    """Тест управления ролями"""
    print("\n=== Тест управления ролями ===")
    
    branch_id = uuid4()
    print(f"Branch ID: {branch_id}")
    
    # Добавляем роль менеджера
    user.add_role(
        role_type=RoleType.MANAGER,
        branch_id=branch_id,
        assigned_by=uuid4()
    )
    print(f"Добавлена роль менеджера в филиале")
    
    # Проверяем наличие роли
    assert user.has_role(RoleType.MANAGER, branch_id) is True
    assert user.has_role(RoleType.MANAGER) is False  # Без branch_id не должна находиться
    
    # Проверяем has_any_role
    assert user.has_any_role([RoleType.MANAGER, RoleType.ADMIN], branch_id) is True
    assert user.has_any_role([RoleType.ADMIN, RoleType.OWNER], branch_id) is False
    
    # Получаем роли в филиале
    branch_roles = user.get_roles_in_branch(branch_id)
    print(f"Роли в филиале: {[r.value for r in branch_roles]}")
    
    # Проверяем, что в филиале есть:
    # - роль USER (глобальная)
    # - роль MANAGER (привязанная к филиалу)
    assert RoleType.USER in branch_roles, "Глобальная роль USER должна быть в филиале"
    assert RoleType.MANAGER in branch_roles, "Роль MANAGER должна быть в филиале"
    assert len(branch_roles) == 2, f"Ожидалось 2 роли, получено {len(branch_roles)}"
    
    print("✓ Глобальная роль USER доступна в филиале")
    print("✓ Роль MANAGER доступна в филиале")
    
    # Удаляем роль
    user.remove_role(RoleType.MANAGER, branch_id)
    print("Роль менеджера удалена")
    
    assert user.has_role(RoleType.MANAGER, branch_id) is False
    
    # Проверяем роли после удаления
    branch_roles_after = user.get_roles_in_branch(branch_id)
    print(f"Роли в филиале после удаления: {[r.value for r in branch_roles_after]}")
    
    assert RoleType.USER in branch_roles_after, "Глобальная роль USER должна остаться"
    assert RoleType.MANAGER not in branch_roles_after, "Роль MANAGER должна быть удалена"
    assert len(branch_roles_after) == 1, f"Ожидалась 1 роль, получено {len(branch_roles_after)}"
    
    print("✅ Тест управления ролями пройден")


def test_global_roles_in_branches(user):
    """Тест поведения глобальных ролей в филиалах"""
    print("\n=== Тест глобальных ролей в филиалах ===")
    
    # Создаем несколько филиалов
    branch1 = uuid4()
    branch2 = uuid4()
    branch3 = uuid4()
    
    print(f"Филиал 1: {branch1}")
    print(f"Филиал 2: {branch2}")
    print(f"Филиал 3: {branch3}")
    
    # Добавляем глобальную роль ADMIN
    admin_id = uuid4()
    user.add_role(RoleType.ADMIN, assigned_by=admin_id)
    print("Добавлена глобальная роль ADMIN")
    
    # Добавляем роль MANAGER только в branch1
    user.add_role(RoleType.MANAGER, branch_id=branch1)
    print("Добавлена роль MANAGER в филиал 1")
    
    # Добавляем роль ACCOUNTANT в branch2
    user.add_role(RoleType.ACCOUNTANT, branch_id=branch2)
    print("Добавлена роль ACCOUNTANT в филиал 2")
    
    # Проверяем роли в каждом филиале
    roles_branch1 = user.get_roles_in_branch(branch1)
    roles_branch2 = user.get_roles_in_branch(branch2)
    roles_branch3 = user.get_roles_in_branch(branch3)
    
    print(f"\nРоли в филиале 1: {[r.value for r in roles_branch1]}")
    print(f"Роли в филиале 2: {[r.value for r in roles_branch2]}")
    print(f"Роли в филиале 3: {[r.value for r in roles_branch3]}")
    
    # Проверка филиала 1
    assert RoleType.USER in roles_branch1
    assert RoleType.ADMIN in roles_branch1  # глобальная роль
    assert RoleType.MANAGER in roles_branch1
    assert RoleType.ACCOUNTANT not in roles_branch1
    assert len(roles_branch1) == 3
    
    # Проверка филиала 2
    assert RoleType.USER in roles_branch2
    assert RoleType.ADMIN in roles_branch2  # глобальная роль
    assert RoleType.ACCOUNTANT in roles_branch2
    assert RoleType.MANAGER not in roles_branch2
    assert len(roles_branch2) == 3
    
    # Проверка филиала 3 (только глобальные роли)
    assert RoleType.USER in roles_branch3
    assert RoleType.ADMIN in roles_branch3  # глобальная роль
    assert RoleType.MANAGER not in roles_branch3
    assert RoleType.ACCOUNTANT not in roles_branch3
    assert len(roles_branch3) == 2
    
    print("\n✓ Глобальные роли доступны во всех филиалах")
    print("✓ Локальные роли доступны только в своих филиалах")
    
    print("✅ Тест глобальных ролей в филиалах пройден")


def test_permissions(user):
    """Тест получения разрешений"""
    print("\n=== Тест получения разрешений ===")
    
    # Добавляем несколько ролей
    branch1 = uuid4()
    branch2 = uuid4()
    
    user.add_role(RoleType.MANAGER, branch_id=branch1)
    user.add_role(RoleType.ACCOUNTANT, branch_id=branch2)
    
    # Получаем все разрешения
    permissions = user.get_all_permissions()
    print(f"Permissions: {permissions}")
    
    assert "global" in permissions
    assert RoleType.USER.value in permissions["global"]
    
    branch1_str = str(branch1)
    branch2_str = str(branch2)
    
    assert branch1_str in permissions
    assert branch2_str in permissions
    assert RoleType.MANAGER.value in permissions[branch1_str]
    assert RoleType.ACCOUNTANT.value in permissions[branch2_str]
    
    print("✅ Тест получения разрешений пройден")


def test_user_status(user):
    """Тест управления статусом пользователя"""
    print("\n=== Тест управления статусом ===")
    
    # Деактивируем
    user.deactivate()
    print(f"UserEntity active after deactivate: {user.is_active}")
    assert user.is_active is False
    
    # Проверяем исключение
    try:
        user.ensure_active()
        print("❌ Должно было быть исключение")
    except UserEntityNotActiveError as e:
        print(f"✓ Правильное исключение: {e}")
    
    # Активируем
    user.activate()
    print(f"UserEntity active after activate: {user.is_active}")
    assert user.is_active is True
    
    # Подтверждаем email
    user.verify_email()
    print(f"Email verified: {user.is_email_verified}")
    assert user.is_email_verified is True
    
    # Обновляем последний вход
    old_last_login = user.last_login_at
    user.update_last_login()
    print(f"Last login updated: {user.last_login_at}")
    assert user.last_login_at != old_last_login
    
    print("✅ Тест управления статусом пройден")


def test_role_requirements():
    """Тест требований к ролям"""
    print("\n=== Тест требований к ролям ===")
    
    # Создаем свежего пользователя для этого теста
    user = create_test_user(email="requirements@example.com")
    print(f"Создан пользователь с базовыми ролями: {[r.role_type.value for r in user.roles]}")
    
    branch_id = uuid4()
    print(f"Branch ID: {branch_id}")
    
    # Добавляем роль MANAGER
    user.add_role(RoleType.MANAGER, branch_id=branch_id)
    print(f"Добавлена роль MANAGER")
    
    # Должно пройти - роль MANAGER есть
    try:
        user.require_role(RoleType.MANAGER, branch_id)
        print("✓ require_role с правильной ролью прошла")
    except InsufficientPermissionsError:
        print("❌ Не должно быть исключения")
    
    # Должно выбросить исключение - роли ADMIN нет в этом филиале
    try:
        user.require_role(RoleType.ADMIN, branch_id)
        print("❌ Должно было быть исключение для ADMIN")
    except InsufficientPermissionsError as e:
        print(f"✓ Правильное исключение для ADMIN: {e}")
    
    # Проверка any_role - должна пройти, так как MANAGER есть в списке
    try:
        user.require_any_role([RoleType.ADMIN, RoleType.MANAGER], branch_id)
        print("✓ require_any_role с MANAGER в списке прошла")
    except InsufficientPermissionsError:
        print("❌ Не должно быть исключения для any_role с MANAGER")
    
    # Проверка any_role - должна выбросить исключение, так как нужных ролей нет
    try:
        user.require_any_role([RoleType.ADMIN, RoleType.OWNER], branch_id)
        print("❌ Должно было быть исключение для any_role с ADMIN/OWNER")
    except InsufficientPermissionsError as e:
        print(f"✓ Правильное исключение для any_role: {e}")
    
    # Добавляем глобальную роль ADMIN
    user.add_role(RoleType.ADMIN)
    print(f"Добавлена глобальная роль ADMIN")
    
    # Проверка с глобальной ролью
    try:
        user.require_role(RoleType.ADMIN)  # без branch_id
        print("✓ require_role с глобальной ролью ADMIN прошла")
    except InsufficientPermissionsError:
        print("❌ Не должно быть исключения для глобальной роли")
    
    # Проверка, что глобальная роль работает и в филиале
    try:
        user.require_role(RoleType.ADMIN, branch_id)
        print("✓ require_role с глобальной ролью ADMIN в филиале прошла")
    except InsufficientPermissionsError:
        print("❌ Глобальная роль должна работать в филиале")
    
    print("✅ Тест требований к ролям пройден")


def test_password_validation():
    """Тест валидации паролей"""
    print("\n=== Тест валидации паролей ===")
    
    # Тест слабого пароля
    is_valid, issues = PasswordValidationService.validate_password_strength("weak")
    print(f"Пароль 'weak' валидный: {is_valid}")
    print(f"Проблемы: {issues}")
    assert is_valid is False
    assert len(issues) > 0
    
    # Тест сильного пароля
    strong_password = "StrongP@ssw0rd123"
    is_valid, issues = PasswordValidationService.validate_password_strength(strong_password)
    print(f"Пароль '{strong_password}' валидный: {is_valid}")
    print(f"Проблемы: {issues}")
    assert is_valid is True
    assert len(issues) == 0
    
    # Тест генерации временного пароля
    temp_password = PasswordValidationService.generate_temporary_password()
    print(f"Сгенерированный пароль: {temp_password}")
    
    # Проверяем, что сгенерированный пароль валидный
    is_valid, issues = PasswordValidationService.validate_password_strength(temp_password)
    assert is_valid is True
    
    print("✅ Тест валидации паролей пройден")


def test_password_value_object():
    """Тест Value Object Password"""
    print("\n=== Тест Password Value Object ===")
    
    # Тест PasswordHash
    print("Тест PasswordHash:")
    
    # Валидный хеш
    valid_hash = get_valid_password_hash()
    try:
        password_hash = PasswordHash(valid_hash)
        print(f"✓ Валидный хеш создан: {password_hash.value[:20]}...")
    except ValueError as e:
        print(f"❌ Ошибка: {e}")
    
    # Невалидный хеш (слишком короткий)
    try:
        password_hash = PasswordHash("short")
        print("❌ Должно быть исключение для короткого хеша")
    except ValueError as e:
        print(f"✓ Правильное исключение для короткого хеша: {e}")
    
    # Пустой хеш
    try:
        password_hash = PasswordHash("")
        print("❌ Должно быть исключение для пустого хеша")
    except ValueError as e:
        print(f"✓ Правильное исключение для пустого хеша: {e}")
    
    # Тест RawPassword
    print("\nТест RawPassword:")
    
    # Слишком короткий
    try:
        raw = RawPassword("short")
        print("❌ Должно быть исключение для короткого пароля")
    except ValueError as e:
        print(f"✓ Правильное исключение: {e}")
    
    # Без заглавной буквы
    try:
        raw = RawPassword("password123!")
        print("❌ Должно быть исключение (нет заглавной)")
    except ValueError as e:
        print(f"✓ Правильное исключение: {e}")
    
    # Без цифры
    try:
        raw = RawPassword("Password!")
        print("❌ Должно быть исключение (нет цифры)")
    except ValueError as e:
        print(f"✓ Правильное исключение: {e}")
    
    # Без спецсимвола
    try:
        raw = RawPassword("Password123")
        print("❌ Должно быть исключение (нет спецсимвола)")
    except ValueError as e:
        print(f"✓ Правильное исключение: {e}")
    
    # Валидный пароль
    try:
        raw = RawPassword("StrongP@ssw0rd")
        print(f"✓ Валидный пароль создан: {raw}")
    except ValueError as e:
        print(f"❌ Ошибка: {e}")
    
    # Тест строкового представления (должно скрывать пароль)
    raw = RawPassword("StrongP@ssw0rd")
    print(f"Строковое представление: {raw}")
    assert str(raw) == "********"
    
    print("✅ Тест Password Value Object пройден")


def test_email_value_object():
    """Тест Value Object Email"""
    print("\n=== Тест Email Value Object ===")
    
    # Валидные email
    valid_emails = [
        "test@example.com",
        "user.name@domain.co.uk",
        "user+tag@example.org",
        "simple@example.com",
        "very.common@example.com",
        "disposable.style.email.with+symbol@example.com"
    ]
    
    for email_str in valid_emails:
        try:
            email = Email(email_str)
            print(f"✓ Валидный email: {email}")
            # Проверяем свойства
            assert email.value == email_str
            assert '@' in email.value
            assert email.domain  # домен не пустой
            assert email.local_part  # локальная часть не пустая
            print(f"  - Локальная часть: '{email.local_part}'")
            print(f"  - Домен: '{email.domain}'")
        except ValueError as e:
            print(f"❌ Не должно быть ошибки для {email_str}: {e}")
    
    # Невалидные email
    invalid_emails = [
        "test@",  # нет домена
        "@domain.com",  # нет локальной части
        "test@domain",  # нет точки в домене
        "test@.com",  # домен начинается с точки
        "test@domain.",  # домен заканчивается точкой
        "",  # пустой
        "a" * 300 + "@domain.com",  # слишком длинный
        "plainaddress",  # нет @
        "#@%^%#$@#$@#.com",  # спецсимволы
        "test@domain..com",  # двойная точка
        "test@-domain.com",  # домен начинается с дефиса
        "test@domain.c",  # домен верхнего уровня слишком короткий
    ]
    
    for email_str in invalid_emails:
        try:
            email = Email(email_str)
            print(f"❌ Должно быть исключение для '{email_str}', но создано: {email}")
        except ValueError as e:
            print(f"✓ Правильное исключение для '{email_str}': {e}")
    
    # Тест иммутабельности
    print("\nТест иммутабельности:")
    email = Email("test@example.com")
    try:
        # Попытка изменить значение (должна быть ошибка, так как frozen=True)
        email.value = "new@example.com"
        print("❌ Должна быть ошибка при изменении")
    except Exception as e:
        print(f"✓ Нельзя изменить значение: {type(e).__name__}")
    
    # Тест сравнения
    print("\nТест сравнения:")
    email1 = Email("test@example.com")
    email2 = Email("test@example.com")
    email3 = Email("other@example.com")
    
    print(f"email1 == email2: {email1 == email2} (должно быть True)")
    print(f"email1 == email3: {email1 == email3} (должно быть False)")
    
    assert email1 == email2
    assert email1 != email3
    
    # Тест хеширования (для использования в словарях)
    print("\nТест хеширования:")
    email_dict = {email1: "user1", email3: "user2"}
    print(f"email_dict[email1] = {email_dict[email1]}")
    assert email_dict[email1] == "user1"
    assert email_dict[email3] == "user2"
    
    print("✅ Тест Email Value Object пройден")


def test_authorization_service():
    """Тест сервиса авторизации"""
    print("\n=== Тест сервиса авторизации ===")
    
    # Создаем свежего пользователя ТОЛЬКО с ролью USER (без других ролей)
    regular_user = create_test_user(email="regular@example.com")
    print(f"Создан обычный пользователь с ролями: {[r.role_type.value for r in regular_user.roles]}")
    
    # Создаем другого пользователя
    other_user = create_test_user(email="other@example.com")
    print(f"Другой пользователь с ролями: {[r.role_type.value for r in other_user.roles]}")
    
    # Проверяем can_manage_user (без специальных ролей - только USER)
    can_manage = AuthorizationService.can_manage_user(regular_user, other_user)
    print(f"Обычный пользователь (только USER) может управлять другим: {can_manage}")
    assert can_manage is False, "Обычный пользователь НЕ должен управлять другими"
    print("✓ Обычный пользователь не может управлять другими (правильно)")
    
    # Проверяем can_assign_role (без специальных ролей)
    can_assign = AuthorizationService.can_assign_role(regular_user, other_user, RoleType.MANAGER)
    print(f"Обычный пользователь может назначать роли: {can_assign}")
    assert can_assign is False, "Обычный пользователь НЕ должен назначать роли"
    print("✓ Обычный пользователь не может назначать роли (правильно)")
    
    # Создаем пользователя с ролью ADMIN
    print("\n--- Создаем пользователя с ролью ADMIN ---")
    admin_user = create_test_user_with_role(RoleType.ADMIN, email="admin@example.com")
    print(f"ADMIN пользователь с ролями: {[r.role_type.value for r in admin_user.roles]}")
    
    can_manage = AuthorizationService.can_manage_user(admin_user, other_user)
    print(f"ADMIN может управлять обычным пользователем: {can_manage}")
    assert can_manage is True, "ADMIN должен управлять обычным пользователем"
    print("✓ ADMIN может управлять обычным пользователем (правильно)")
    
    # Проверяем can_assign_role для ADMIN
    can_assign = AuthorizationService.can_assign_role(admin_user, other_user, RoleType.MANAGER)
    print(f"ADMIN может назначить роль MANAGER: {can_assign}")
    assert can_assign is True, "ADMIN должен назначать роль MANAGER"
    print("✓ ADMIN может назначать роль MANAGER (правильно)")
    
    # Проверяем, что ADMIN не может назначить SUPER_ADMIN
    can_assign_super = AuthorizationService.can_assign_role(admin_user, other_user, RoleType.SUPER_ADMIN)
    print(f"ADMIN может назначить SUPER_ADMIN: {can_assign_super}")
    assert can_assign_super is False, "ADMIN НЕ должен назначать SUPER_ADMIN"
    print("✓ ADMIN не может назначить SUPER_ADMIN (правильно)")
    
    # Проверяем validate_role_assignment
    try:
        AuthorizationService.validate_role_assignment(
            admin_user, other_user, RoleType.MANAGER, branch_id=uuid4()
        )
        print("✓ Валидация назначения роли прошла успешно")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    
    # --- Создаем владельца (OWNER) ---
    print("\n--- Создаем владельца (OWNER) ---")
    branch_id = uuid4()
    owner_user = create_test_user_with_role(RoleType.OWNER, branch_id=branch_id, email="owner@example.com")
    print(f"OWNER пользователь с ролями: {[r.role_type.value for r in owner_user.roles]}")
    print(f"Филиал владельца: {branch_id}")

    # Создаем пользователя в том же филиале с ЛОКАЛЬНОЙ ролью
    branch_user = create_test_user(email="branch@example.com")
    branch_user.add_role(RoleType.MANAGER, branch_id=branch_id)
    print(f"Пользователь в филиале владельца с ролями: {[r.role_type.value for r in branch_user.roles]}")
    print(f"✓ У пользователя есть локальная роль MANAGER")

    # OWNER должен управлять пользователем с локальной ролью
    can_manage_owner = AuthorizationService.can_manage_user(owner_user, branch_user)
    assert can_manage_owner is True, "OWNER должен управлять пользователем с локальной ролью"
    print("✓ OWNER управляет пользователем с локальной ролью (правильно)")

    # Создаем пользователя в другом филиале (только глобальная USER)
    other_branch_user = create_test_user(email="other_branch@example.com")
    print(f"\nПользователь в другом филиале с ролями: {[r.role_type.value for r in other_branch_user.roles]}")
    print(f"✓ У пользователя только глобальная USER")

    # OWNER НЕ должен управлять пользователем без локальных ролей
    can_manage_other = AuthorizationService.can_manage_user(owner_user, other_branch_user)
    assert can_manage_other is False, "OWNER НЕ должен управлять пользователем без локальных ролей"
    print("✓ OWNER не управляет пользователем без локальных ролей (правильно)")
    
    # --- Создаем супер-админа ---
    print("\n--- Создаем SUPER_ADMIN ---")
    super_admin = create_test_user_with_role(RoleType.SUPER_ADMIN, email="super@example.com")
    print(f"SUPER_ADMIN пользователь с ролями: {[r.role_type.value for r in super_admin.roles]}")
    
    # SUPER_ADMIN может управлять всеми
    can_manage_super = AuthorizationService.can_manage_user(super_admin, admin_user)
    print(f"SUPER_ADMIN может управлять ADMIN: {can_manage_super}")
    assert can_manage_super is True, "SUPER_ADMIN должен управлять ADMIN"
    
    can_manage_super = AuthorizationService.can_manage_user(super_admin, owner_user)
    print(f"SUPER_ADMIN может управлять OWNER: {can_manage_super}")
    assert can_manage_super is True, "SUPER_ADMIN должен управлять OWNER"
    
    can_manage_super = AuthorizationService.can_manage_user(super_admin, regular_user)
    print(f"SUPER_ADMIN может управлять обычным пользователем: {can_manage_super}")
    assert can_manage_super is True, "SUPER_ADMIN должен управлять обычным пользователем"
    print("✓ SUPER_ADMIN может управлять всеми (правильно)")
    
    print("✅ Тест сервиса авторизации пройден")


def test_role_hierarchy_and_inheritance():
    """Тест иерархии и наследования ролей"""
    print("\n=== Тест иерархии ролей ===")
    
    # Создаем пользователей с разными ролями используя хелперы
    super_admin = create_test_user_with_role(RoleType.SUPER_ADMIN, email="super@example.com")
    admin = create_test_user_with_role(RoleType.ADMIN, email="admin@example.com")
    
    branch_id = uuid4()
    owner = create_test_user_with_role(RoleType.OWNER, branch_id=branch_id, email="owner@example.com")
    
    print(f"Super Admin roles: {[r.role_type.value for r in super_admin.roles]}")
    print(f"Admin roles: {[r.role_type.value for r in admin.roles]}")
    print(f"Owner roles: {[r.role_type.value for r in owner.roles]}")
    
    # Тест сервиса авторизации
    print("\nПроверка прав на управление пользователями:")
    
    # Super Admin может управлять всеми
    assert AuthorizationService.can_manage_user(super_admin, admin) is True
    assert AuthorizationService.can_manage_user(super_admin, owner) is True
    print("✓ Super Admin может управлять всеми")
    
    # Admin может управлять всеми, кроме Super Admin
    assert AuthorizationService.can_manage_user(admin, super_admin) is False
    assert AuthorizationService.can_manage_user(admin, owner) is True
    print("✓ Admin может управлять всеми, кроме Super Admin")
    
    # Owner и пользователь с локальной ролью в его филиале
    local_user = create_test_user(email="local@example.com")
    local_user.add_role(RoleType.MANAGER, branch_id=branch_id)
    
    # Owner должен управлять local_user (есть локальная роль)
    can_manage = AuthorizationService.can_manage_user(owner, local_user)
    assert can_manage is True, "Owner должен управлять пользователем с локальной ролью"
    print("✓ Owner управляет пользователем с локальной ролью")

    # Создаем пользователя только с глобальной USER (не в филиале)
    global_user = create_test_user(email="global@example.com")
    
    # Owner НЕ должен управлять global_user (нет локальных ролей)
    can_manage_global = AuthorizationService.can_manage_user(owner, global_user)
    assert can_manage_global is False, "Owner НЕ должен управлять пользователем только с глобальной USER"
    print("✓ Owner не управляет пользователем только с глобальной USER")

    print("✅ Тест иерархии ролей пройден")


def test_role_assignment_validation():
    """Тест валидации назначения ролей"""
    print("\n=== Тест валидации назначения ролей ===")
    
    # Создаем пользователей с правильными хешами
    super_admin = create_test_user_with_role(RoleType.SUPER_ADMIN, email="super@example.com")
    admin = create_test_user_with_role(RoleType.ADMIN, email="admin@example.com")
    target_user = create_test_user(email="target@example.com")
    
    branch_id = uuid4()
    
    print("Проверка назначения ролей:")
    
    # Super Admin может назначить любую роль
    try:
        AuthorizationService.validate_role_assignment(
            super_admin, target_user, RoleType.SUPER_ADMIN
        )
        print("✓ Super Admin может назначить SUPER_ADMIN")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    
    # Admin не может назначить SUPER_ADMIN
    try:
        AuthorizationService.validate_role_assignment(
            admin, target_user, RoleType.SUPER_ADMIN
        )
        print("❌ Admin НЕ должен мочь назначить SUPER_ADMIN")
    except InsufficientPermissionsError as e:
        print(f"✓ Admin не может назначить SUPER_ADMIN: {e}")
    
    # Admin может назначить ADMIN
    try:
        AuthorizationService.validate_role_assignment(
            admin, target_user, RoleType.ADMIN
        )
        print("✓ Admin может назначить ADMIN")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    
    # Проверка бизнес-ролей
    print("\nПроверка бизнес-ролей:")
    
    # Нельзя назначить бизнес-роль без филиала
    try:
        AuthorizationService.validate_role_assignment(
            admin, target_user, RoleType.MANAGER  # branch_id не указан
        )
        print("❌ Должна быть ошибка - нет branch_id")
    except RoleAssignmentError as e:
        print(f"✓ Правильная ошибка: {e}")
    
    # Нельзя назначить системную роль с филиалом
    try:
        AuthorizationService.validate_role_assignment(
            admin, target_user, RoleType.ADMIN, branch_id=branch_id
        )
        print("❌ Должна быть ошибка - системная роль с филиалом")
    except RoleAssignmentError as e:
        print(f"✓ Правильная ошибка: {e}")
    
    print("✅ Тест валидации назначения ролей пройден")


def test_role_uniqueness():
    """Тест уникальности ролей"""
    print("\n=== Тест уникальности ролей ===")
    
    user = create_test_user(email="unique@example.com")
    print(f"Создан пользователь с ролями: {[r.role_type.value for r in user.roles]}")
    
    branch_id = uuid4()
    
    # Тест 1: Попытка добавить дубликат глобальной роли
    print("\nТест 1: Дубликат глобальной роли USER")
    try:
        user.add_role(RoleType.USER)  # пытаемся добавить еще одну глобальную USER
        print("❌ Должна быть ошибка при добавлении дубликата глобальной USER")
    except ValueError as e:
        print(f"✓ Правильная ошибка: {e}")
    
    # Тест 2: Попытка добавить локальную USER (когда глобальная уже есть)
    print("\nТест 2: Локальная роль USER при существующей глобальной")
    try:
        user.add_role(RoleType.USER, branch_id=branch_id)
        print("❌ Должна быть ошибка при добавлении локальной USER")
    except ValueError as e:
        print(f"✓ Правильная ошибка: {e}")
    
    # Тест 3: Добавление другой глобальной роли
    print("\nТест 3: Добавление глобальной роли ADMIN")
    try:
        user.add_role(RoleType.ADMIN)
        print(f"✓ Глобальная роль ADMIN добавлена")
        assert user.has_role(RoleType.ADMIN) is True
    except ValueError as e:
        print(f"❌ Ошибка: {e}")
    
    # Тест 4: Добавление локальной роли MANAGER
    print("\nТест 4: Добавление локальной роли MANAGER")
    try:
        user.add_role(RoleType.MANAGER, branch_id=branch_id)
        print(f"✓ Локальная роль MANAGER добавлена в филиал {branch_id}")
        assert user.has_role(RoleType.MANAGER, branch_id) is True
    except ValueError as e:
        print(f"❌ Ошибка: {e}")
    
    # Тест 5: Проверка количества ролей
    print("\nТест 5: Проверка количества ролей")
    print(f"Все роли пользователя: {[f'{r.role_type.value}({r.branch_id})' for r in user.roles]}")
    assert len(user.roles) == 3  # USER (global), ADMIN (global), MANAGER (local)
    print(f"✓ Всего ролей: {len(user.roles)} (правильно)")
    
    print("\n✅ Тест уникальности ролей пройден")


def test_edge_cases():
    """Тест граничных случаев"""
    print("\n=== Тест граничных случаев ===")
    
    user = create_test_user()
    branch_id = uuid4()
    
    # Тест 1: Попытка добавить дубликат роли
    print("Тест 1: Дубликат роли")
    user.add_role(RoleType.MANAGER, branch_id=branch_id)
    try:
        user.add_role(RoleType.MANAGER, branch_id=branch_id)
        print("❌ Должна быть ошибка при добавлении дубликата")
    except ValueError as e:
        print(f"✓ Правильная ошибка: {e}")
    
    # Тест 2: Попытка удалить базовую роль
    print("\nТест 2: Удаление базовой роли")
    try:
        user.remove_role(RoleType.USER)
        print("❌ Должна быть ошибка при удалении USER")
    except ValueError as e:
        print(f"✓ Правильная ошибка: {e}")
    
    # Тест 3: Попытка добавить локальную USER (когда глобальная уже есть)
    print("\nТест 3: Добавление локальной USER при существующей глобальной")
    try:
        user.add_role(RoleType.USER, branch_id=branch_id)
        print("❌ Должна быть ошибка при добавлении локальной USER")
    except ValueError as e:
        print(f"✓ Правильная ошибка: {e}")
    
    # Тест 4: Проверка роли в несуществующем филиале
    print("\nТест 4: Проверка в несуществующем филиале")
    fake_branch = uuid4()
    assert user.has_role(RoleType.MANAGER, fake_branch) is False
    print(f"✓ Роль MANAGER не найдена в филиале {fake_branch}")
    
    # Тест 5: get_roles_in_branch с несуществующим филиалом
    print("\nТест 5: get_roles_in_branch с несуществующим филиалом")
    roles = user.get_roles_in_branch(fake_branch)
    print(f"Роли в несуществующем филиале: {[r.value for r in roles]}")
    assert RoleType.USER in roles  # Глобальная роль должна быть
    assert len(roles) == 1
    print("✓ Глобальные роли доступны даже в несуществующем филиале")
    
    print("\n✅ Тест граничных случаев пройден")


def main():
    """Главная функция тестирования"""
    print("=" * 50)
    print("ТЕСТИРОВАНИЕ ДОМЕННОГО СЛОЯ")
    print("=" * 50)
    
    try:
        # Создаем пользователя для тестов, которые его требуют
        user = test_user_creation()
        
        # Запускаем все тесты
        test_role_management(user)
        test_global_roles_in_branches(user)
        test_permissions(user)
        test_user_status(user)
        
        # Этот тест создает своего пользователя
        test_role_requirements()  # убрали передачу user
        
        test_password_validation()
        test_password_value_object()
        test_email_value_object()
        test_role_uniqueness()
        
        # Эти тесты создают своих пользователей
        test_authorization_service()
        test_role_hierarchy_and_inheritance()
        test_role_assignment_validation()
        test_edge_cases()
        
        print("\n" + "=" * 50)
        print("✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n❌ Ошибка при тестировании: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()