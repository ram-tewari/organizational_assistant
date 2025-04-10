# backend_test/app/utils/scheduler.py

from apscheduler.schedulers.background import BackgroundScheduler
#from backend_test.app.utils.brightspace_integration import BrightspaceIntegration
from backend.app.utils.email_utils import send_email
from backend.app.utils.database import SessionLocal, Task
from datetime import datetime, timedelta
#from backend_test.app.utils.config import settings

# Initialize the scheduler
scheduler = BackgroundScheduler()
scheduler.start()

def schedule_reminder(task_id: int, user_email: str, reminder_time: datetime):
    """
    Schedule a reminder for a task.
    """
    scheduler.add_job(
        send_reminder,
        "date",
        run_date=reminder_time,
        args=[task_id, user_email],
    )

def send_reminder(task_id: int, user_email: str):
    """
    Send a reminder email for a task.
    """
    db = SessionLocal()
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        if task:
            subject = f"Reminder: {task.title}"
            body = f"Task: {task.title}\nDescription: {task.description}\nDue Date: {task.due_date}"
            send_email(user_email, subject, body)
    finally:
        db.close()

def schedule_pomodoro_reminders(sessions):
    for session in sessions:
        schedule_reminder(
            task_id=session["task_id"],
            user_email=session["user_email"],
            reminder_time=session["start"] - timedelta(minutes=15)
        )


'''def schedule_brightspace_sync(user_id: int, course_id: str, auth_token: str):
    """Schedule regular Brightspace sync"""
    brightspace = BrightspaceIntegration(
        domain=settings.BRIGHTSPACE_DEFAULT_DOMAIN,
        access_token=auth_token
    )

    # Run daily at 8 AM
    scheduler.add_job(
        brightspace.import_to_system,
        'cron',
        hour=8,
        args=[course_id, user_id],
        id=f"brightspace_sync_{user_id}_{course_id}"
    )'''