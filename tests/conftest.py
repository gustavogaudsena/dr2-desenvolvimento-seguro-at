import pytest
from fastapi.testclient import TestClient
from main import app
from routes.consultas import consultas


@pytest.fixture
def client():
    consultas.clear()
    with TestClient(app) as c:
        login = c.post("/signin", data={
            "username": "medico@clinica.com",
            "password": "medico123",
        })
        assert login.status_code == 200
        c.headers["Authorization"] = f"Bearer {login.json()['access_token']}"
        yield c
    consultas.clear()
