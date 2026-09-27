from datetime import date
from uuid import UUID, uuid4
from routes.consultas import consultas

NOVA_CONSULTA = {
    "paciente": "Maria Silva",
    "medico": "Dr. João Souza",
    "data": "2026-10-01T14:30:00",
    "observacoes": "Trazer exames anteriores",
}


def criar_consulta(client, payload=NOVA_CONSULTA):
    response = client.post("/consultas/", json=payload)
    assert response.status_code == 201
    return response.json()["data"]


def test_criar_consulta_retorna_201_com_id_gerado(client):
    response = client.post("/consultas/", json=NOVA_CONSULTA)

    assert response.status_code == 201
    consulta = response.json()["data"]
    assert consulta["paciente"] == NOVA_CONSULTA["paciente"]
    assert consulta["medico"] == NOVA_CONSULTA["medico"]
    assert consulta["data"] == NOVA_CONSULTA["data"]
    assert consulta["observacoes"] == NOVA_CONSULTA["observacoes"]
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


def test_atualizar_consulta_com_payload_invalido_retorna_422(client):
    criada = criar_consulta(client)

    response = client.put(f"/consultas/{criada['id']}", json={"paciente": "Maria Silva"})

    assert response.status_code == 422


def test_nenhuma_resposta_da_api_expoe_criado_em(client):
    criada = client.post("/consultas/", json=NOVA_CONSULTA).json()["data"]
    busca = client.get(f"/consultas/{criada['id']}").json()["data"]
    lista = client.get("/consultas/").json()["data"]
    atualizada = client.put(f"/consultas/{criada['id']}", json=NOVA_CONSULTA).json()["data"]

    for consulta in [criada, busca, *lista, atualizada]:
        assert "criado_em" not in consulta


def test_criado_em_enviado_pelo_cliente_e_ignorado(client):
    payload = {**NOVA_CONSULTA, "criado_em": "2000-01-01T00:00:00"}

    criada = criar_consulta(client, payload)

    assert consultas[UUID(criada["id"])].criado_em.year != 2000


def test_atualizar_consulta_preserva_criado_em(client):
    criada = criar_consulta(client)
    criado_em_original = consultas[UUID(criada["id"])].criado_em

    client.put(f"/consultas/{criada['id']}", json={**NOVA_CONSULTA, "criado_em": "2000-01-01T00:00:00"})

    assert consultas[UUID(criada["id"])].criado_em == criado_em_original


def test_agenda_mostra_so_consultas_do_dia_pedido(client):
    criar_consulta(client, {**NOVA_CONSULTA, "paciente": "Ana Dia Um", "data": "2026-10-01T10:00:00"})
    criar_consulta(client, {**NOVA_CONSULTA, "paciente": "Bruno Dia Dois", "data": "2026-10-02T10:00:00"})

    response = client.get("/agenda?data=2026-10-01")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert "Ana Dia Um" in response.text
    assert "Bruno Dia Dois" not in response.text


def test_agenda_sem_data_mostra_consultas_de_hoje(client):
    hoje = date.today().isoformat()
    criar_consulta(client, {**NOVA_CONSULTA, "paciente": "Carla Hoje", "data": f"{hoje}T10:00:00"})

    response = client.get("/agenda")

    assert response.status_code == 200
    assert "Carla Hoje" in response.text


def test_agenda_ordena_consultas_por_horario(client):
    criar_consulta(client, {**NOVA_CONSULTA, "paciente": "Tarde", "data": "2026-10-01T15:00:00"})
    criar_consulta(client, {**NOVA_CONSULTA, "paciente": "Manha", "data": "2026-10-01T09:00:00"})

    html = client.get("/agenda?data=2026-10-01").text

    assert html.index("Manha") < html.index("Tarde")


def test_agenda_herda_layout_do_template_base(client):
    html = client.get("/agenda?data=2026-10-01").text

    assert "Clínica — Recepção" in html
    assert "Agenda do dia" in html


def test_agenda_escapa_html_de_paciente_e_observacoes(client):
    criar_consulta(client, {
        **NOVA_CONSULTA,
        "paciente": "<script>alert(1)</script>",
        "observacoes": "<img src=x onerror=alert(2)>",
    })

    html = client.get("/agenda?data=2026-10-01").text

    assert "<script>alert(1)</script>" not in html
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in html
    assert "<img src=x onerror=alert(2)>" not in html
    assert "&lt;img src=x onerror=alert(2)&gt;" in html
