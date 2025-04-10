# backend_test/tests/test_websocket.py

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

# Fixture to provide a TestClient instance
@pytest.fixture(scope="module")
def client():
    with TestClient(app) as client:
        yield client

def test_pomodoro_websocket(client):
    with client.websocket_connect("/timer") as websocket:
        data = websocket.receive_text()
        assert "Time remaining: 25:00 " in data

        for _ in range(3):  # Check 3 more messages
            data = websocket.receive_text()
            assert "Time remaining" in data