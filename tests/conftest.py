import os

os.environ["DATABASE_URL"] = "sqlite://"

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from auth.rate_limiter import request_history
from database.database import get_session
from database.seed import seed_users
from main import app


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        seed_users(session)
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    request_history.clear()
    with TestClient(app) as c:
        login = c.post("/signin", data={
            "username": "medico@clinica.com",
            "password": "medico123",
        })
        assert login.status_code == 200
        c.headers["Authorization"] = f"Bearer {login.json()['access_token']}"
        yield c
    app.dependency_overrides.clear()
    request_history.clear()
