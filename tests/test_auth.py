from auth.jwt_handler import create_access_token
from auth.rate_limiter import (
    DEFAULT_MAX_REQUESTS,
    LOGIN_MAX_REQUESTS,
    request_history,
)
from models.users import Role, User


def test_profissional_nao_acessa_rota_restrita_a_admin(client):
    login = client.post("/signin", data={
        "username": "medico@clinica.com",
        "password": "medico123",
    })
    assert login.status_code == 200

    response = client.get("/admin", headers={
        "Authorization": f"Bearer {login.json()['access_token']}",
    })

    assert response.status_code == 403


def test_profissional_nao_acessa_consulta_de_outro_profissional(client):
    outro_profissional = User(
        email="outro@clinica.com",
        name="Outro Médico",
        password="hash-não-utilizado",
        role=Role.PROFISSIONAL_SAUDE,
    )
    outro_token = create_access_token(outro_profissional, False)
    criada = client.post(
        "/consultas/",
        headers={"Authorization": f"Bearer {outro_token}"},
        json={
            "paciente": "Paciente Protegido",
            "medico": "Outro Médico",
            "data": "2026-10-01T14:30:00",
        },
    ).json()["data"]

    response = client.get(f"/consultas/{criada['id']}")

    assert response.status_code == 404


def test_recepcionista_nao_cria_consulta(client):
    login = client.post("/signin", data={
        "username": "recepcao@clinica.com",
        "password": "recepcao123",
    })
    assert login.status_code == 200

    response = client.post(
        "/consultas/",
        headers={
            "Authorization": f"Bearer {login.json()['access_token']}",
        },
        json={
            "paciente": "Paciente Teste",
            "medico": "Médico Teste",
            "data": "2026-10-01T14:30:00",
        },
    )

    assert response.status_code == 403


def test_profissional_nao_altera_nem_exclui_consulta_de_outro(client):
    outro_profissional = User(
        email="outro@clinica.com",
        name="Outro Médico",
        password="hash-não-utilizado",
        role=Role.PROFISSIONAL_SAUDE,
    )
    outro_token = create_access_token(outro_profissional, False)
    criada = client.post(
        "/consultas/",
        headers={"Authorization": f"Bearer {outro_token}"},
        json={
            "paciente": "Paciente Protegido",
            "medico": "Outro Médico",
            "data": "2026-10-01T14:30:00",
        },
    ).json()["data"]

    alteracao = client.put(
        f"/consultas/{criada['id']}",
        json={
            "paciente": "Paciente Alterado",
            "medico": "Outro Médico",
            "data": "2026-10-02T14:30:00",
        },
    )
    exclusao = client.delete(f"/consultas/{criada['id']}")

    assert alteracao.status_code == 404
    assert exclusao.status_code == 404


def test_agenda_exige_autenticacao(client):
    response = client.get(
        "/agenda",
        headers={"Authorization": ""},
    )

    assert response.status_code == 401


def test_signup_rejeita_role_enviada_no_body(client):
    admin = User(
        email="admin-teste@clinica.com",
        name="Administrador Teste",
        password="hash-não-utilizado",
        role=Role.ADMINISTRADOR,
        mfa_enabled=True,
    )
    admin_token = create_access_token(admin, True)

    response = client.post(
        "/signup",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "email": "novo@clinica.com",
            "name": "Novo Profissional",
            "password": "senha-segura",
            "role": "administrador",
        },
    )

    assert response.status_code == 422


def test_rate_limiter_aplica_limite_generico(client):
    request_history.clear()
    for _ in range(DEFAULT_MAX_REQUESTS):
        response = client.get("/openapi.json")
        assert response.status_code == 200

    response = client.get("/openapi.json")

    assert response.status_code == 429


def test_rate_limiter_aplica_limite_menor_ao_login(client):
    request_history.clear()
    for _ in range(LOGIN_MAX_REQUESTS):
        response = client.post("/signin", data={
            "username": "ataque@clinica.com",
            "password": "senha-incorreta",
        })
        assert response.status_code == 401

    response = client.post("/signin", data={
        "username": "ataque@clinica.com",
        "password": "senha-incorreta",
    })

    assert response.status_code == 429
