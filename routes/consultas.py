from fastapi import APIRouter, HTTPException, status, Request
from models.consultas import Consulta
import uuid
consultas_router = APIRouter(prefix="/consultas")
consultas = dict()  # {id: consulta}


@consultas_router.get("/")
async def get_consultas():
    return {
        "data": list(consultas.values()),
    }


@consultas_router.get("/{consulta_id}", status_code=status.HTTP_200_OK)
async def get_consulta_by_id(consulta_id: uuid.UUID):
    consulta = consultas.get(consulta_id, None)
    if consulta is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Consulta não encontrada")

    return {
        "data": consulta
    }


@consultas_router.post("/", status_code=status.HTTP_201_CREATED)
async def create_consulta(consulta: Consulta):
    consulta.id = uuid.uuid4()
    consultas[consulta.id] = consulta

    return {
        "data": consulta
    }


@consultas_router.put("/{consulta_id}", status_code=status.HTTP_200_OK)
async def update_consulta(consulta_id: uuid.UUID, request: Request):
    consulta = consultas.get(consulta_id, None)
    if consulta is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Consulta não encontrada")

    updated_consulta = await request.json()
    updated_consulta["id"] = consulta_id
    consultas[consulta_id] = updated_consulta

    return {
        "data": updated_consulta
    }


@consultas_router.delete("/{consulta_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_consulta(consulta_id: uuid.UUID):
    consulta = consultas.get(consulta_id, None)
    if consulta is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Consulta não encontrada")

    del consultas[consulta_id]
