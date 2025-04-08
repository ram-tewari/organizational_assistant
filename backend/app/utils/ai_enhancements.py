# backend/app/utils/ai_enhancements.py

from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from backend.app.utils.database import SessionLocal, Task, Habit, PomodoroSession, Goal
from backend.app.utils.google_calendar import suggest_time_slots, fetch_google_calendar_events

# Sample data for training the model
def generate_sample_data():
    data = {
        "days_until_deadline": [1, 5, 10, 2, 7, 3],
        "task_length": [2, 5, 1, 3, 4, 2],  # Estimated task length in hours
        "priority": ["high", "medium", "low", "high", "medium", "high"],  # Target variable
    }
    return pd.DataFrame(data)

# Train a decision tree model
def train_priority_model():
    # Generate sample data
    df = generate_sample_data()

    # Convert priority labels to numerical values
    priority_map = {"high": 2, "medium": 1, "low": 0}
    df["priority"] = df["priority"].map(priority_map)

    # Features and target variable
    X = df[["days_until_deadline", "task_length"]]
    y = df["priority"]

    # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Train the model
    model = DecisionTreeClassifier()
    model.fit(X_train, y_train)

    # Evaluate the model
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Model accuracy: {accuracy * 100:.2f}%")

    return model

# Predict task priority
def predict_task_priority(model, days_until_deadline: int, task_length: int):
    priority_map = {2: "high", 1: "medium", 0: "low"}
    prediction = model.predict([[days_until_deadline, task_length]])
    return priority_map[prediction[0]]

def suggest_task_schedule(user_id: int, task: Task, db: SessionLocal) -> Optional[datetime]:
    """
    Suggest an optimal time for a task based on user availability and priorities.
    """
    try:
        # Fetch the user's calendar events
        start_time = datetime.utcnow()
        end_time = start_time + timedelta(days=7)
        events = fetch_google_calendar_events(start_time, end_time)

        # Find free time slots
        free_slots = suggest_time_slots(events, start_time, end_time)

        # Suggest the first available slot that fits the task duration
        task_duration_minutes = 60  # Default task duration (can be customized)
        for slot in free_slots:
            slot_duration = (slot["end"] - slot["start"]).total_seconds() / 60
            if slot_duration >= task_duration_minutes:
                return slot["start"]
        return None
    except Exception as e:
        # Log the error and return None
        print(f"Error suggesting task schedule: {e}")
        return None


def suggest_habits(user_id: int, db: SessionLocal) -> List[Dict[str, str]]:
    """
    Suggest new habits based on user goals and behavior.
    """
    # Fetch user goals
    goals = db.query(Goal).filter(Goal.user_id == user_id).all()

    # Suggest habits based on goal categories
    habit_suggestions = []
    for goal in goals:
        if goal.category == "health":
            habit_suggestions.append({"title": "Drink more water", "description": "Stay hydrated throughout the day."})
        elif goal.category == "productivity":
            habit_suggestions.append({"title": "Plan your day", "description": "Start each day with a plan."})
        elif goal.category == "learning":
            habit_suggestions.append({"title": "Read daily", "description": "Read for at least 30 minutes every day."})

    return habit_suggestions

def detect_distractions(user_id: int, db: SessionLocal) -> List[str]:
    """
    Detect distractions during Pomodoro sessions and suggest focus-enhancing techniques.
    """
    # Fetch recent Pomodoro sessions
    sessions = (
        db.query(PomodoroSession)
        .filter(PomodoroSession.user_id == user_id, PomodoroSession.status == "completed")
        .order_by(PomodoroSession.start_time.desc())
        .limit(5)
        .all()
    )

    # Analyze session durations (basic heuristic for distractions)
    distractions = []
    for session in sessions:
        if session.duration() < 25:  # Sessions shorter than 25 minutes may indicate distractions
            distractions.append("Short session detected. Consider minimizing distractions.")

    return distractions