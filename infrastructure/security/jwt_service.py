from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import jwt
from jwt.exceptions import PyJWTError

from application.interfaces.services.token_service import TokenService
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
    
    def create_access_token(self, user_id: str) -> str:
        now = datetime.now()
        expire = now + timedelta(minutes=self.access_token_expire_minutes)
        payload = {
            "sub": user_id,
            "exp": int(expire.timestamp()),
            "iat": int(now.timestamp()),
            "type": "access"
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        
    def verify_access_token(self, token: str) -> Dict[str, Any]:
        """Verify and decode JWT access token"""
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm]
            )

            print(payload)
            
            # Check token type
            if payload.get("type") != "access":
                raise InvalidTokenError("Invalid token type")
            
            return payload
        except jwt.ExpiredSignatureError:
            raise InvalidTokenError("Token has expired")
        except jwt.InvalidTokenError as e:
            raise InvalidTokenError(f"Invalid token: {str(e)}")
    
    def create_refresh_token(self, user_id: str) -> str:
        now = datetime.utcnow()
        expire = now + timedelta(days=self.refresh_token_expire_days)
        payload = {
            "sub": user_id,
            "exp": int(expire.timestamp()),
            "iat": int(now.timestamp()),
            "type": "refresh"
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def verify_refresh_token(self, token: str) -> Dict[str, Any]:
        """Verify and decode JWT refresh token"""
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm]
            )
            if payload.get("type") != "refresh":
                raise InvalidTokenError("Invalid token type")
            return payload
        except jwt.ExpiredSignatureError:
            raise InvalidTokenError("Token has expired")
        except jwt.InvalidTokenError as e:
            raise InvalidTokenError(f"Invalid token: {str(e)}")