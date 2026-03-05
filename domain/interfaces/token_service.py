from abc import ABC, abstractmethod
from typing import Dict, Any

class TokenService(ABC):
    @abstractmethod
    def create_access_token(self, user_id: str, email: str, first_name: str, last_name: str) -> str:
        pass
    
    @abstractmethod
    def verify_access_token(self, token: str) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def generate_refresh_token(self) -> str:
        pass
    
    @abstractmethod
    def generate_invitation_token(self) -> str:
        pass

    @abstractmethod
    def create_refresh_token(self, user_id: str) -> str:
        pass