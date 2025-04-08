# backend/tests/test_pomodoro_advanced.py

import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
from backend.app.main import app
from backend.app.utils.database import SessionLocal, Base, engine
from backend.app.utils.database import PomodoroSession, PomodoroChallenge, User

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

# Helper function to create a unique user
def create_unique_user(db: SessionLocal, email_suffix: int):
    user = User(name=f"Test User {email_suffix}", email=f"test{email_suffix}@example.com", password="password")
    db.add(user)
    db.commit()
    return user

# Test: Start a Pomodoro session with custom intervals
def test_start_pomodoro_session(client, db_session):
    # Create a unique user
    user = create_unique_user(db_session, 1)

    # Start a Pomodoro session
    response = client.post(
        "/api/pomodoro/start",
        json={
            "work_duration_minutes": 30,
            "break_duration_minutes": 10,
        },
    )
    assert response.status_code == 200
    assert "session_id" in response.json()

# Test: Create a Pomodoro challenge
def test_create_pomodoro_challenge(client, db_session):
    # Create a unique user
    user = create_unique_user(db_session, 2)

    # Create a challenge
    response = client.post(
        "/api/pomodoro/challenges",
        json={
            "title": "Weekly Challenge",
            "description": "Complete 10 Pomodoro sessions this week.",
            "target_sessions": 10,
            "start_date": datetime.utcnow().isoformat(),
            "end_date": (datetime.utcnow() + timedelta(days=7)).isoformat(),
        },
    )
    assert response.status_code == 200
    assert "challenge_id" in response.json()

# Test: Get Pomodoro statistics
def test_get_pomodoro_statistics(client, db_session):
    # Create a unique user
    user = create_unique_user(db_session, 3)

    # Create a Pomodoro session
    session = PomodoroSession(
        start_time=datetime.utcnow(),
        end_time=datetime.utcnow() + timedelta(minutes=25),
        status="completed",
        user_id=user.id,
        focus_time_minutes=25,
    )
    db_session.add(session)
    db_session.commit()

    # Get statistics
    response = client.get(f"/api/pomodoro/statistics/{user.id}")
    assert response.status_code == 200
    assert "total_focus_time_minutes" in response.json()
    assert "average_session_duration_minutes" in response.json()
    assert "total_sessions" in response.json()