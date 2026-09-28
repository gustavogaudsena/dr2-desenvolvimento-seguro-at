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
