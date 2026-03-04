import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from infrastructure.email.smtp_sender import SMTPEmailSender


class TestSMTPEmailSender:
    """Тесты для SMTP отправителя email"""

    @pytest.fixture
    def email_sender(self, monkeypatch):
        """Фикстура для email отправителя с моком"""
        # Мокаем настройки
        monkeypatch.setenv("SMTP_HOST", "smtp.test.com")
        monkeypatch.setenv("SMTP_PORT", "587")
        monkeypatch.setenv("SMTP_USERNAME", "test@test.com")
        monkeypatch.setenv("SMTP_PASSWORD", "password")
        monkeypatch.setenv("SMTP_FROM_EMAIL", "noreply@test.com")
        monkeypatch.setenv("SMTP_FROM_NAME", "Test Service")
        monkeypatch.setenv("FRONTEND_URL", "http://localhost:3000")
        monkeypatch.setenv("VERIFY_EMAIL_URL", "/verify-email")
        monkeypatch.setenv("RESET_PASSWORD_URL", "/reset-password")
        
        # Перезагружаем настройки
        from importlib import reload
        import infrastructure.config
        reload(infrastructure.config)
        
        # Создаем отправителя с моком шаблонов
        with patch('infrastructure.email.smtp_sender.Environment') as mock_env:
            mock_template = MagicMock()
            mock_template.render.return_value = "<html>Test Email</html>"
            mock_env.return_value.get_template.return_value = mock_template
            
            sender = SMTPEmailSender(template_dir="fake/path")
            sender._send_email = AsyncMock()  # мокаем отправку
            yield sender

    @pytest.mark.asyncio
    async def test_send_verification_email(self, email_sender):
        """Тест отправки письма для подтверждения email"""
        to_email = "user@example.com"
        full_name = "Test User"
        token = "verification_token_123"
        
        await email_sender.send_verification_email(to_email, full_name, token)
        
        email_sender._send_email.assert_called_once()
        args = email_sender._send_email.call_args[1]
        assert args['to_email'] == to_email
        assert args['subject'] == "Подтвердите ваш email"
        assert "html_content" in args

    @pytest.mark.asyncio
    async def test_send_password_reset_email(self, email_sender):
        """Тест отправки письма для сброса пароля"""
        to_email = "user@example.com"
        full_name = "Test User"
        token = "reset_token_123"
        
        await email_sender.send_password_reset_email(to_email, full_name, token)
        
        email_sender._send_email.assert_called_once()
        args = email_sender._send_email.call_args[1]
        assert args['to_email'] == to_email
        assert args['subject'] == "Сброс пароля"
        assert "html_content" in args

    @pytest.mark.asyncio
    async def test_send_welcome_email(self, email_sender):
        """Тест отправки приветственного письма"""
        to_email = "user@example.com"
        full_name = "Test User"
        
        await email_sender.send_welcome_email(to_email, full_name)
        
        email_sender._send_email.assert_called_once()
        args = email_sender._send_email.call_args[1]
        assert args['to_email'] == to_email
        assert args['subject'] == "Добро пожаловать!"
        assert "html_content" in args