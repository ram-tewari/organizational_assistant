from datetime import datetime
import re

def normalize_time(time_str: str) -> str:
    """Normalize time strings to 24-hour format"""
    time_str = time_str.lower()
    if match := re.search(r"(\d+)\s*(am|pm)", time_str):
        hour, period = match.groups()
        hour = int(hour)
        if period == "pm" and hour < 12:
            hour += 12
        elif period == "am" and hour == 12:
            hour = 0
        return f"{hour:02d}:00:00"
    return time_str