# backend/tests/test_pomodoro.py

import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
from backend.app.main import app  # Import your FastAPI app
from backend.app.utils.database import SessionLocal, Base, engine

# Fixture to provide a TestClient instance
@pytest.fixture(scope="module")
def client():
    with TestClient(app) as client:
        yield client

# Fixture to set up and tear down the database
@pytest.fixture(scope="module")
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

# Fixture to provide a database session
@pytest.fixture(scope="function")
def db_session(setup_database):
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_start_pomodoro_session(client, db_session):
    # Start a Pomodoro session
    response = client.post("/api/pomodoro/start")
    assert response.status_code == 200
    assert "session_id" in response.json()

def test_end_pomodoro_session(client, db_session):
    # Start a Pomodoro session
    start_response = client.post("/api/pomodoro/start")
    session_id = start_response.json()["session_id"]

    # End the Pomodoro session
    end_response = client.post(f"/api/pomodoro/end/{session_id}")
    assert end_response.status_code == 200
    assert "session_id" in end_response.json()

def test_get_all_pomodoro_sessions(client, db_session):
    # Start a Pomodoro session
    client.post("/api/pomodoro/start")

    # Get all Pomodoro sessions
    response = client.get("/api/pomodoro/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0

# Test: Export Pomodoro logs
def test_export_pomodoro_logs(client, db_session):
    # Start a Pomodoro session
    client.post("/api/pomodoro/start")

    # Export Pomodoro logs
    response = client.get("/api/pomodoro/export-logs")
    assert response.status_code == 200
    assert "message" in response.json()