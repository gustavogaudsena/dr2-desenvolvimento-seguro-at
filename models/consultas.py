from datetime import datetime, timezone
from typing import Annotated

from pydantic import ConfigDict, StringConstraints
from sqlmodel import Field, SQLModel
import uuid

NOME_PATTERN = r"^[A-Za-zÀ-ÖØ-öø-ÿ .'-]+$"
Nome = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=2,
        max_length=100,
        pattern=NOME_PATTERN,
    ),
]


class ConsultaBase(SQLModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    paciente: Nome
    medico: Nome
    data: datetime
    observacoes: str | None = Field(default=None, max_length=500)


class ConsultaCreate(ConsultaBase):
    pass


class Consulta(ConsultaBase, table=True):
    __tablename__ = "consultas"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    criado_em: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
    )
    owner: str = Field(index=True, max_length=254)


class ConsultaPublica(ConsultaBase):
    id: uuid.UUID


class RespostaConsulta(SQLModel):
    data: ConsultaPublica


class RespostaConsultas(SQLModel):
    data: list[ConsultaPublica]
