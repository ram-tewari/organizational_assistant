# backend_test/app/routes/study.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.utils.ai_enhancements import suggest_habits, detect_distractions, suggest_task_schedule
from backend.app.utils.database import SessionLocal, Task
from backend.app.utils.productivity_utils import generate_weekly_report, get_focus_metrics, calculate_productivity_score
from backend.app.utils.study_recommendations import analyze_study_sessions

# Create a router for study-related endpoints
router = APIRouter(prefix="/api/study", tags=["study"])

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Get study session recommendations
@router.get("/recommendations/{user_id}")
def get_study_recommendations(user_id: int, db: Session = Depends(get_db)):
    """
    Get study session recommendations for a user.
    """
    try:
        recommendations = analyze_study_sessions(user_id, db)
        return recommendations
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Get productivity score
@router.get("/productivity-score/{user_id}")
def get_productivity_score(user_id: int, db: Session = Depends(get_db)):
    """
    Get the productivity score for a user.
    """
    try:
        productivity_score = calculate_productivity_score(user_id, db)
        return {"productivity_score": productivity_score}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Get focus metrics
@router.get("/focus-metrics/{user_id}")
def get_focus_metrics_for_user(user_id: int, db: Session = Depends(get_db)):
    """
    Get focus metrics for a user.
    """
    try:
        focus_metrics = get_focus_metrics(user_id, db)
        return focus_metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Generate weekly report
@router.get("/weekly-report/{user_id}")
def get_weekly_report(user_id: int, db: Session = Depends(get_db)):
    """
    Generate a weekly productivity report for a user.
    """
    try:
        report = generate_weekly_report(user_id, db)
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Suggest task schedule
@router.post("/suggest-task-schedule/{task_id}")
def suggest_task_schedule_for_task(task_id: int, db: Session = Depends(get_db)):
    """
    Suggest an optimal time for a task.
    """
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        suggested_time = suggest_task_schedule(task.user_id, task, db)
        if suggested_time:
            return {"suggested_time": suggested_time.isoformat()}
        else:
            return {"message": "No available time slots found."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Suggest habits
@router.get("/suggest-habits/{user_id}")
def suggest_habits_for_user(user_id: int, db: Session = Depends(get_db)):
    """
    Suggest new habits for a user.
    """
    try:
        habit_suggestions = suggest_habits(user_id, db)
        return {"suggestions": habit_suggestions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Detect distractions
@router.get("/detect-distractions/{user_id}")
def detect_distractions_for_user(user_id: int, db: Session = Depends(get_db)):
    """
    Detect distractions and suggest focus-enhancing techniques.
    """
    try:
        distractions = detect_distractions(user_id, db)
        return {"distractions": distractions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))