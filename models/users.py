from enum import Enum
from typing import Annotated

from pydantic import ConfigDict, StringConstraints
from sqlmodel import Field, SQLModel

NOME_PATTERN = r"^[A-Za-zÀ-ÖØ-öø-ÿ .'-]+$"
EMAIL_PATTERN = r"^[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+$"
Nome = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=2,
        max_length=100,
        pattern=NOME_PATTERN,
    ),
]
Email = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=5,
        max_length=254,
        pattern=EMAIL_PATTERN,
    ),
]
Password = Annotated[
    str,
    StringConstraints(min_length=8, max_length=72),
]


class Role(str, Enum):
    RECEPCIONISTA = "recepcionista"
    PROFISSIONAL_SAUDE = "profissional_saude"
    ADMINISTRADOR = "administrador"


class User(SQLModel, table=True):
    __tablename__ = "users"

    email: str = Field(primary_key=True, max_length=254)
    name: str = Field(max_length=100)
    password: str = Field(max_length=72)
    role: Role = Field(index=True)
    mfa_enabled: bool = False


class UserCreate(SQLModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    email: Email
    name: Nome
    password: Password


class TokenResponse(SQLModel):
    access_token: str
    token_type: str = "bearer"
