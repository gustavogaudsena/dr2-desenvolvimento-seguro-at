import pytest
from fastapi.testclient import TestClient
from main import app
from routes.consultas import consultas


@pytest.fixture
def client():
    # Cada teste começa com o dicionário vazio, sem vazar dados entre testes.
    consultas.clear()
    with TestClient(app) as c:
        yield c
    consultas.clear()
