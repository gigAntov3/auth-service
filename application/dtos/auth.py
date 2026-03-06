from dataclasses import dataclass
from typing import Optional, List
from uuid import UUID

from application.dtos.users import UserPublicDTO


@dataclass
class DeviceInfoDTO:
    ip_address: str
    user_agent: str
    device_name: str
    device_type: str


@dataclass
class RegisterRequestDTO(DeviceInfoDTO):
    first_name: str
    last_name: str
    email: str
    password: str



@dataclass
class LoginRequestDTO(DeviceInfoDTO):
    email: str
    password: str


@dataclass
class TokenResponseDTO:
    access_token: str
    refresh_token: str
    expires_in: int
    token_type: str = "Bearer"


@dataclass
class LoginResponseDTO(TokenResponseDTO, UserPublicDTO):
    pass


@dataclass
class RegisterResponseDTO(TokenResponseDTO, UserPublicDTO):
    pass



@dataclass
class LogoutRequestDTO(DeviceInfoDTO): 
    refresh_token: str


@dataclass
class RefreshRequestDTO:
    refresh_token: str


@dataclass
class RefreshResponseDTO(TokenResponseDTO):
    pass