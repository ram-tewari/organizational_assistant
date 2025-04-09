# backend/tests/test_tasks.py

import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
from backend.app.main import app
from backend.app.utils.database import SessionLocal, Base, engine, Task, User


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="module")
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(setup_database):
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(scope="function")
def test_user(db_session):
    db_session.query(User).delete()  # Clear existing users
    db_session.commit()
    user = User(name="Test User", email="test@example.com", password="password")
    db_session.add(user)
    db_session.commit()
    return user


def test_create_task_with_scheduling_options(client, db_session, test_user):
    due_date = datetime.utcnow() + timedelta(days=7)
    response = client.post(
        "/api/tasks/",
        json={
            "title": "Learn AI",
            "description": "Study machine learning basics",
            "due_date": due_date.isoformat(),
            "task_length": 10,
            "subtasks": [
                "Watch lecture 1",
                "Read chapter 1",
                "Complete exercises",
                "Review notes"
            ],
            "user_id": test_user.id
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Task created successfully"
    assert data["task"]["title"] == "Learn AI"
    assert len(data["scheduling_options"]) == 3
    assert data["scheduling_options"][0]["name"] == "Intensive Schedule"


def test_create_task_with_user_priority(client, db_session, test_user):
    due_date = datetime.utcnow() + timedelta(days=2)
    response = client.post(
        "/api/tasks/",
        json={
            "title": "Learn AI",
            "description": "Study machine learning basics",
            "priority": "high",
            "due_date": due_date.isoformat(),
            "user_id": test_user.id
        },
    )
    assert response.status_code == 200
    assert response.json()["task"]["priority"] == "high"


def test_update_task(client, db_session, test_user):
    # Create a task first
    due_date = datetime.utcnow() + timedelta(days=2)
    create_response = client.post(
        "/api/tasks/",
        json={
            "title": "Learn AI",
            "description": "Study machine learning basics",
            "priority": "high",
            "due_date": due_date.isoformat(),
            "user_id": test_user.id
        },
    )
    task_id = create_response.json()["task"]["id"]

    # Update the task
    updated_due_date = datetime.utcnow() + timedelta(days=3)
    update_response = client.put(
        f"/api/tasks/{task_id}",
        json={
            "title": "Updated Task",
            "description": "Updated description",
            "priority": "medium",
            "due_date": updated_due_date.isoformat(),
        },
    )
    assert update_response.status_code == 200
    assert update_response.json()["title"] == "Updated Task"
    assert update_response.json()["priority"] == "medium"


def test_delete_task(client, db_session, test_user):
    # Create a task first
    due_date = datetime.utcnow() + timedelta(days=2)
    create_response = client.post(
        "/api/tasks/",
        json={
            "title": "Learn AI",
            "description": "Study machine learning basics",
            "priority": "high",
            "due_date": due_date.isoformat(),
            "user_id": test_user.id
        },
    )
    task_id = create_response.json()["task"]["id"]

    # Delete the task
    delete_response = client.delete(f"/api/tasks/{task_id}")
    assert delete_response.status_code == 200
    assert delete_response.json()["detail"] == "Task deleted"


def test_create_subtask(client, db_session, test_user):
    # Create a task first
    due_date = datetime.utcnow() + timedelta(days=2)
    create_response = client.post(
        "/api/tasks/",
        json={
            "title": "Learn AI",
            "description": "Study machine learning basics",
            "priority": "high",
            "due_date": due_date.isoformat(),
            "user_id": test_user.id
        },
    )
    task_id = create_response.json()["task"]["id"]

    # Create a subtask
    response = client.post(
        f"/api/tasks/{task_id}/subtasks",
        json={
            "title": "Watch Lecture 1",
            "description": "Introduction to AI",
        },
    )
    assert response.status_code == 200
    assert "subtask_id" in response.json()


def test_get_subtasks(client, db_session, test_user):
    # Create a task first
    due_date = datetime.utcnow() + timedelta(days=2)
    create_response = client.post(
        "/api/tasks/",
        json={
            "title": "Learn AI",
            "description": "Study machine learning basics",
            "priority": "high",
            "due_date": due_date.isoformat(),
            "user_id": test_user.id
        },
    )
    task_id = create_response.json()["task"]["id"]

    # Create a subtask
    client.post(
        f"/api/tasks/{task_id}/subtasks",
        json={
            "title": "Watch Lecture 1",
            "description": "Introduction to AI",
        },
    )

    # Retrieve subtasks
    response = client.get(f"/api/tasks/{task_id}/subtasks")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0


def test_add_task_dependency(client, db_session, test_user):
    # Create two tasks
    due_date = datetime.utcnow() + timedelta(days=2)
    task1_response = client.post(
        "/api/tasks/",
        json={
            "title": "Task 1",
            "description": "Complete Task 1",
            "priority": "high",
            "due_date": due_date.isoformat(),
            "user_id": test_user.id
        },
    )
    task1_id = task1_response.json()["task"]["id"]

    task2_response = client.post(
        "/api/tasks/",
        json={
            "title": "Task 2",
            "description": "Complete Task 2",
            "priority": "high",
            "due_date": due_date.isoformat(),
            "user_id": test_user.id
        },
    )
    task2_id = task2_response.json()["task"]["id"]

    # Add a dependency
    response = client.post(
        f"/api/tasks/{task2_id}/add-dependency",
        json={
            "depends_on_task_id": task1_id,
        },
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Dependency added successfully"


def test_complete_task(client, db_session, test_user):
    # Create a task first
    due_date = datetime.utcnow() + timedelta(days=2)
    create_response = client.post(
        "/api/tasks/",
        json={
            "title": "Learn AI",
            "description": "Study machine learning basics",
            "priority": "high",
            "due_date": due_date.isoformat(),
            "user_id": test_user.id
        },
    )
    task_id = create_response.json()["task"]["id"]

    # Mark the task as completed
    response = client.post(f"/api/tasks/{task_id}/complete")
    assert response.status_code == 200
    assert response.json()["message"] == "Task marked as completed"


# Test: Create a task template
def test_create_task_template(client, db_session):
    response = client.post(
        "/api/tasks/templates",
        json={
            "title": "Study Session Template",
            "description": "Template for study sessions",
            "subtasks": ["Read notes", "Watch lecture", "Practice problems"],
        },
    )
    assert response.status_code == 200
    assert "template_id" in response.json()

# Test: Create a task from a template
def test_create_task_from_template(client, db_session):
    # Create a template first
    template_response = client.post(
        "/api/tasks/templates",
        json={
            "title": "Study Session Template",
            "description": "Template for study sessions",
            "subtasks": ["Read notes", "Watch lecture", "Practice problems"],
        },
    )
    template_id = template_response.json()["template_id"]

    # Create a task from the template
    due_date = datetime.utcnow() + timedelta(days=2)
    response = client.post(
        f"/api/tasks/create-from-template/{template_id}",
        json={
            "title": "Study AI",
            "description": "Study machine learning basics",
            "priority": "high",
            "due_date": due_date.isoformat(),
        },
    )
    assert response.status_code == 200
    assert "task_id" in response.json()

# Test: Retrieve recurring tasks
def test_get_recurring_tasks(client, db_session):
    # Create a recurring task
    due_date = datetime.utcnow() + timedelta(days=2)
    client.post(
        "/api/tasks/",
        json={
            "title": "Daily Exercise",
            "description": "Exercise for 30 minutes",
            "priority": "medium",
            "due_date": due_date.isoformat(),
            "recurrence": "DAILY",
        },
    )

    # Retrieve recurring tasks
    response = client.get("/api/tasks/recurring")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0
    assert all(task["recurrence"] is not None for task in response.json())

# Test: Mark a task as completed
def test_complete_task(client, db_session, test_user):
    # Create a task first
    due_date = datetime.utcnow() + timedelta(days=2)
    create_response = client.post(
        "/api/tasks/",
        json={
            "title": "Learn AI",
            "description": "Study machine learning basics",
            "priority": "high",
            "due_date": due_date.isoformat(),
            "user_id": test_user.id
        },
    )
    task_id = create_response.json()["task"]["id"]

    # Mark the task as completed
    response = client.post(f"/api/tasks/{task_id}/complete")
    assert response.status_code == 200
    assert response.json()["message"] == "Task marked as completed"

    # Mark the task as completed
    response = client.post(f"/api/tasks/{task_id}/complete")
    assert response.status_code == 200
    assert "message" in response.json()
    assert response.json()["message"] == "Task marked as completed"

# Test: Retrieve tasks by priority
def test_get_tasks_by_priority(client, db_session):
    # Create a high-priority task
    due_date = datetime.utcnow() + timedelta(days=2)
    client.post(
        "/api/tasks/",
        json={
            "title": "Learn AI",
            "description": "Study machine learning basics",
            "priority": "high",
            "due_date": due_date.isoformat(),
        },
    )

    # Retrieve high-priority tasks
    response = client.get("/api/tasks/priority/high")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0
    assert all(task["priority"] == "high" for task in response.json())

# Test: Retrieve overdue tasks
def test_get_overdue_tasks(client, db_session):
    # Create an overdue task
    due_date = datetime.utcnow() - timedelta(days=1)  # 1 day ago
    client.post(
        "/api/tasks/",
        json={
            "title": "Overdue Task",
            "description": "This task is overdue",
            "priority": "high",
            "due_date": due_date.isoformat(),
        },
    )

    # Retrieve overdue tasks
    response = client.get("/api/tasks/overdue")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0
    assert all(task["due_date"] < datetime.utcnow().isoformat() for task in response.json())

# Test: Retrieve tasks due today
def test_get_tasks_due_today(client, db_session):
    # Create a task due today
    due_date = datetime.utcnow().replace(hour=23, minute=59, second=59)  # End of today
    client.post(
        "/api/tasks/",
        json={
            "title": "Task Due Today",
            "description": "This task is due today",
            "priority": "high",
            "due_date": due_date.isoformat(),
        },
    )

    # Retrieve tasks due today
    response = client.get("/api/tasks/due-today")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0
    assert all(task["due_date"] >= datetime.utcnow().replace(hour=0, minute=0, second=0).isoformat() for task in response.json())

# Test: Retrieve tasks by user
def test_get_tasks_by_user(client, db_session):
    # Create a task for a specific user
    due_date = datetime.utcnow() + timedelta(days=2)
    client.post(
        "/api/tasks/",
        json={
            "title": "User Task",
            "description": "This task belongs to a specific user",
            "priority": "high",
            "due_date": due_date.isoformat(),
            "user_id": 1,  # Assuming user_id 1 exists
        },
    )

# Retrieve tasks for the user
    response = client.get("/api/tasks/user/1")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0
    assert all(task["user_id"] == 1 for task in response.json())