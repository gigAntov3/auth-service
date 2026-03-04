import pytest
from uuid import uuid4, UUID
from datetime import datetime, timedelta
from infrastructure.auth.jwt_service import JWTTokenService
from infrastructure.config import settings


class TestJWTTokenService:
    """Тесты для JWT сервиса"""

    def setup_method(self):
        # Сохраняем оригинальные настройки
        self.original_secret = settings.JWT_SECRET_KEY
        settings.JWT_SECRET_KEY = "test_secret_key_for_jwt_tests"
        self.token_service = JWTTokenService()

    def teardown_method(self):
        # Восстанавливаем оригинальные настройки
        settings.JWT_SECRET_KEY = self.original_secret

    def test_create_access_token(self):
        """Тест создания access token"""
        user_id = uuid4()
        roles = ["user", "admin"]
        permissions = {"global": ["user", "admin"]}
        
        token, expires_in = self.token_service.create_access_token(
            user_id=user_id,
            roles=roles,
            permissions=permissions
        )
        
        assert token is not None
        assert expires_in == settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
        assert isinstance(token, str)

    def test_verify_valid_access_token(self):
        """Тест проверки валидного access token"""
        user_id = uuid4()
        roles = ["user", "admin"]
        
        token, _ = self.token_service.create_access_token(
            user_id=user_id,
            roles=roles
        )
        
        payload = self.token_service.verify_access_token(token)
        assert payload is not None
        assert payload['sub'] == str(user_id)
        assert payload['type'] == 'access'
        assert payload['roles'] == roles

    def test_verify_expired_access_token(self):
        """Тест проверки истекшего access token"""
        # Создаем токен с истекшим сроком
        import jwt
        from datetime import datetime, timedelta, timezone
        
        expired_payload = {
            'sub': str(uuid4()),
            'type': 'access',
            'exp': datetime.now(timezone.utc) - timedelta(seconds=1),
            'iat': datetime.now(timezone.utc) - timedelta(hours=1)
        }
        
        expired_token = jwt.encode(
            expired_payload, 
            settings.JWT_SECRET_KEY, 
            algorithm=settings.JWT_ALGORITHM
        )
        
        payload = self.token_service.verify_access_token(expired_token)
        assert payload is None

    def test_verify_invalid_access_token(self):
        """Тест проверки неверного access token"""
        payload = self.token_service.verify_access_token("invalid.token.here")
        assert payload is None

    def test_create_refresh_token(self):
        """Тест создания refresh token"""
        user_id = uuid4()
        
        token, expires_in = self.token_service.create_refresh_token(user_id)
        
        assert token is not None
        assert expires_in == settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
        assert isinstance(token, str)

    def test_verify_valid_refresh_token(self):
        """Тест проверки валидного refresh token"""
        user_id = uuid4()
        
        token, _ = self.token_service.create_refresh_token(user_id)
        
        payload = self.token_service.verify_refresh_token(token)
        assert payload is not None
        assert payload['sub'] == str(user_id)
        assert payload['type'] == 'refresh'

    def test_create_email_verification_token(self):
        """Тест создания токена подтверждения email"""
        user_id = uuid4()
        email = "test@example.com"
        
        token = self.token_service.create_email_verification_token(user_id, email)
        
        assert token is not None
        assert isinstance(token, str)

    def test_verify_valid_email_token(self):
        """Тест проверки валидного токена подтверждения email"""
        user_id = uuid4()
        email = "test@example.com"
        
        token = self.token_service.create_email_verification_token(user_id, email)
        
        payload = self.token_service.verify_email_token(token)
        assert payload is not None
        assert payload['user_id'] == str(user_id)
        assert payload['email'] == email
        assert payload['type'] == 'email_verification'

    def test_create_password_reset_token(self):
        """Тест создания токена сброса пароля"""
        user_id = uuid4()
        email = "test@example.com"
        
        token = self.token_service.create_password_reset_token(user_id, email)
        
        assert token is not None
        assert isinstance(token, str)

    def test_verify_valid_password_reset_token(self):
        """Тест проверки валидного токена сброса пароля"""
        user_id = uuid4()
        email = "test@example.com"
        
        token = self.token_service.create_password_reset_token(user_id, email)
        
        payload = self.token_service.verify_password_reset_token(token)
        assert payload is not None
        assert payload['user_id'] == str(user_id)
        assert payload['email'] == email
        assert payload['type'] == 'password_reset'

    def test_wrong_token_type(self):
        """Тест, что access token не работает как refresh token"""
        user_id = uuid4()
        
        access_token, _ = self.token_service.create_access_token(user_id, ["user"])
        refresh_payload = self.token_service.verify_refresh_token(access_token)
        assert refresh_payload is None
        
        refresh_token, _ = self.token_service.create_refresh_token(user_id)
        access_payload = self.token_service.verify_access_token(refresh_token)
        assert access_payload is None