import uuid

from fastapi import Depends, HTTPException, status
from sqlmodel import Session, select

from auth.authenticate import require_professional
from database.database import get_session
from models.consultas import Consulta


async def require_owned_consulta(
    consulta_id: uuid.UUID,
    user: dict = Depends(require_professional),
    session: Session = Depends(get_session),
) -> Consulta:
    statement = select(Consulta).where(
        Consulta.id == consulta_id,
        Consulta.owner == user["sub"],
    )
    consulta = session.exec(statement).first()
    if consulta is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Consulta não encontrada",
        )
    return consulta
