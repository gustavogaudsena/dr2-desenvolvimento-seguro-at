from datetime import datetime, timezone
from fastapi import APIRouter, Depends, status
from auth.authenticate import require_professional
from auth.autorizacao import require_owned_consulta
from database.consultas import consultas
from models.consultas import Consulta, ConsultaCreate, RespostaConsulta, RespostaConsultas
import uuid
consultas_router = APIRouter(prefix="/consultas")


@consultas_router.get("/", response_model=RespostaConsultas)
async def get_consultas(user: dict = Depends(require_professional)):
    return {
        "data": [
            consulta for consulta in consultas.values()
            if consulta.owner == user["sub"]
        ],
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
):
    consulta = Consulta(id=uuid.uuid4(),
                        criado_em=datetime.now(timezone.utc),
                        owner=user["sub"],
                        **dados.model_dump())
    consultas[consulta.id] = consulta

    return {
        "data": consulta
    }


@consultas_router.put("/{consulta_id}", status_code=status.HTTP_200_OK,
                      response_model=RespostaConsulta)
async def update_consulta(
    consulta_id: uuid.UUID,
    dados: ConsultaCreate,
    consulta: Consulta = Depends(require_owned_consulta),
):
    updated_consulta = consulta.model_copy(update=dados.model_dump())
    consultas[consulta_id] = updated_consulta

    return {
        "data": updated_consulta
    }


@consultas_router.delete("/{consulta_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_consulta(
    consulta_id: uuid.UUID,
    _: Consulta = Depends(require_owned_consulta),
):
    del consultas[consulta_id]
