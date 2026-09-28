from fastapi import APIRouter, Depends, status
from sqlmodel import Session, select

from auth.authenticate import require_professional
from auth.autorizacao import require_owned_consulta
from database.database import get_session
from models.consultas import (
    Consulta,
    ConsultaCreate,
    RespostaConsulta,
    RespostaConsultas,
)

consultas_router = APIRouter(prefix="/consultas")


@consultas_router.get("/", response_model=RespostaConsultas)
async def get_consultas(
    user: dict = Depends(require_professional),
    session: Session = Depends(get_session),
):
    statement = select(Consulta).where(Consulta.owner == user["sub"])
    return {
        "data": session.exec(statement).all(),
    }


@consultas_router.get("/{consulta_id}", status_code=status.HTTP_200_OK,
                      response_model=RespostaConsulta)
async def get_consulta_by_id(
    consulta: Consulta = Depends(require_owned_consulta),
):
    return {
        "data": consulta
    }


@consultas_router.post("/", status_code=status.HTTP_201_CREATED,
                       response_model=RespostaConsulta)
async def create_consulta(
    dados: ConsultaCreate,
    user: dict = Depends(require_professional),
    session: Session = Depends(get_session),
):
    consulta = Consulta(
        owner=user["sub"],
        **dados.model_dump(),
    )
    session.add(consulta)
    session.commit()
    session.refresh(consulta)

    return {
        "data": consulta
    }


@consultas_router.put("/{consulta_id}", status_code=status.HTTP_200_OK,
                      response_model=RespostaConsulta)
async def update_consulta(
    dados: ConsultaCreate,
    consulta: Consulta = Depends(require_owned_consulta),
    session: Session = Depends(get_session),
):
    consulta.sqlmodel_update(dados.model_dump())
    session.add(consulta)
    session.commit()
    session.refresh(consulta)

    return {
        "data": consulta
    }


@consultas_router.delete("/{consulta_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_consulta(
    consulta: Consulta = Depends(require_owned_consulta),
    session: Session = Depends(get_session),
):
    session.delete(consulta)
    session.commit()
