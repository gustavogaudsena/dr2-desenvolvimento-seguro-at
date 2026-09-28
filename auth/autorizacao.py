import uuid

from fastapi import Depends, HTTPException, status

from auth.authenticate import require_professional
from database.consultas import consultas
from models.consultas import Consulta


async def require_owned_consulta(
    consulta_id: uuid.UUID,
    user: dict = Depends(require_professional),
) -> Consulta:
    consulta = consultas.get(consulta_id)
    if consulta is None or consulta.owner != user["sub"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Consulta não encontrada",
        )
    return consulta
