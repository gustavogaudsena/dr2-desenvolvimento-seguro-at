from datetime import datetime
from pydantic import BaseModel
import uuid


class ConsultaBase(BaseModel):
    paciente: str
    medico: str
    data: datetime
    observacoes: str | None = None


class ConsultaCreate(ConsultaBase):
    pass


class Consulta(ConsultaBase):
    id: uuid.UUID
    criado_em: datetime


class ConsultaPublica(ConsultaBase):
    id: uuid.UUID


class RespostaConsulta(BaseModel):
    data: ConsultaPublica


class RespostaConsultas(BaseModel):
    data: list[ConsultaPublica]
