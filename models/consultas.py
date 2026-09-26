from datetime import datetime
from pydantic import BaseModel
import uuid

class Consulta(BaseModel):
    id: uuid.UUID | None = None
    paciente: str
    medico: str
    data: datetime
    criado_em: datetime

    class Settings:
        name = "consultas"


