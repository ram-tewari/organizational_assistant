# backend/app/routes/pomodoro.py

from fastapi import APIRouter, Depends, HTTPException, WebSocket
from sqlalchemy.orm import Session
from datetime import datetime
from backend.app.utils.database import SessionLocal, PomodoroSession, export_pomodoro_logs, calculate_weekly_trends, \
    end_pomodoro_session
from pydantic import BaseModel
import asyncio

from backend.app.utils.pomodoro_utils import start_pomodoro_session, get_pomodoro_statistics, create_pomodoro_challenge

# Create a router for Pomodoro-related endpoints
router = APIRouter(prefix="/api/pomodoro", tags=["pomodoro"])

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Start a Pomodoro session
@router.post("/start")
def start_pomodoro(db: Session = Depends(get_db)):
    """
    Start a new Pomodoro session.
    """
    try:
        session = PomodoroSession(
            start_time=datetime.utcnow(),
            status="running",
            user_id=1,  # Replace with actual user ID from authentication
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        return {"message": "Pomodoro session started", "session_id": session.id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# End a Pomodoro session
@router.post("/end/{session_id}")
def end_pomodoro(session_id: int, db: Session = Depends(get_db)):
    """
    End a Pomodoro session.
    """
    try:
        session = db.query(PomodoroSession).filter(PomodoroSession.id == session_id).first()
        if not session:
            raise HTTPException(status_code=404, detail="Pomodoro session not found")

        session.end_time = datetime.utcnow()
        session.status = "completed"
        db.commit()
        db.refresh(session)
        return {"message": "Pomodoro session ended", "session_id": session.id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# Get all Pomodoro sessions
@router.get("/")
def get_all_pomodoro_sessions(db: Session = Depends(get_db)):
    """
    Retrieve all Pomodoro sessions.
    """
    try:
        sessions = db.query(PomodoroSession).all()
        return sessions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Export Pomodoro logs
@router.get("/export-logs")
def export_logs(db: Session = Depends(get_db)):
    """
    Export Pomodoro session logs to a JSON file.
    """
    try:
        return export_pomodoro_logs(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Get weekly productivity trends
@router.get("/weekly-trends")
def get_weekly_trends(db: Session = Depends(get_db)):
    """
    Get weekly productivity trends based on Pomodoro sessions.
    """
    try:
        return calculate_weekly_trends(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Start a Pomodoro session with custom intervals
@router.post("/start")
def start_pomodoro(
    work_duration_minutes: int = 25,
    break_duration_minutes: int = 5,
    db: Session = Depends(get_db),
):
    """
    Start a new Pomodoro session with custom work and break durations.
    """
    try:
        session = start_pomodoro_session(
            user_id=1,  # Replace with actual user ID from authentication
            work_duration_minutes=work_duration_minutes,
            break_duration_minutes=break_duration_minutes,
            db=db,
        )
        return {"message": "Pomodoro session started", "session_id": session.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class CreatePomodoroChallengeRequest(BaseModel):
    title: str
    description: str
    target_sessions: int
    start_date: datetime
    end_date: datetime

@router.post("/challenges")
def create_challenge(
    request: CreatePomodoroChallengeRequest,
    db: Session = Depends(get_db),
):
    """
    Create a new Pomodoro challenge.
    """
    try:
        challenge = create_pomodoro_challenge(
            user_id=1,  # Replace with actual user ID from authentication
            title=request.title,
            description=request.description,
            target_sessions=request.target_sessions,
            start_date=request.start_date,
            end_date=request.end_date,
            db=db,
        )
        return {"message": "Challenge created successfully", "challenge_id": challenge.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Get Pomodoro statistics
@router.get("/statistics/{user_id}")
def get_statistics(user_id: int, db: Session = Depends(get_db)):
    """
    Get Pomodoro statistics for a user.
    """
    try:
        statistics = get_pomodoro_statistics(user_id, db)
        return statistics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.websocket("/timer")
async def pomodoro_timer(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # Start a 25-minute Pomodoro session
            for i in range(25 * 60, 0, -1):
                minutes, seconds = divmod(i, 60)
                await websocket.send_text(f"Time remaining: {minutes:02}:{seconds:02}")
                await asyncio.sleep(1)
            await websocket.send_text("Time's up! Take a 5-minute break.")
            await asyncio.sleep(5 * 60)  # 5-minute break
    except Exception as e:
        await websocket.close()
        print(f"WebSocket error: {e}")