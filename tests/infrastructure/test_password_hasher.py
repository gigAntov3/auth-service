import pytest
from infrastructure.auth.password_hasher import BcryptPasswordHasher


class TestBcryptPasswordHasher:
    """Тесты для хеширования паролей"""

    def setup_method(self):
        self.hasher = BcryptPasswordHasher(rounds=4)  # rounds=4 для быстрых тестов

    def test_hash_password(self):
        """Тест хеширования пароля"""
        password = "Test123!@#"
        hashed = self.hasher.hash(password)
        
        assert hashed != password
        assert len(hashed) > 20
        assert hashed.startswith("$2b$")

    def test_verify_correct_password(self):
        """Тест проверки правильного пароля"""
        password = "Test123!@#"
        hashed = self.hasher.hash(password)
        
        assert self.hasher.verify(password, hashed) is True

    def test_verify_wrong_password(self):
        """Тест проверки неправильного пароля"""
        password = "Test123!@#"
        wrong_password = "Wrong123!@#"
        hashed = self.hasher.hash(password)
        
        assert self.hasher.verify(wrong_password, hashed) is False

    def test_verify_empty_password(self):
        """Тест проверки пустого пароля"""
        hashed = self.hasher.hash("Test123!@#")
        
        assert self.hasher.verify("", hashed) is False

    def test_hash_same_password_different_results(self):
        """Тест, что один и тот же пароль дает разные хеши (из-за соли)"""
        password = "Test123!@#"
        hash1 = self.hasher.hash(password)
        hash2 = self.hasher.hash(password)
        
        assert hash1 != hash2
        assert self.hasher.verify(password, hash1) is True
        assert self.hasher.verify(password, hash2) is True