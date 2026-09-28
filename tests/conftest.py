import pytest
from fastapi.testclient import TestClient
from auth.rate_limiter import request_history
from database.consultas import consultas
from main import app


@pytest.fixture
def client():
    consultas.clear()
    request_history.clear()
    with TestClient(app) as c:
        login = c.post("/signin", data={
            "username": "medico@clinica.com",
            "password": "medico123",
        })
        assert login.status_code == 200
        c.headers["Authorization"] = f"Bearer {login.json()['access_token']}"
        yield c
    consultas.clear()
    request_history.clear()
