from enum import Enum

from pydantic import BaseModel


class Role(str, Enum):
    RECEPCIONISTA = "recepcionista"
    PROFISSIONAL_SAUDE = "profissional_saude"
    ADMINISTRADOR = "administrador"


class User(BaseModel):
    email: str
    name: str
    password: str
    role: Role
    mfa_enabled: bool = False


class UserCreate(BaseModel):
    email: str
    name: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
