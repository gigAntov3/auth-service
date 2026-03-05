from dataclasses import dataclass
from typing import Optional, List
from uuid import UUID


@dataclass
class RegisterRequestDTO:
    first_name: str
    last_name: str
    email: str
    password: str
    ip_address: str
    user_agent: str


@dataclass
class RegisterResponseDTO:
    access_token: str
    refresh_token: str
    expires_in: int
    user_id: UUID
    first_name: str
    last_name: str
    email: str
    role: Optional[str] = None



@dataclass
class LoginRequestDTO:
    email: str
    password: str
    ip_address: str
    user_agent: str

@dataclass
class LoginResponseDTO:
    access_token: str
    refresh_token: str
    expires_in: int
    user_id: UUID
    first_name: str
    last_name: str
    email: str
    role: Optional[str] = None



@dataclass
class LogoutRequestDTO: 
    refresh_token: str
    ip_address: str
    user_agent: str


@dataclass
class RefreshRequestDTO:
    refresh_token: str
    ip_address: str
    user_agent: str


@dataclass
class RefreshResponseDTO:
    access_token: str
    refresh_token: str
    expires_in: int