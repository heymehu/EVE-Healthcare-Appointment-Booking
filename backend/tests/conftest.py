import os

os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["SECRET_KEY"] = "test-secret-key-do-not-use-in-production"
os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "60"
os.environ["CORS_ORIGINS"] = "http://localhost:5173"

from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete
from sqlalchemy.orm import sessionmaker

from app.core.database import Base, engine, get_db
from app.main import app
from app.models.diagnostic_centre import DiagnosticCentre
from app.models.test import DiagnosticTest


TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(autouse=True)
def clean_tables():
    yield
    session = TestingSessionLocal()
    for table in reversed(Base.metadata.sorted_tables):
        session.execute(delete(table))
    session.commit()
    session.close()


@pytest.fixture
def db():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client():
    def override_get_db():
        session = TestingSessionLocal()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def seed_centre(db):
    centre = DiagnosticCentre(
        name="Apollo Diagnostics",
        location="Bokaro, Jharkhand",
        description="Seeded centre",
        rating=4.5,
        review_count=120,
    )
    db.add(centre)
    db.flush()
    tests = [
        DiagnosticTest(centre_id=centre.id, name="Lipid Profile", category="Blood Test", price=500),
        DiagnosticTest(centre_id=centre.id, name="CBC", category="Blood Test", price=300),
    ]
    db.add_all(tests)
    db.commit()
    db.refresh(centre)
    db.refresh(tests[0])
    return centre, tests[0]


def auth_headers(client, suffix="1"):
    signup = client.post(
        "/auth/signup",
        json={
            "name": f"Mehul Kumar {suffix}",
            "email": f"mehul{suffix}@example.com",
            "password": "secret123",
        },
    )
    assert signup.status_code == 201
    login = client.post(
        "/auth/login",
        json={"email": f"mehul{suffix}@example.com", "password": "secret123"},
    )
    assert login.status_code == 200
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def future_date():
    return (date.today() + timedelta(days=7)).isoformat()
