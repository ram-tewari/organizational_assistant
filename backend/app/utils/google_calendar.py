# backend_test/app/utils/google_calendar.py

from datetime import datetime, timezone, timedelta
from googleapiclient.discovery import build
from backend.app.utils.google_auth import authenticate_google_calendar
import logging
from typing import List, Dict, Any, Optional

# Set up logging
logger = logging.getLogger(__name__)

def fetch_google_calendar_events(start_time: datetime, end_time: datetime) -> List[Dict[str, Any]]:
    """
    Fetch events from Google Calendar within a specified time range.
    """
    try:
        creds = authenticate_google_calendar()
        service = build("calendar", "v3", credentials=creds)

        # Convert start_time and end_time to UTC and format for the API
        time_min = start_time.astimezone(timezone.utc).isoformat()
        time_max = end_time.astimezone(timezone.utc).isoformat()

        # Fetch events within the specified time range
        events_result = (
            service.events()
            .list(
                calendarId="primary",
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )

        return events_result.get("items", [])
    except Exception as e:
        logger.error(f"Error fetching Google Calendar events: {e}")
        raise

def find_free_time_slots(events: List[Dict[str, Any]], start_time: datetime, end_time: datetime) -> List[Dict[str, datetime]]:
    """
    Find free time slots between events in the user's calendar.
    """
    free_slots = []
    current_time = start_time.astimezone(timezone.utc)

    for event in events:
        event_start = datetime.fromisoformat(event["start"].get("dateTime", event["start"].get("date"))).astimezone(timezone.utc)
        event_end = datetime.fromisoformat(event["end"].get("dateTime", event["end"].get("date"))).astimezone(timezone.utc)

        if current_time < event_start:
            free_slots.append({"start": current_time, "end": event_start})
        current_time = max(current_time, event_end)

    if current_time < end_time.astimezone(timezone.utc):
        free_slots.append({"start": current_time, "end": end_time.astimezone(timezone.utc)})

    return free_slots

def suggest_time_slots(free_slots: List[Dict[str, datetime]], task_duration_minutes: int) -> List[Dict[str, datetime]]:
    """
    Suggest optimal time slots for tasks based on free time in the user's calendar.
    """
    suggested_slots = []
    for slot in free_slots:
        slot_duration = (slot["end"] - slot["start"]).total_seconds() / 60
        if slot_duration >= task_duration_minutes:
            suggested_slots.append(slot)
    return suggested_slots

def create_google_calendar_event(
    summary: str,
    start_time: datetime,
    end_time: datetime,
    description: Optional[str] = None,
    location: Optional[str] = None,
    reminders: Optional[Dict[str, int]] = None,
) -> str:
    """
    Create an event in Google Calendar with optional reminders.
    """
    try:
        creds = authenticate_google_calendar()
        service = build("calendar", "v3", credentials=creds)

        # Convert start_time and end_time to UTC
        start_time_utc = start_time.astimezone(timezone.utc)
        end_time_utc = end_time.astimezone(timezone.utc)

        event = {
            "summary": summary,
            "description": description,
            "start": {
                "dateTime": start_time_utc.isoformat(),
                "timeZone": "UTC",
            },
            "end": {
                "dateTime": end_time_utc.isoformat(),
                "timeZone": "UTC",
            },
        }

        if location:
            event["location"] = location

        # Add reminders if provided
        if reminders:
            event["reminders"] = {
                "useDefault": False,
                "overrides": [{"method": "popup", "minutes": minutes} for minutes in reminders.values()],
            }

        # Insert the event into the primary calendar
        event = service.events().insert(calendarId="primary", body=event).execute()
        return event.get("id")
    except Exception as e:
        logger.error(f"Error creating Google Calendar event: {e}")
        raise

def block_time_in_calendar(
    summary: str,
    start_time: datetime,
    end_time: datetime,
    activity_type: str,
    description: Optional[str] = None,
    reminders: Optional[Dict[str, int]] = None,
) -> str:
    """
    Block time in Google Calendar for a specific activity (e.g., study, exercise, meeting).
    """
    try:
        # Add activity type to the event summary
        summary_with_activity = f"{activity_type}: {summary}"

        # Create the event
        event_id = create_google_calendar_event(
            summary=summary_with_activity,
            start_time=start_time,
            end_time=end_time,
            description=description,
            reminders=reminders,
        )
        return event_id
    except Exception as e:
        logger.error(f"Error blocking time in Google Calendar: {e}")
        raise

def check_for_conflicts(start_time: datetime, end_time: datetime) -> List[Dict[str, Any]]:
    """
    Check for conflicts with existing events in the user's calendar.
    """
    try:
        # Fetch events within the specified time range
        events = fetch_google_calendar_events(start_time, end_time)

        # Check for overlapping events
        conflicts = []
        for event in events:
            event_start = datetime.fromisoformat(event["start"].get("dateTime", event["start"].get("date"))).astimezone(timezone.utc)
            event_end = datetime.fromisoformat(event["end"].get("dateTime", event["end"].get("date"))).astimezone(timezone.utc)

            if (start_time < event_end) and (end_time > event_start):
                conflicts.append(event)

        return conflicts
    except Exception as e:
        logger.error(f"Error checking for conflicts: {e}")
        raise