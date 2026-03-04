import aiosmtplib

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Environment, FileSystemLoader
from typing import Optional

from application.interfaces.email_sender import EmailSender
from infrastructure.config import settings


class SMTPEmailSender(EmailSender):
    """Отправка email через SMTP с Jinja2 шаблонами"""

    def __init__(self, template_dir: str = "templates/email"):
        self.host = settings.SMTP_HOST
        self.port = settings.SMTP_PORT
        self.username = settings.SMTP_USERNAME
        self.password = settings.SMTP_PASSWORD
        self.from_email = settings.SMTP_FROM_EMAIL
        self.from_name = settings.SMTP_FROM_NAME
        self.use_tls = settings.SMTP_USE_TLS
        self.frontend_url = settings.FRONTEND_URL
        self.verify_url = settings.VERIFY_EMAIL_URL
        self.reset_url = settings.RESET_PASSWORD_URL
        
        # Настройка Jinja2 для шаблонов
        self.template_env = Environment(
            loader=FileSystemLoader(template_dir)
        )

    async def send_verification_email(self, to_email: str, full_name: str, 
                                      verification_token: str) -> None:
        """Отправить письмо для подтверждения email"""
        template = self.template_env.get_template("verification_email.html")
        verification_link = f"{self.frontend_url}{self.verify_url}?token={verification_token}"
        
        html_content = template.render(
            full_name=full_name,
            verification_link=verification_link,
            expires_in=settings.JWT_EMAIL_VERIFY_EXPIRE_HOURS
        )
        
        await self._send_email(
            to_email=to_email,
            subject="Подтвердите ваш email",
            html_content=html_content
        )

    async def send_password_reset_email(self, to_email: str, full_name: str,
                                       reset_token: str) -> None:
        """Отправить письмо для сброса пароля"""
        template = self.template_env.get_template("password_reset_email.html")
        reset_link = f"{self.frontend_url}{self.reset_url}?token={reset_token}"
        
        html_content = template.render(
            full_name=full_name,
            reset_link=reset_link,
            expires_in=settings.JWT_PASSWORD_RESET_EXPIRE_HOURS
        )
        
        await self._send_email(
            to_email=to_email,
            subject="Сброс пароля",
            html_content=html_content
        )

    async def send_welcome_email(self, to_email: str, full_name: str) -> None:
        """Отправить приветственное письмо"""
        template = self.template_env.get_template("welcome_email.html")
        
        html_content = template.render(full_name=full_name)
        
        await self._send_email(
            to_email=to_email,
            subject="Добро пожаловать!",
            html_content=html_content
        )

    async def _send_email(self, to_email: str, subject: str, 
                         html_content: str, cc: Optional[list] = None,
                         bcc: Optional[list] = None) -> None:
        """Базовый метод отправки email"""
        message = MIMEMultipart("alternative")
        message["From"] = f"{self.from_name} <{self.from_email}>"
        message["To"] = to_email
        message["Subject"] = subject
        
        if cc:
            message["Cc"] = ", ".join(cc)
        if bcc:
            message["Bcc"] = ", ".join(bcc)
        
        # Добавляем HTML версию
        part = MIMEText(html_content, "html")
        message.attach(part)
        
        # Отправляем
        await aiosmtplib.send(
            message,
            hostname=self.host,
            port=self.port,
            username=self.username,
            password=self.password,
            use_tls=self.use_tls
        )