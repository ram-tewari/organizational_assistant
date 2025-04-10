# backend_test/app/utils/productivity_utils.py

from datetime import datetime, timedelta
from typing import List, Dict, Any

from sqlalchemy import func

from backend.app.utils.database import SessionLocal, Task, PomodoroSession, Habit


def calculate_productivity_score(user_id: int, db: SessionLocal) -> float:
    """
    Calculate a productivity score for the user based on completed tasks and focus time.
    """
    # Fetch completed tasks
    completed_tasks = db.query(Task).filter(Task.user_id == user_id, Task.status == "completed").count()

    # Fetch total focus time from Pomodoro sessions
    focus_time_minutes = (
        db.query(PomodoroSession)
        .filter(PomodoroSession.user_id == user_id, PomodoroSession.status == "completed")
        .with_entities(func.sum(PomodoroSession.focus_time_minutes))
        .scalar() or 0
    )

    # Calculate productivity score (weighted sum of tasks and focus time)
    productivity_score = (completed_tasks * 10) + (focus_time_minutes * 0.1)
    return productivity_score

def get_focus_metrics(user_id: int, db: SessionLocal) -> Dict[str, Any]:
    """
    Get focus metrics for the user (total focus time, average session duration).
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
    }

def generate_weekly_report(user_id: int, db: SessionLocal) -> Dict[str, Any]:
    """
    Generate a weekly productivity report for the user.
    """
    # Calculate productivity score
    productivity_score = calculate_productivity_score(user_id, db)

    # Get focus metrics
    focus_metrics = get_focus_metrics(user_id, db)

    # Fetch completed tasks
    completed_tasks = (
        db.query(Task)
        .filter(Task.user_id == user_id, Task.status == "completed")
        .all()
    )

    # Fetch habit streaks (if applicable)
    habits = (
        db.query(Habit)
        .filter(Habit.user_id == user_id)
        .all()
    )
    habit_streaks = [habit.streak for habit in habits]

    return {
        "productivity_score": productivity_score,
        "focus_metrics": focus_metrics,
        "completed_tasks": [task.title for task in completed_tasks],
        "habit_streaks": habit_streaks,
    }