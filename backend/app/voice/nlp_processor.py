from openai import OpenAI
from datetime import datetime, timedelta
import re
import json
from typing import Dict, Any
from .utils import normalize_time


class NLPProcessor:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

        self.SYSTEM_PROMPT = """You are a voice command parser for a productivity app. 
        Return JSON with these possible intents: 
        - create_task: {title, due_date, priority}
        - start_pomodoro: {duration}
        - create_event: {title, start_time, end_time}
        - add_note: {title, content, subject}
        - upload_file: {file_path}
        Example: {"intent":"create_task","title":"Finish report","due_date":"2025-04-15"}"""

    def parse(self, command: str) -> Dict[str, Any]:
        """Convert natural language to structured command"""
        response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": command},
            ],
            response_format={"type": "json_object"},
            temperature=0.3  # Reduce creativity for consistent parsing
        )

        try:
            parsed = json.loads(response.choices[0].message.content)
            return self._post_process(parsed)
        except json.JSONDecodeError:
            return {"error": "Failed to parse command"}

    def _post_process(self, parsed: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize dates/times and validate structure"""
        if "due_date" in parsed:
            parsed["due_date"] = self._normalize_date(parsed["due_date"])
        if "start_time" in parsed:
            parsed["start_time"] = normalize_time(parsed["start_time"])
        return parsed

    def _normalize_date(self, date_str: str) -> str:
        """Convert relative dates to ISO format"""
        date_str = date_str.lower()
        if date_str == "today":
            return datetime.now().strftime("%Y-%m-%d")
        elif date_str == "tomorrow":
            return (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        return date_str