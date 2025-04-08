# backend/app/routes/tasks.py

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.app.utils.database import SessionLocal, Task, Subtask, TaskTemplate, TaskPriority
from datetime import datetime, timedelta
from typing import List, Optional
from backend.app.utils.scheduler import schedule_reminder
from backend.app.utils.ai_enhancements import train_priority_model, predict_task_priority
import json

# Create a router for task-related endpoints
router = APIRouter(prefix="/api/tasks", tags=["tasks"])

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Train the priority model when the application starts
priority_model = train_priority_model()

# Pydantic models for request validation
class TaskCreateRequest(BaseModel):
    title: str
    description: str
    priority: Optional[TaskPriority] = None
    due_date: datetime
    task_length: Optional[int] = None
    reminder_enabled: Optional[bool] = False
    reminder_time: Optional[datetime] = None
    recurrence: Optional[str] = None  # New field for recurring tasks
    template_id: Optional[int] = None  # New field for task templates

class TaskUpdateRequest(BaseModel):
    title: str
    description: str
    priority: TaskPriority
    due_date: datetime
    reminder_enabled: Optional[bool] = False
    reminder_time: Optional[datetime] = None
    recurrence: Optional[str] = None  # New field for recurring tasks

class SubtaskCreateRequest(BaseModel):
    title: str
    description: Optional[str] = None

class TaskDependencyRequest(BaseModel):
    depends_on_task_id: int

class TaskTemplateCreateRequest(BaseModel):
    title: str
    description: str
    subtasks: List[str]  # List of subtask titles

# Create a new task
@router.post("/")
def create_task(request: TaskCreateRequest, user_email: str = "user@example.com", db: Session = Depends(get_db)):
    """
    Create a new task and schedule a reminder if enabled.
    If no priority is provided, use AI to suggest a priority.
    """
    try:
        # If no priority is provided, task_length is required
        if request.priority is None and request.task_length is None:
            raise HTTPException(
                status_code=400,
                detail="task_length is required when priority is not provided",
            )

        # Calculate days until deadline
        days_until_deadline = (request.due_date - datetime.utcnow()).days

        # If no priority is provided, use AI to predict it
        if request.priority is None:
            predicted_priority = predict_task_priority(
                priority_model, days_until_deadline, request.task_length
            )
            priority_map = {"high": TaskPriority.HIGH, "medium": TaskPriority.MEDIUM, "low": TaskPriority.LOW}
            priority = priority_map[predicted_priority]
        else:
            priority = request.priority

        # Create the task
        task = Task(
            title=request.title,
            description=request.description,
            priority=priority,
            due_date=request.due_date,
            reminder_enabled=request.reminder_enabled,
            reminder_time=request.reminder_time,
            recurrence=request.recurrence,
            template_id=request.template_id,
        )
        db.add(task)
        db.commit()
        db.refresh(task)

        # Schedule a reminder if enabled
        if request.reminder_enabled and request.reminder_time:
            schedule_reminder(task.id, user_email, request.reminder_time)

        return {"message": "Task created successfully", "task_id": task.id, "priority": priority.value}
    except HTTPException as e:
        raise e  # Re-raise HTTPException to return the correct status code
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# Retrieve all tasks
@router.get("/")
def get_tasks(db: Session = Depends(get_db)):
    """
    Retrieve all tasks.
    """
    tasks = db.query(Task).all()
    return tasks

