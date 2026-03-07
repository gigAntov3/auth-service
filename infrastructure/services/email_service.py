import logging
from typing import Optional
from application.interfaces.services.email_service import EmailService

class MockEmailService(EmailService):
    """Заглушка для email сервиса (не требует реальной отправки)"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    async def send_verification_code(self, to_email: str, code: str) -> None:
        """Отправка кода верификации (заглушка)"""
        print(f"\n\n\n📧 [MOCK] Verification code to {to_email}: {code}\n\n\n")
    
    async def send_invitation(self, to_email: str, company_name: str, invite_link: str) -> None:
        """Отправка приглашения (заглушка)"""
        self.logger.info(f"📧 [MOCK] Invitation to {to_email} for company '{company_name}': {invite_link}")
    
    async def send_password_reset(self, to_email: str, reset_link: str) -> None:
        """Отправка сброса пароля (заглушка)"""
        self.logger.info(f"📧 [MOCK] Password reset to {to_email}: {reset_link}")
    
    async def _send_email(self, to_email: str, subject: str, html_content: Optional[str] = None, text_content: Optional[str] = None) -> None:
        """Заглушка для отправки email"""
        self.logger.info(f"📧 [MOCK] Email to {to_email}")
        self.logger.info(f"   Subject: {subject}")
        if text_content:
            self.logger.info(f"   Text: {text_content[:100]}...")