from uuid import uuid4

NOVA_CONSULTA = {
    "paciente": "Maria Silva",
    "medico": "Dr. João Souza",
    "data": "2026-10-01T14:30:00",
    "criado_em": "2026-09-26T10:00:00",
}


def criar_consulta(client):
    response = client.post("/consultas/", json=NOVA_CONSULTA)
    assert response.status_code == 201
    return response.json()["data"]


def test_criar_consulta_retorna_201_com_id_gerado(client):
    response = client.post("/consultas/", json=NOVA_CONSULTA)

    assert response.status_code == 201
    consulta = response.json()["data"]
    assert consulta["paciente"] == NOVA_CONSULTA["paciente"]
    assert consulta["medico"] == NOVA_CONSULTA["medico"]
    assert consulta["data"] == NOVA_CONSULTA["data"]
    assert consulta["id"]


def test_listar_consultas_retorna_consultas_criadas(client):
    criada = criar_consulta(client)

    response = client.get("/consultas/")

    assert response.status_code == 200
    assert response.json()["data"] == [criada]


def test_buscar_consulta_por_id(client):
    criada = criar_consulta(client)

    response = client.get(f"/consultas/{criada['id']}")

    assert response.status_code == 200
    assert response.json()["data"] == criada


def test_atualizar_consulta_sem_id_no_body_mantem_id(client):
    criada = criar_consulta(client)
    alteracao = {**NOVA_CONSULTA, "data": "2026-10-02T09:00:00"}

    response = client.put(f"/consultas/{criada['id']}", json=alteracao)

    assert response.status_code == 200
    assert response.json()["data"]["data"] == "2026-10-02T09:00:00"
    busca = client.get(f"/consultas/{criada['id']}").json()["data"]
    assert busca["id"] == criada["id"]
    assert busca["data"] == "2026-10-02T09:00:00"


def test_remover_consulta(client):
    criada = criar_consulta(client)

    response = client.delete(f"/consultas/{criada['id']}")

    assert response.status_code == 204
    assert client.get(f"/consultas/{criada['id']}").status_code == 404


def test_buscar_consulta_inexistente_retorna_404(client):
    response = client.get(f"/consultas/{uuid4()}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Consulta não encontrada"


def test_criar_consulta_sem_campos_obrigatorios_retorna_422(client):
    response = client.post("/consultas/", json={"paciente": "Maria Silva"})

    assert response.status_code == 422