# Update a task
@router.put("/{task_id}")
def update_task(task_id: int, request: TaskUpdateRequest, db: Session = Depends(get_db)):
    """
    Update an existing task.
    """
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    try:
        # Update task fields
        task.title = request.title
        task.description = request.description
        task.priority = request.priority
        task.due_date = request.due_date
        task.reminder_enabled = request.reminder_enabled
        task.reminder_time = request.reminder_time
        task.recurrence = request.recurrence

        db.commit()
        db.refresh(task)

        # Reschedule the reminder if enabled
        if request.reminder_enabled and request.reminder_time:
            schedule_reminder(task.id, "user@example.com", request.reminder_time)

        return task
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# Delete a task
@router.delete("/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    """
    Delete a task.
    """
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    try:
        db.delete(task)
        db.commit()
        return {"detail": "Task deleted"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# Retrieve tasks with description "Class"
@router.get("/classes/")
def get_class_tasks(db: Session = Depends(get_db)):
    """
    Retrieve all tasks with the description "Class".
    """
    classes = db.query(Task).filter(Task.description == "Class").all()
    return classes

# Create a new subtask
@router.post("/{task_id}/subtasks")
def create_subtask(task_id: int, request: SubtaskCreateRequest, db: Session = Depends(get_db)):
    """
    Create a new subtask for a task.
    """
    subtask = Subtask(title=request.title, description=request.description, task_id=task_id)
    db.add(subtask)
    db.commit()
    db.refresh(subtask)
    return {"message": "Subtask created successfully", "subtask_id": subtask.id}

# Retrieve all subtasks for a task
@router.get("/{task_id}/subtasks")
def get_subtasks(task_id: int, db: Session = Depends(get_db)):
    """
    Retrieve all subtasks for a task.
    """
    subtasks = db.query(Subtask).filter(Subtask.task_id == task_id).all()
    return subtasks

# Update a subtask
@router.put("/subtasks/{subtask_id}")
def update_subtask(subtask_id: int, request: SubtaskCreateRequest, db: Session = Depends(get_db)):
    """
    Update a subtask.
    """
    subtask = db.query(Subtask).filter(Subtask.id == subtask_id).first()
    if not subtask:
        raise HTTPException(status_code=404, detail="Subtask not found")

    subtask.title = request.title
    subtask.description = request.description
    db.commit()
    db.refresh(subtask)
    return subtask

# Delete a subtask
@router.delete("/subtasks/{subtask_id}")
def delete_subtask(subtask_id: int, db: Session = Depends(get_db)):
    """
    Delete a subtask.
    """
    subtask = db.query(Subtask).filter(Subtask.id == subtask_id).first()
    if not subtask:
        raise HTTPException(status_code=404, detail="Subtask not found")

    db.delete(subtask)
    db.commit()
    return {"detail": "Subtask deleted"}

# Add a task dependency
@router.post("/{task_id}/add-dependency")
def add_task_dependency(task_id: int, request: TaskDependencyRequest, db: Session = Depends(get_db)):
    """
    Add a dependency between two tasks.
    """
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    dependent_task = db.query(Task).filter(Task.id == request.depends_on_task_id).first()
    if not dependent_task:
        raise HTTPException(status_code=404, detail="Dependent task not found")

    task.depends_on = request.depends_on_task_id
    db.commit()
    db.refresh(task)
    return {"message": "Dependency added successfully"}

# Create a new task template
@router.post("/templates")
def create_task_template(request: TaskTemplateCreateRequest, db: Session = Depends(get_db)):
    """
    Create a new task template.
    """
    template = TaskTemplate(
        title=request.title,
        description=request.description,
        subtasks=json.dumps(request.subtasks),  # Store subtasks as JSON
    )
    db.add(template)
    db.commit()
    db.refresh(template)
    return {"message": "Task template created successfully", "template_id": template.id}

# Retrieve all task templates
@router.get("/templates")
def get_task_templates(db: Session = Depends(get_db)):
    """
    Retrieve all task templates.
    """
    templates = db.query(TaskTemplate).all()
    return templates

# Create a new task from a template
@router.post("/create-from-template/{template_id}")
def create_task_from_template(template_id: int, request: TaskCreateRequest, db: Session = Depends(get_db)):
    """
    Create a new task from a template.
    """
    template = db.query(TaskTemplate).filter(TaskTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Task template not found")

    # Create the task
    task = Task(
        title=request.title,
        description=request.description,
        priority=request.priority,
        due_date=request.due_date,
        reminder_enabled=request.reminder_enabled,
        reminder_time=request.reminder_time,
        recurrence=request.recurrence,
        template_id=template_id,
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    # Add subtasks from the template
    subtasks = json.loads(template.subtasks)
    for subtask_title in subtasks:
        subtask = Subtask(title=subtask_title, task_id=task.id)
        db.add(subtask)
    db.commit()

    return {"message": "Task created from template successfully", "task_id": task.id}

# Retrieve tasks with dependencies
@router.get("/{task_id}/dependencies")
def get_task_dependencies(task_id: int, db: Session = Depends(get_db)):
    """
    Retrieve all tasks that depend on the given task.
    """
    dependent_tasks = db.query(Task).filter(Task.depends_on == task_id).all()
    return dependent_tasks

# Retrieve recurring tasks
@router.get("/recurring")
def get_recurring_tasks(db: Session = Depends(get_db)):
    """
    Retrieve all recurring tasks.
    """
    recurring_tasks = db.query(Task).filter(Task.recurrence.isnot(None)).all()
    return recurring_tasks

# Mark a task as completed
@router.post("/{task_id}/complete")
def complete_task(task_id: int, db: Session = Depends(get_db)):
    """
    Mark a task as completed.
    """
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.status = "completed"
    db.commit()
    db.refresh(task)
    return {"message": "Task marked as completed", "task_id": task.id}

# Retrieve tasks by priority
@router.get("/priority/{priority}")
def get_tasks_by_priority(priority: TaskPriority, db: Session = Depends(get_db)):
    """
    Retrieve all tasks with a specific priority.
    """
    tasks = db.query(Task).filter(Task.priority == priority).all()
    return tasks

# Retrieve overdue tasks
@router.get("/overdue")
def get_overdue_tasks(db: Session = Depends(get_db)):
    """
    Retrieve all tasks that are overdue.
    """
    current_time = datetime.utcnow()
    overdue_tasks = db.query(Task).filter(Task.due_date < current_time, Task.status != "completed").all()
    return overdue_tasks

# Retrieve tasks due today
@router.get("/due-today")
def get_tasks_due_today(db: Session = Depends(get_db)):
    """
    Retrieve all tasks due today.
    """
    current_time = datetime.utcnow()
    start_of_day = current_time.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = start_of_day + timedelta(days=1)
    tasks_due_today = db.query(Task).filter(Task.due_date >= start_of_day, Task.due_date < end_of_day).all()
    return tasks_due_today

# Retrieve tasks by user
@router.get("/user/{user_id}")
def get_tasks_by_user(user_id: int, db: Session = Depends(get_db)):
    """
    Retrieve all tasks for a specific user.
    """
    tasks = db.query(Task).filter(Task.user_id == user_id).all()
    return tasks