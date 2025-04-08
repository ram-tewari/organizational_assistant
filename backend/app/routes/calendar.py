# backend/app/routes/calendar.py
import os
from fastapi import APIRouter, HTTPException, UploadFile, File
from datetime import datetime
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from backend.app.utils.google_calendar import (
    fetch_google_calendar_events,
    find_free_time_slots,
    suggest_time_slots,
    create_google_calendar_event,
    block_time_in_calendar,
    check_for_conflicts,
)
from backend.app.utils.schedule_parser import parse_csv_schedule, parse_ics_schedule

# Create a router for calendar-related endpoints
router = APIRouter(prefix="/api/calendar", tags=["calendar"])

# Pydantic model for request body validation
class FetchEventsRequest(BaseModel):
    start_time: datetime
    end_time: datetime

class CreateEventRequest(BaseModel):
    summary: str
    start_time: datetime
    end_time: datetime
    description: Optional[str] = None
    location: Optional[str] = None
    reminders: Optional[Dict[str, int]] = None

class BlockTimeRequest(BaseModel):
    summary: str
    start_time: datetime
    end_time: datetime
    activity_type: str
    description: Optional[str] = None
    reminders: Optional[Dict[str, int]] = None

class CheckConflictsRequest(BaseModel):
    start_time: datetime
    end_time: datetime

# Fetch events from Google Calendar
@router.post("/events", response_model=Dict[str, List[Dict[str, Any]]])
def fetch_events(request: FetchEventsRequest):
    """
    Fetch events from Google Calendar within a specified time range.
    """
    try:
        events = fetch_google_calendar_events(request.start_time, request.end_time)
        return {"events": events}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Suggest optimal time slots for tasks
@router.post("/suggest-time", response_model=Dict[str, List[Dict[str, datetime]]])
def suggest_time_for_task(request: FetchEventsRequest):
    """
    Suggest optimal time slots for tasks based on free time in the user's calendar.
    """
    try:
        events = fetch_google_calendar_events(request.start_time, request.end_time)
        free_slots = find_free_time_slots(events, request.start_time, request.end_time)
        suggested_slots = suggest_time_slots(free_slots, 60)  # Default task duration of 60 minutes
        return {"suggested_slots": suggested_slots}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Create an event in Google Calendar
@router.post("/create-event")
def create_event(request: CreateEventRequest):
    """
    Create an event in Google Calendar.
    """
    try:
        event_id = create_google_calendar_event(
            summary=request.summary,
            start_time=request.start_time,
            end_time=request.end_time,
            description=request.description,
            location=request.location,
            reminders=request.reminders,
        )
        return {"message": "Event created successfully", "event_id": event_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Block time in Google Calendar
@router.post("/block-time")
def block_time(request: BlockTimeRequest):
    """
    Block time in Google Calendar for a specific activity.
    """
    try:
        event_id = block_time_in_calendar(
            summary=request.summary,
            start_time=request.start_time,
            end_time=request.end_time,
            activity_type=request.activity_type,
            description=request.description,
            reminders=request.reminders,
        )
        return {"message": "Time blocked successfully", "event_id": event_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Check for conflicts in Google Calendar
@router.post("/check-conflicts")
def check_conflicts(request: CheckConflictsRequest):
    """
    Check for conflicts with existing events in Google Calendar.
    """
    try:
        conflicts = check_for_conflicts(request.start_time, request.end_time)
        return {"conflicts": conflicts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#sync class schedule with google calendar
@router.post("/upload-schedule")
async def upload_schedule(file: UploadFile = File(...)):
    """
    Upload a class schedule file (CSV or ICS) and sync it with Google Calendar.
    """
    try:
        # Save the uploaded file temporarily
        file_path = f"temp_{file.filename}"
        with open(file_path, "wb") as f:
            f.write(file.file.read())

        # Parse the file based on its extension
        if file.filename.endswith(".csv"):
            events = parse_csv_schedule(file_path)
        elif file.filename.endswith(".ics"):
            events = parse_ics_schedule(file_path)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format. Use CSV or ICS.")

        # Add events to Google Calendar
        for event in events:
            create_google_calendar_event(
                summary=event["title"],
                start_time=event["start_time"],
                end_time=event["end_time"],
                description=event["description"],
            )

        # Clean up the temporary file
        os.remove(file_path)

        return {"message": "Class schedule synced successfully", "num_events": len(events)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))