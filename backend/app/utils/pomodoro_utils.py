# backend_test/app/utils/pomodoro_utils.py

from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from backend.app.utils.database import SessionLocal, PomodoroSession, PomodoroChallenge, Task, Subtask
from sqlalchemy.orm import Session
import math


def generate_task_schedules(
        task_id: int,
        task_length: int,
        due_date: datetime,
        priority: str,
        subtasks: List[str],
        db: Session
) -> List[Dict[str, Any]]:
    """
    Generate 3 different schedule options for completing a task using Pomodoro technique.
    Each schedule breaks down the task into manageable Pomodoro sessions.
    """
    # Calculate available time until deadline
    now = datetime.utcnow()
    total_available_hours = (due_date - now).total_seconds() / 3600

    # Determine Pomodoro session length based on priority
    if priority == "high":
        work_duration = 50  # 50-minute focus sessions for high priority
        break_duration = 10
    else:
        work_duration = 25  # Standard 25-minute sessions
        break_duration = 5

    # Calculate total Pomodoro sessions needed
    total_sessions = math.ceil(task_length * 60 / work_duration)

    # Generate 3 schedule options
    options = []

    # Option 1: Intensive (complete as soon as possible)
    intensive_sessions = min(total_sessions, 4)  # Max 4 sessions per day
    intensive_days = math.ceil(total_sessions / intensive_sessions)
    option1 = {
        "id": 1,
        "name": "Intensive Schedule",
        "description": f"Complete in {intensive_days} days with {intensive_sessions} sessions per day",
        "sessions_per_day": intensive_sessions,
        "schedule": []
    }

    current_day = now.date()
    sessions_remaining = total_sessions
    while sessions_remaining > 0:
        day_sessions = min(intensive_sessions, sessions_remaining)
        option1["schedule"].append({
            "date": current_day.isoformat(),
            "sessions": day_sessions,
            "session_length": work_duration,
            "break_length": break_duration
        })
        sessions_remaining -= day_sessions
        current_day += timedelta(days=1)

    options.append(option1)

    # Option 2: Balanced (even distribution)
    balanced_days = max(3, math.ceil(total_available_hours / 24 * 0.6))  # Use 60% of available time
    balanced_sessions = math.ceil(total_sessions / balanced_days)
    option2 = {
        "id": 2,
        "name": "Balanced Schedule",
        "description": f"Complete in {balanced_days} days with {balanced_sessions} sessions per day",
        "sessions_per_day": balanced_sessions,
        "schedule": []
    }

    current_day = now.date()
    sessions_remaining = total_sessions
    while sessions_remaining > 0:
        day_sessions = min(balanced_sessions, sessions_remaining)
        option2["schedule"].append({
            "date": current_day.isoformat(),
            "sessions": day_sessions,
            "session_length": work_duration,
            "break_length": break_duration
        })
        sessions_remaining -= day_sessions
        current_day += timedelta(days=1)

    options.append(option2)

    # Option 3: Relaxed (minimum daily commitment)
    relaxed_sessions = max(1, math.floor(total_sessions / total_available_hours * 8))  # About 1-2 sessions per day
    relaxed_days = math.ceil(total_sessions / relaxed_sessions)
    option3 = {
        "id": 3,
        "name": "Relaxed Schedule",
        "description": f"Complete in {relaxed_days} days with {relaxed_sessions} sessions per day",
        "sessions_per_day": relaxed_sessions,
        "schedule": []
    }

    current_day = now.date()
    sessions_remaining = total_sessions
    while sessions_remaining > 0:
        day_sessions = min(relaxed_sessions, sessions_remaining)
        option3["schedule"].append({
            "date": current_day.isoformat(),
            "sessions": day_sessions,
            "session_length": work_duration,
            "break_length": break_duration
        })
        sessions_remaining -= day_sessions
        current_day += timedelta(days=1)

    options.append(option3)

    # If subtasks exist, distribute them across sessions
    if subtasks:
        for option in options:
            subtask_idx = 0
            for day in option["schedule"]:
                day["subtasks"] = []
                for _ in range(day["sessions"]):
                    if subtask_idx < len(subtasks):
                        day["subtasks"].append(subtasks[subtask_idx])
                        subtask_idx += 1

    return options


# [Keep all existing functions below this point...]

def start_pomodoro_session(
    user_id: int,
    work_duration_minutes: int = 25,
    break_duration_minutes: int = 5,
    db: SessionLocal = None,
) -> PomodoroSession:
    """
    Start a new Pomodoro session with custom work and break durations.
    """
    session = PomodoroSession(
        start_time=datetime.utcnow(),
        status="running",
        user_id=user_id,
        work_duration_minutes=work_duration_minutes,
        break_duration_minutes=break_duration_minutes,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session

def create_pomodoro_challenge(
    user_id: int,
    title: str,
    description: str,
    target_sessions: int,
    start_date: datetime,
    end_date: datetime,
    db: SessionLocal,
) -> PomodoroChallenge:
    """
    Create a new Pomodoro challenge.
    """
    challenge = PomodoroChallenge(
        title=title,
        description=description,
        target_sessions=target_sessions,
        start_date=start_date,
        end_date=end_date,
        user_id=user_id,
    )
    db.add(challenge)
    db.commit()
    db.refresh(challenge)
    return challenge

def get_pomodoro_statistics(user_id: int, db: SessionLocal) -> Dict[str, Any]:
    """
    Get Pomodoro statistics for a user (total focus time, average session duration, etc.).
    """
    # Fetch all completed Pomodoro sessions
    sessions = (
        db.query(PomodoroSession)
        .filter(PomodoroSession.user_id == user_id, PomodoroSession.status == "completed")
        .all()
    )

    # Calculate total focus time and average session duration
    total_focus_time = sum(session.focus_time_minutes for session in sessions)
    average_session_duration = total_focus_time / len(sessions) if sessions else 0

    return {
        "total_focus_time_minutes": total_focus_time,
        "average_session_duration_minutes": average_session_duration,
        "total_sessions": len(sessions),
    }