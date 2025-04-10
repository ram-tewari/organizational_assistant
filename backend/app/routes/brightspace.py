# backend_test/app/routes/brightspace.py
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from backend.app.utils.brightspace_integration import BrightspaceIntegration
from backend.app.utils.database import SessionLocal, Task
from datetime import datetime

router = APIRouter(prefix="/api/brightspace", tags=["brightspace"])


class BrightspaceAuth(BaseModel):
    domain: str
    access_token: str
    user_id: int  # Your system's user ID


class CourseImportRequest(BaseModel):
    course_id: str
    auth: BrightspaceAuth


@router.post("/import-course-tasks")
def import_course_tasks(request: CourseImportRequest):
    """Import all tasks from a Brightspace course"""
    try:
        brightspace = BrightspaceIntegration(
            domain=request.auth.domain,
            access_token=request.auth.access_token
        )

        imported_tasks = brightspace.import_to_system(
            course_id=request.course_id,
            user_id=request.auth.user_id
        )

        return {
            "message": f"Successfully imported {len(imported_tasks)} tasks",
            "imported_tasks": imported_tasks
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error during import: {str(e)}"
        )


@router.get("/tasks/{user_id}")
def get_imported_tasks(user_id: int):
    """Get all tasks imported from Brightspace for a user"""
    db = SessionLocal()
    try:
        tasks = db.query(Task).filter(
            Task.user_id == user_id,
            Task.source == "brightspace"
        ).all()

        return tasks
    finally:
        db.close()