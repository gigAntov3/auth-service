from datetime import datetime
from typing import Optional, Tuple
from domain.entities.user import UserEntity
from domain.entities.refresh_token import RefreshTokenEntity
from domain.value_objects.credentials import Credentials
from domain.value_objects.role import Role
from domain.interfaces.password_hasher import PasswordHasher
from domain.interfaces.token_service import TokenService

class AuthDomainService:
    """Доменный сервис для аутентификации"""
    
    def __init__(
        self,
        password_hasher: PasswordHasher,
        token_service: TokenService
    ):
        self.password_hasher = password_hasher
        self.token_service = token_service
    
    def authenticate(
        self,
        user: UserEntity,
        credentials: Credentials
    ) -> bool:
        if not user.is_active:
            return False
        
        if credentials.password and user.password_hash:
            return self.password_hasher.verify(
                credentials.password,
                user.password_hash
            )
        
        return False
    
    def create_auth_tokens(
        self,
        user: UserEntity,
        company_id: Optional[str] = None,
        role: Optional[Role] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Tuple[str, RefreshTokenEntity]:
        """Создает access и refresh токены"""
        
        # Access token payload
        payload = {
            "sub": str(user.id),
            "email": user.email,
            "phone": user.phone,
            "name": user.get_full_name()
        }
        
        if company_id:
            payload["company_id"] = company_id
        
        if role:
            payload["role"] = role.type.value
            payload["permissions"] = list(role.get_permissions())
        
        access_token = self.token_service.create_access_token(payload)
        
        # Create refresh token
        refresh_token_value = self.token_service.generate_refresh_token()
        token_hash = self.password_hasher.hash(refresh_token_value)
        
        refresh_token = RefreshTokenEntity.create(
            user_id=user.id,
            token_hash=token_hash,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        return access_token, refresh_token