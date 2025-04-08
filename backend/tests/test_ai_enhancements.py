# backend/tests/test_ai_enhancements.py

import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
from backend.app.main import app
from backend.app.utils.database import SessionLocal, Base, engine
from backend.app.utils.database import Task, PomodoroSession, User, Goal

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

# Test: Suggest task schedule
def test_suggest_task_schedule(client, db_session):
    # Create a unique user
    user = create_unique_user(db_session, 1)

    # Create a task
    task = Task(title="Test Task", description="Test Description", user_id=user.id)
    db_session.add(task)
    db_session.commit()

    # Suggest task schedule
    response = client.post(f"/api/study/suggest-task-schedule/{task.id}")
    assert response.status_code == 200
    assert "suggested_time" in response.json() or "message" in response.json()

# Test: Suggest habits
def test_suggest_habits(client, db_session):
    # Create a unique user
    user = create_unique_user(db_session, 2)

    # Create a goal
    goal = Goal(title="Stay Healthy", description="Focus on health", category="health", user_id=user.id)
    db_session.add(goal)
    db_session.commit()

    # Suggest habits
    response = client.get(f"/api/study/suggest-habits/{user.id}")
    assert response.status_code == 200
    assert "suggestions" in response.json()
    assert len(response.json()["suggestions"]) > 0

# Test: Detect distractions
def test_detect_distractions(client, db_session):
    # Create a unique user
    user = create_unique_user(db_session, 3)

    # Create a short Pomodoro session
    pomodoro_session = PomodoroSession(
        start_time=datetime.utcnow(),
        end_time=datetime.utcnow() + timedelta(minutes=10),
        status="completed",
        user_id=user.id,
        focus_time_minutes=10,
    )
    db_session.add(pomodoro_session)
    db_session.commit()

    # Detect distractions
    response = client.get(f"/api/study/detect-distractions/{user.id}")
    assert response.status_code == 200
    assert "distractions" in response.json()
    assert len(response.json()["distractions"]) > 0