# backend_test/tests/test_study.py

import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
from backend.app.main import app  # Import your FastAPI app
from backend.app.utils.database import SessionLocal, Base, engine, PomodoroSession, User, Task


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

# Fixture to create a test user
@pytest.fixture(scope="function")
def test_user(db_session):
    user = User(name="Test User", email="test@example.com", password="password")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

# Test: Get study session recommendations
def test_get_study_recommendations(client, db_session, test_user):
    # Create a Pomodoro session for the test user
    start_time = datetime.utcnow().replace(hour=10, minute=0, second=0, microsecond=0)
    end_time = start_time + timedelta(hours=1)

    session = PomodoroSession(
        start_time=start_time,
        end_time=end_time,
        user_id=test_user.id,  # Add this line
    )
    db_session.add(session)
    db_session.commit()

    # Get study session recommendations
    response = client.get(f"/api/study/recommendations/{test_user.id}")
    assert response.status_code == 200
    assert "recommendations" in response.json()
    assert len(response.json()["recommendations"]) > 0

#Helper function to create a unique user
def create_unique_user(db: SessionLocal, email_suffix: int):
    user = User(name=f"Test User {email_suffix}", email=f"test{email_suffix}@example.com", password="password")
    db.add(user)
    db.commit()
    return user

# Test: Get productivity score
def test_get_productivity_score(client, db_session):
    # Create a unique user
    user = create_unique_user(db_session, 1)

    # Create completed tasks and Pomodoro sessions
    task = Task(title="Test Task", description="Test Description", user_id=user.id, status="completed")
    db_session.add(task)
    db_session.commit()

    pomodoro_session = PomodoroSession(
        start_time=datetime.utcnow(),
        end_time=datetime.utcnow() + timedelta(minutes=25),
        status="completed",
        user_id=user.id,
        focus_time_minutes=25,
    )
    db_session.add(pomodoro_session)
    db_session.commit()

    # Get productivity score
    response = client.get(f"/api/study/productivity-score/{user.id}")
    assert response.status_code == 200
    assert "productivity_score" in response.json()
    assert response.json()["productivity_score"] > 0

# Test: Get focus metrics
def test_get_focus_metrics(client, db_session):
    # Create a unique user
    user = create_unique_user(db_session, 2)

    # Create Pomodoro sessions
    pomodoro_session = PomodoroSession(
        start_time=datetime.utcnow(),
        end_time=datetime.utcnow() + timedelta(minutes=25),
        status="completed",
        user_id=user.id,
        focus_time_minutes=25,
    )
    db_session.add(pomodoro_session)
    db_session.commit()

    # Get focus metrics
    response = client.get(f"/api/study/focus-metrics/{user.id}")
    assert response.status_code == 200
    assert "total_focus_time_minutes" in response.json()
    assert "average_session_duration_minutes" in response.json()
    assert response.json()["total_focus_time_minutes"] == 25
    assert response.json()["average_session_duration_minutes"] == 25

# Test: Generate weekly report
def test_generate_weekly_report(client, db_session):
    # Create a unique user
    user = create_unique_user(db_session, 3)

    # Create completed tasks and Pomodoro sessions
    task = Task(title="Test Task", description="Test Description", user_id=user.id, status="completed")
    db_session.add(task)
    db_session.commit()

    pomodoro_session = PomodoroSession(
        start_time=datetime.utcnow(),
        end_time=datetime.utcnow() + timedelta(minutes=25),
        status="completed",
        user_id=user.id,
        focus_time_minutes=25,
    )
    db_session.add(pomodoro_session)
    db_session.commit()

    # Generate weekly report
    response = client.get(f"/api/study/weekly-report/{user.id}")
    assert response.status_code == 200
    assert "productivity_score" in response.json()
    assert "focus_metrics" in response.json()
    assert "completed_tasks" in response.json()
    assert "habit_streaks" in response.json()