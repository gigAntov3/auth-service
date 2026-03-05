from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import jwt
from jwt.exceptions import PyJWTError

from domain.interfaces.token_service import TokenService
from application.exceptions import InvalidTokenError

class JWTTokenService(TokenService):
    """JWT implementation of token service"""
    
    def __init__(
        self,
        secret_key: str,
        algorithm: str = "HS256",
        access_token_expire_minutes: int = 30,
        refresh_token_expire_days: int = 30
    ):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expire_minutes = access_token_expire_minutes
        self.refresh_token_expire_days = refresh_token_expire_days
    
    def create_access_token(self, payload: Dict[str, Any]) -> str:
        """Create JWT access token"""
        token_payload = {}

        for key, value in payload.items():
            # Превращаем value objects в строки, если нужно
            if hasattr(value, "value"):  # например Email.value
                token_payload[key] = value.value
            else:
                token_payload[key] = value

        # Add expiration
        now = datetime.utcnow()
        expire = now + timedelta(minutes=self.access_token_expire_minutes)
        token_payload["exp"] = int(expire.timestamp())  # обязательно int
        token_payload["iat"] = int(now.timestamp())     # обязательно int
        token_payload["type"] = "access"

        return jwt.encode(token_payload, self.secret_key, algorithm=self.algorithm)
    
    def verify_access_token(self, token: str) -> Dict[str, Any]:
        """Verify and decode JWT access token"""
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm]
            )
            
            # Check token type
            if payload.get("type") != "access":
                raise InvalidTokenError("Invalid token type")
            
            return payload
        except jwt.ExpiredSignatureError:
            raise InvalidTokenError("Token has expired")
        except jwt.InvalidTokenError as e:
            raise InvalidTokenError(f"Invalid token: {str(e)}")
    
    def generate_refresh_token(self) -> str:
        """Generate a random refresh token"""
        import secrets
        return secrets.token_urlsafe(32)
    
    def generate_invitation_token(self) -> str:
        """Generate a random invitation token"""
        import secrets
        return secrets.token_urlsafe(48)
    
    def create_refresh_token_payload(self, user_id: str) -> str:
        """Create JWT refresh token"""
        payload = {
            "sub": user_id,
            "exp": datetime.utcnow() + timedelta(days=self.refresh_token_expire_days),
            "iat": datetime.utcnow(),
            "type": "refresh"
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)