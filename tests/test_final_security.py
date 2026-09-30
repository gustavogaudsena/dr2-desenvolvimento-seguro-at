from unittest.mock import Mock
from uuid import uuid4

from sqlmodel import Session

from database.database import get_session
from main import app


def test_entrada_invalida_nao_chega_ao_banco(client):
    session_mock = Mock(spec=Session)
    app.dependency_overrides[get_session] = lambda: session_mock

    response = client.post("/consultas/", json={
        "paciente": "<script>alert(1)</script>",
        "medico": "Médico Teste",
        "data": "2026-10-01T14:30:00",
    })

    assert response.status_code == 422
    session_mock.add.assert_not_called()
    session_mock.commit.assert_not_called()


def test_ownership_consulta_o_banco_sem_expor_recurso(client):
    session_mock = Mock(spec=Session)
    session_mock.exec.return_value.first.return_value = None
    app.dependency_overrides[get_session] = lambda: session_mock

    response = client.get(f"/consultas/{uuid4()}")

    assert response.status_code == 404
    session_mock.exec.assert_called_once()


def test_openapi_documenta_autenticacao_e_escopo_m2m(client):
    schema = client.get("/openapi.json").json()
    schemes = schema["components"]["securitySchemes"]

    assert schemes["UserBearer"]["flows"]["password"]["tokenUrl"] == "/signin"
    client_credentials = schemes["ClientBearer"]["flows"]["clientCredentials"]
    assert client_credentials["tokenUrl"] == "/oauth/token"
    assert "horarios:read" in client_credentials["scopes"]
    assert schema["paths"]["/consultas/"]["get"]["security"] == [
        {"UserBearer": []},
    ]
    assert schema["paths"]["/laboratorio/horarios-disponiveis"]["get"][
        "security"
    ] == [{"ClientBearer": ["horarios:read"]}]


def test_openapi_nao_expoe_campos_internos(client):
    schema = client.get("/openapi.json").json()
    consulta_publica = schema["components"]["schemas"]["ConsultaPublica"]
    consulta_create = schema["components"]["schemas"]["ConsultaCreate"]

    assert "owner" not in consulta_publica["properties"]
    assert "criado_em" not in consulta_publica["properties"]
    assert consulta_create["additionalProperties"] is False
