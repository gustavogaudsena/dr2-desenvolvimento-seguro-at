from main import ALLOWED_ORIGINS


def test_cors_permite_origem_da_allowlist(client):
    response = client.options("/consultas/", headers={
        "Origin": ALLOWED_ORIGINS[0],
        "Access-Control-Request-Method": "GET",
    })

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == ALLOWED_ORIGINS[0]


def test_cors_nao_permite_origem_desconhecida(client):
    response = client.get(
        "/consultas/",
        headers={"Origin": "https://site-malicioso.com"},
    )

    assert "access-control-allow-origin" not in response.headers


def test_resposta_inclui_cabecalhos_de_seguranca(client):
    response = client.get("/consultas/")

    assert response.headers["strict-transport-security"] == (
        "max-age=31536000; includeSubDomains"
    )
    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["x-content-type-options"] == "nosniff"
