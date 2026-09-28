from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

NOME_PATTERN = r"^[A-Za-zÀ-ÖØ-öø-ÿ .'-]+$"
EMAIL_PATTERN = r"^[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+$"


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
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    email: str = Field(
        min_length=5,
        max_length=254,
        pattern=EMAIL_PATTERN,
    )
    name: str = Field(
        min_length=2,
        max_length=100,
        pattern=NOME_PATTERN,
    )
    password: str = Field(min_length=8, max_length=72)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
