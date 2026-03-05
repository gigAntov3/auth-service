import logging
from typing import Optional
from application.interfaces.services.sms_service import SmsService

class MockSMSService(SmsService):
    """Заглушка для SMS сервиса (не требует реальной отправки)"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.sent_sms = []  # для тестирования можно хранить отправленные
    
    async def send_verification_code(self, to_phone: str, code: str) -> None:
        """Отправка кода верификации по SMS (заглушка)"""
        self.logger.info(f"📱 [MOCK] SMS verification to {to_phone}: {code}")
        self.sent_sms.append({
            'to': to_phone,
            'type': 'verification',
            'code': code
        })
    
    async def send_invitation(self, to_phone: str, company_name: str, token: str) -> None:
        """Отправка приглашения по SMS (заглушка)"""
        message = f"You're invited to join {company_name}! Use token: {token}"
        self.logger.info(f"📱 [MOCK] SMS invitation to {to_phone}: {message}")
        self.sent_sms.append({
            'to': to_phone,
            'type': 'invitation',
            'company': company_name,
            'token': token
        })
    
    async def send_notification(self, to_phone: str, message: str) -> None:
        """Отправка уведомления по SMS (заглушка)"""
        self.logger.info(f"📱 [MOCK] SMS notification to {to_phone}: {message}")
        self.sent_sms.append({
            'to': to_phone,
            'type': 'notification',
            'message': message
        })
    
    async def _send_sms(self, to_phone: str, message: str) -> None:
        """Заглушка для отправки SMS"""
        self.logger.info(f"📱 [MOCK] SMS to {to_phone}: {message}")
        self.sent_sms.append({
            'to': to_phone,
            'message': message
        })