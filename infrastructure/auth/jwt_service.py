from typing import Optional, Dict, Any, Tuple
from uuid import UUID
from datetime import datetime, timedelta, timezone
import jwt

from application.interfaces.token_service import TokenService
from infrastructure.config import settings


class JWTTokenService(TokenService):
    """Реализация JWT токенов"""

    def __init__(self):
        self.secret_key = settings.JWT_SECRET_KEY
        self.algorithm = settings.JWT_ALGORITHM
        self.access_token_expire = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        self.refresh_token_expire = timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
        self.email_verification_expire = timedelta(hours=settings.JWT_EMAIL_VERIFY_EXPIRE_HOURS)
        self.password_reset_expire = timedelta(hours=settings.JWT_PASSWORD_RESET_EXPIRE_HOURS)

    def create_access_token(self, user_id: UUID, roles: list, 
                           permissions: dict = None) -> Tuple[str, int]:
        """Создание access token"""
        expires_at = datetime.now(timezone.utc) + self.access_token_expire
        payload = {
            'sub': str(user_id),
            'type': 'access',
            'roles': roles,
            'permissions': permissions or {},
            'exp': expires_at,
            'iat': datetime.now(timezone.utc)
        }
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return token, int(self.access_token_expire.total_seconds())

    def create_refresh_token(self, user_id: UUID) -> Tuple[str, int]:
        """Создание refresh token"""
        expires_at = datetime.now(timezone.utc) + self.refresh_token_expire
        payload = {
            'sub': str(user_id),
            'type': 'refresh',
            'exp': expires_at,
            'iat': datetime.now(timezone.utc)
        }
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return token, int(self.refresh_token_expire.total_seconds())

    def create_email_verification_token(self, user_id: UUID, email: str) -> str:
        """Создание токена для подтверждения email"""
        expires_at = datetime.now(timezone.utc) + self.email_verification_expire
        payload = {
            'user_id': str(user_id),
            'email': email,
            'type': 'email_verification',
            'exp': expires_at,
            'iat': datetime.now(timezone.utc)
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def create_password_reset_token(self, user_id: UUID, email: str) -> str:
        """Создание токена для сброса пароля"""
        expires_at = datetime.now(timezone.utc) + self.password_reset_expire
        payload = {
            'user_id': str(user_id),
            'email': email,
            'type': 'password_reset',
            'exp': expires_at,
            'iat': datetime.now(timezone.utc)
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def verify_access_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Проверка access token"""
        try:
            payload = jwt.decode(
                token, 
                self.secret_key, 
                algorithms=[self.algorithm]
            )
            if payload.get('type') != 'access':
                return None
            return payload
        except jwt.PyJWTError:
            return None

    def verify_refresh_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Проверка refresh token"""
        try:
            payload = jwt.decode(
                token, 
                self.secret_key, 
                algorithms=[self.algorithm]
            )
            if payload.get('type') != 'refresh':
                return None
            return payload
        except jwt.PyJWTError:
            return None

    def verify_email_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Проверка токена подтверждения email"""
        try:
            payload = jwt.decode(
                token, 
                self.secret_key, 
                algorithms=[self.algorithm]
            )
            if payload.get('type') != 'email_verification':
                return None
            return payload
        except jwt.PyJWTError:
            return None

    def verify_password_reset_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Проверка токена сброса пароля"""
        try:
            payload = jwt.decode(
                token, 
                self.secret_key, 
                algorithms=[self.algorithm]
            )
            if payload.get('type') != 'password_reset':
                return None
            return payload
        except jwt.PyJWTError:
            return None