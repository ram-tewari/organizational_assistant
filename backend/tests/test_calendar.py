import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from datetime import datetime, timedelta, timezone
from backend.app.routes.calendar import router
from backend.app.utils.google_calendar import fetch_google_calendar_events, create_google_calendar_event
from backend.app.utils.schedule_parser import parse_csv_schedule, parse_ics_schedule
import os

# Create a FastAPI app and include the router
app = FastAPI()
app.include_router(router)

# Create a TestClient for the app
client = TestClient(app)

# Test data
TEST_TIMEZONE = "America/New_York"
TEST_START_TIME = datetime.now(timezone.utc).replace(hour=9, minute=0, second=0, microsecond=0)
TEST_END_TIME = TEST_START_TIME + timedelta(hours=8)

# Ensure valid Google Calendar credentials
@pytest.fixture(scope="module", autouse=True)
def setup_google_calendar():
    # Print the current working directory for debugging
    print(f"Current working directory: {os.getcwd()}")

    # Check if credentials.json exists in the root directory
    credentials_path = os.path.join(os.getcwd(), "credentials.json")
    print(f"Looking for credentials.json at: {credentials_path}")

    assert os.path.exists(credentials_path), (
        f"Google API credentials file (credentials.json) is missing. "
        f"Expected path: {credentials_path}"
    )

    # Delete existing token if it's invalid
    token_path = os.path.join(os.getcwd(), "token.json")
    if os.path.exists(token_path):
        os.remove(token_path)

# Test cases
def test_fetch_events():
    """
    Test fetching events from Google Calendar.
    """
    response = client.post(
        "/api/calendar/events",
        json={
            "start_time": TEST_START_TIME.isoformat(),
            "end_time": TEST_END_TIME.isoformat(),
            "user_timezone": TEST_TIMEZONE,
        },
    )
    assert response.status_code == 200, f"Expected 200, got {response.status_code}. Response: {response.json()}"
    assert "events" in response.json()

def test_suggest_time_for_task():
    """
    Test suggesting optimal time slots for tasks.
    """
    response = client.post(
        "/api/calendar/suggest-time",
        json={
            "start_time": TEST_START_TIME.isoformat(),
            "end_time": TEST_END_TIME.isoformat(),
            "user_timezone": TEST_TIMEZONE,
        },
    )
    assert response.status_code == 200, f"Expected 200, got {response.status_code}. Response: {response.json()}"
    assert "suggested_slots" in response.json()

def test_create_event():
    """
    Test creating an event in Google Calendar.
    """
    response = client.post(
        "/api/calendar/create-event",
        json={
            "summary": "Test Event",
            "start_time": TEST_START_TIME.isoformat(),
            "end_time": (TEST_START_TIME + timedelta(hours=1)).isoformat(),
            "description": "Test Description",
            "location": "Test Location",
            "reminders": {"reminder1": 10},
        },
    )
    assert response.status_code == 200, f"Expected 200, got {response.status_code}. Response: {response.json()}"
    assert "event_id" in response.json()

def test_block_time():
    """
    Test blocking time in Google Calendar.
    """
    response = client.post(
        "/api/calendar/block-time",
        json={
            "summary": "Test Block",
            "start_time": TEST_START_TIME.isoformat(),
            "end_time": (TEST_START_TIME + timedelta(hours=1)).isoformat(),
            "activity_type": "Test Activity",
            "description": "Test Description",
            "reminders": {"reminder1": 10},
        },
    )
    assert response.status_code == 200, f"Expected 200, got {response.status_code}. Response: {response.json()}"
    assert "event_id" in response.json()

def test_check_conflicts():
    """
    Test checking for conflicts in Google Calendar.
    """
    response = client.post(
        "/api/calendar/check-conflicts",
        json={
            "start_time": TEST_START_TIME.isoformat(),
            "end_time": (TEST_START_TIME + timedelta(hours=1)).isoformat(),
        },
    )
    assert response.status_code == 200, f"Expected 200, got {response.status_code}. Response: {response.json()}"
    assert "conflicts" in response.json()

def test_upload_schedule_csv():
    """
    Test uploading a CSV schedule and syncing it with Google Calendar.
    """
    # Create a mock CSV file
    with open("test_schedule.csv", "w") as f:
        f.write("title,description,start_time,end_time,location\n")
        f.write("Test Class,Test Description,2023-10-01T09:00:00,2023-10-01T10:00:00,Test Location\n")

    # Upload the mock CSV file
    with open("test_schedule.csv", "rb") as f:
        response = client.post(
            "/api/calendar/upload-schedule",
            files={"file": ("test_schedule.csv", f, "text/csv")},
            data={"user_timezone": TEST_TIMEZONE},
        )
    assert response.status_code == 200, f"Expected 200, got {response.status_code}. Response: {response.json()}"
    assert "num_events" in response.json()

def test_upload_schedule_ics():
    """
    Test uploading an ICS schedule and syncing it with Google Calendar.
    """
    # Create a mock ICS file
    with open("test_schedule.ics", "w") as f:
        f.write("BEGIN:VCALENDAR\n")
        f.write("BEGIN:VEVENT\n")
        f.write("SUMMARY:Test Class\n")
        f.write("DESCRIPTION:Test Description\n")
        f.write("DTSTART:20231001T090000\n")
        f.write("DTEND:20231001T100000\n")
        f.write("LOCATION:Test Location\n")
        f.write("END:VEVENT\n")
        f.write("END:VCALENDAR\n")

    # Upload the mock ICS file
    with open("test_schedule.ics", "rb") as f:
        response = client.post(
            "/api/calendar/upload-schedule",
            files={"file": ("test_schedule.ics", f, "text/calendar")},
            data={"user_timezone": TEST_TIMEZONE},
        )
    assert response.status_code == 200, f"Expected 200, got {response.status_code}. Response: {response.json()}"
    assert "num_events" in response.json()

# Clean up mock files after tests
@pytest.fixture(autouse=True)
def cleanup_files():
    yield
    import os
    if os.path.exists("test_schedule.csv"):
        os.remove("test_schedule.csv")
    if os.path.exists("test_schedule.ics"):
        os.remove("test_schedule.ics")