from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
import uuid

NOME_PATTERN = r"^[A-Za-zÀ-ÖØ-öø-ÿ .'-]+$"


class ConsultaBase(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    paciente: str = Field(
        min_length=2,
        max_length=100,
        pattern=NOME_PATTERN,
    )
    medico: str = Field(
        min_length=2,
        max_length=100,
        pattern=NOME_PATTERN,
    )
    data: datetime
    observacoes: str | None = Field(default=None, max_length=500)


class ConsultaCreate(ConsultaBase):
    pass


class Consulta(ConsultaBase):
    id: uuid.UUID
    criado_em: datetime
    owner: str


class ConsultaPublica(ConsultaBase):
    id: uuid.UUID


class RespostaConsulta(BaseModel):
    data: ConsultaPublica


class RespostaConsultas(BaseModel):
    data: list[ConsultaPublica]
