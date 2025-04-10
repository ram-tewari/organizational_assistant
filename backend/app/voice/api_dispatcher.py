from fastapi.testclient import TestClient
from typing import Dict, Any
from datetime import datetime, timedelta
from backend.app.main import app


class APIDispatcher:
    def __init__(self):
        self.client = TestClient(app)

        # Map intents to API endpoints
        self.ENDPOINT_MAP = {
            "create_task": ("POST", "/api/tasks/"),
            "start_pomodoro": ("POST", "/api/pomodoro/start"),
            "create_event": ("POST", "/api/calendar/create-event"),
            "add_note": ("POST", "/api/notes/"),
            "upload_file": ("POST", "/api/files/upload")
        }

    def dispatch(self, command: Dict[str, Any]) -> str:
        """Execute API call based on parsed command"""
        intent = command.get("intent")
        if intent not in self.ENDPOINT_MAP:
            return "Sorry, I don't support that command yet."

        method, endpoint = self.ENDPOINT_MAP[intent]
        payload = self._build_payload(intent, command)

        try:
            response = getattr(self.client, method.lower())(endpoint, json=payload)
            return self._format_response(intent, response.json())
        except Exception as e:
            return f"Error: {str(e)}"

    def _build_payload(self, intent: str, command: Dict[str, Any]) -> Dict[str, Any]:
        """Construct API-specific payloads"""
        base_payload = {
            "user_id": 1  # Default user (replace with auth later)
        }

        if intent == "create_task":
            return {
                **base_payload,
                "title": command["title"],
                "due_date": command.get("due_date"),
                "priority": command.get("priority", "medium")
            }
        elif intent == "start_pomodoro":
            return {
                **base_payload,
                "work_duration_minutes": command.get("duration", 25)
            }
        elif intent == "create_event":
            start_time = f"{command['date']}T{command.get('time', '12:00:00')}"
            return {
                **base_payload,
                "summary": command["title"],
                "start_time": start_time,
                "end_time": (datetime.fromisoformat(start_time) + timedelta(hours=1)).isoformat()
            }
        elif intent == "add_note":
            return {
                **base_payload,
                "title": command.get("title", "Untitled Note"),
                "content": command["content"],
                "subject": command.get("subject", "General")
            }

    def _format_response(self, intent: str, response: Dict[str, Any]) -> str:
        """Convert API response to natural language"""
        if intent == "create_task":
            return f"Task '{response['title']}' created with ID {response['id']}"
        elif intent == "start_pomodoro":
            return f"Pomodoro session started for {response['work_duration_minutes']} minutes"
        elif intent == "create_event":
            return f"Event '{response['summary']}' scheduled at {response['start_time']}"
        return "Action completed successfully"