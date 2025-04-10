# backend_test/app/utils/brightspace_integration.py
'''import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from fastapi import HTTPException
from backend_test.app.utils.database import SessionLocal, Task
from backend_test.app.utils.scheduler import schedule_reminder
from backend_test.app.utils.google_calendar import create_google_calendar_event


class BrightspaceIntegration:
    def __init__(self, domain: str, access_token: str, le_version: str = "1.48"):
        self.base_url = f"{domain}/d2l/api/le/{le_version}"
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

    def _make_request(self, url: str) -> Optional[Dict]:
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise HTTPException(
                status_code=502,
                detail=f"Brightspace API error: {str(e)}"
            )

    def get_course_content(self, course_id: str) -> List[Dict]:
        """Fetch all content modules and topics from a Brightspace course"""
        url = f"{self.base_url}/{course_id}/content/root/"
        return self._make_request(url)

    def get_module_structure(self, course_id: str, module_id: str) -> List[Dict]:
        """Get structure of a specific module"""
        url = f"{self.base_url}/{course_id}/content/modules/{module_id}/structure/"
        return self._make_request(url)

    def get_assignments(self, course_id: str) -> List[Dict]:
        """Fetch assignments from the dropbox tool"""
        url = f"{self.base_url}/{course_id}/dropbox/folders/"
        return self._make_request(url)

    def extract_tasks(self, course_id: str) -> List[Dict]:
        """Extract all tasks (content and assignments) from a course"""
        content = self.get_course_content(course_id)
        if not content:
            return []

        tasks = []
        modules = [item for item in content if item.get("Type") == 0]  # Modules

        for module in modules:
            structure = self.get_module_structure(course_id, module["Id"])
            if not structure:
                continue

            for topic in structure:
                if topic.get("Type") == 1:  # Topic
                    task = {
                        "title": f"{module['Title']}: {topic['Title']}",
                        "description": topic.get("Description", {}).get("Text", ""),
                        "due_date": topic.get("DueDate"),
                        "start_date": topic.get("StartDate"),
                        "source": "brightspace_content",
                        "metadata": {
                            "module_id": module["Id"],
                            "topic_id": topic["Id"],
                            "url": topic.get("Url")
                        }
                    }
                    tasks.append(task)

        assignments = self.get_assignments(course_id) or []
        for assignment in assignments:
            tasks.append({
                "title": f"Assignment: {assignment['Name']}",
                "description": assignment.get("Instructions", {}).get("Text", ""),
                "due_date": assignment.get("DueDate"),
                "start_date": assignment.get("StartDate"),
                "source": "brightspace_assignment",
                "metadata": {
                    "folder_id": assignment["Id"]
                }
            })

        return tasks

    def import_to_system(self, course_id: str, user_id: int) -> List[Task]:
        """Import tasks from Brightspace to our system"""
        brightspace_tasks = self.extract_tasks(course_id)
        db = SessionLocal()
        created_tasks = []

        try:
            for task_data in brightspace_tasks:
                # Skip if no due date
                if not task_data.get("due_date"):
                    continue

                # Create the task
                task = Task(
                    title=task_data["title"],
                    description=task_data["description"],
                    due_date=datetime.fromisoformat(task_data["due_date"]),
                    user_id=user_id,
                    source="brightspace",
                    source_metadata=task_data["metadata"],
                    priority=self._determine_priority(task_data["due_date"])
                )

                db.add(task)
                db.commit()
                db.refresh(task)
                created_tasks.append(task)

                # Schedule calendar event and reminder
                self._schedule_related_events(task, user_id)

            return created_tasks
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Failed to import tasks: {str(e)}"
            )
        finally:
            db.close()

    def _determine_priority(self, due_date_str: str) -> str:
        """Determine task priority based on due date"""
        due_date = datetime.fromisoformat(due_date_str)
        days_until_due = (due_date - datetime.now()).days

        if days_until_due <= 3:
            return "high"
        elif days_until_due <= 7:
            return "medium"
        return "low"

    def _schedule_related_events(self, task: Task, user_id: int):
        """Create calendar events and reminders for the task"""
        # Create calendar event 1 day before due date as reminder
        reminder_time = task.due_date - timedelta(days=1)

        # Schedule email reminder
        schedule_reminder(
            task_id=task.id,
            user_email=f"user_{user_id}@example.com",  # Replace with actual user email
            reminder_time=reminder_time
        )

        # Create calendar blocking event
        create_google_calendar_event(
            summary=f"Study: {task.title}",
            start_time=reminder_time,
            end_time=reminder_time + timedelta(hours=2),
            description=task.description,
            reminders={"reminder": 60}  # 1 hour before
        )'''