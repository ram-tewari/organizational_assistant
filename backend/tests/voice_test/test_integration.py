# backend/tests/voice/test_integration.py
from unittest.mock import patch

import pytest

from fastapi import status


def test_assistant_flow(mock_assistant, test_client):
    # Setup mock responses
    mock_assistant.voice.listen.return_value = "create task Test Project"
    mock_assistant.nlp.parse.return_value = {
        "intent": "create_task",
        "title": "Test Project",
        "due_date": "2025-04-20"
    }
    mock_assistant.api.dispatch.return_value = "Task 'Test Project' created"

    # Mock the actual API endpoint
    with patch('backend.app.routes.tasks.router') as mock_router:
        mock_router.post.return_value = {"id": 1, "title": "Test Project"}

        # Run one iteration
        with patch.object(mock_assistant.voice, 'speak') as mock_speak:
            mock_assistant.run()

            # Verify the workflow
            mock_assistant.voice.listen.assert_called_once()
            mock_assistant.nlp.parse.assert_called_once_with("create task Test Project")
            mock_assistant.api.dispatch.assert_called_once_with({
                "intent": "create_task",
                "title": "Test Project",
                "due_date": "2025-04-20"
            })
            mock_speak.assert_called_once_with("Task 'Test Project' created")