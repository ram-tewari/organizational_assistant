# backend/app/utils/pomodoro_utils.py

from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from backend.app.utils.database import SessionLocal, PomodoroSession, PomodoroChallenge

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