def test_task_creation_dispatch(mock_api_dispatcher):
    # Configure mock response for task creation
    mock_api_dispatcher.client.post.return_value.json.return_value = {
        "id": 1,
        "title": "Test Task",
        "status": "created"
    }

    command = {
        "intent": "create_task",
        "title": "Test Task",  # Make sure required field is included
        "due_date": "2025-04-20"
    }
    result = mock_api_dispatcher.dispatch(command)
    assert "Test Task" in result  # Now checks for title in success response
    mock_api_dispatcher.client.post.assert_called_once_with(
        "/api/tasks/",
        json={
            "title": "Test Task",
            "due_date": "2025-04-20",
            "priority": "medium",  # Default value
            "user_id": 1
        }
    )


def test_pomodoro_dispatch(mock_api_dispatcher):
    # Configure mock response for pomodoro
    mock_api_dispatcher.client.post.return_value.json.return_value = {
        "id": 1,
        "work_duration_minutes": 30,
        "status": "started"
    }

    command = {
        "intent": "start_pomodoro",
        "duration": 30  # Make sure required field is included
    }
    result = mock_api_dispatcher.dispatch(command)
    assert "30" in result  # Checks for duration in success response
    mock_api_dispatcher.client.post.assert_called_once_with(
        "/api/pomodoro/start",
        json={
            "work_duration_minutes": 30,
            "user_id": 1
        }
    )


def test_unknown_command(mock_api_dispatcher):
    result = mock_api_dispatcher.dispatch({"intent": "unknown"})
    assert "don't support" in result.lower()