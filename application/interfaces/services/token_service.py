from abc import ABC, abstractmethod
from typing import Dict, Any

class TokenService(ABC):
    @abstractmethod
    def create_access_token(self, user_id: str, first_name: str, last_name: str, email: str, role: str) -> str:
        pass
    
    @abstractmethod
    def verify_access_token(self, token: str) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def create_refresh_token(self, user_id: str, first_name: str, last_name: str, email: str, role: str) -> str:
        pass