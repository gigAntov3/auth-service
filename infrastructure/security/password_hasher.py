import bcrypt
from application.interfaces.password_hasher import PasswordHasher

class BcryptPasswordHasher(PasswordHasher):
    """Bcrypt implementation of password hashing"""
    
    def __init__(self, rounds: int = 12):
        self.rounds = rounds
    
    def hash(self, password: str) -> str:
        """Hash a password using bcrypt"""
        salt = bcrypt.gensalt(rounds=self.rounds)
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verify(self, password: str, hashed: str) -> bool:
        """Verify a password against its hash"""
        try:
            return bcrypt.checkpw(
                password.encode('utf-8'),
                hashed.encode('utf-8')
            )
        except (ValueError, TypeError):
            return False