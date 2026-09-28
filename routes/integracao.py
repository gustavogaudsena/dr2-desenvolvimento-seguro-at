from datetime import date
from typing import Annotated

from auth.authenticate import require_horarios_read
from auth.hash_password import HashPassword
from auth.jwt_handler import ACCESS_TOKEN_EXPIRE_MINUTES, create_client_access_token
from fastapi import APIRouter, Depends, Form, HTTPException, Query, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from database.consultas import consultas
from models.clients import ClientTokenResponse, OAuthClient

NOME_PATTERN = r"^[A-Za-zÀ-ÖØ-öø-ÿ .'-]+$"

integracao_router = APIRouter(tags=["Integração externa"])
basic_auth = HTTPBasic()
hash_password = HashPassword()

oauth_clients = {
    "laboratorio-parceiro": OAuthClient(
        client_id="laboratorio-parceiro",
        secret_hash="$2b$12$brJq3Qo6W1ILlR6S1BoCDeInA13YVaTfDJ08MZaI.f.ISSDltGo0S",
        allowed_scopes={"horarios:read"},
    ),
}


@integracao_router.post("/oauth/token", response_model=ClientTokenResponse)
async def create_client_token(
    credentials: HTTPBasicCredentials = Depends(basic_auth),
    grant_type: str = Form(),
    scope: str = Form(default="horarios:read"),
):
    if grant_type != "client_credentials":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="unsupported_grant_type",
        )

    client = oauth_clients.get(credentials.username)
    if client is None or not hash_password.verify_hash(
        credentials.password,
        client.secret_hash,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid_client",
            headers={"WWW-Authenticate": "Basic"},
        )

    requested_scopes = set(scope.split())
    if not requested_scopes.issubset(client.allowed_scopes):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="invalid_scope",
        )

    return ClientTokenResponse(
        access_token=create_client_access_token(
            client.client_id,
            requested_scopes,
        ),
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        scope=" ".join(sorted(requested_scopes)),
    )


@integracao_router.get("/laboratorio/horarios-disponiveis")
async def get_horarios_disponiveis(
    data: date,
    medico: Annotated[
        str,
        Query(min_length=2, max_length=100, pattern=NOME_PATTERN),
    ],
    _: dict = Depends(require_horarios_read),
):
    horarios_ocupados = {
        consulta.data.strftime("%H:%M")
        for consulta in consultas.values()
        if consulta.data.date() == data and consulta.medico == medico
    }
    horarios = [
        f"{hora:02d}:00"
        for hora in range(8, 18)
        if f"{hora:02d}:00" not in horarios_ocupados
    ]

    return {
        "data": data,
        "medico": medico,
        "horarios": horarios,
    }
