# backend_test/app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.routes import tasks, pomodoro, calendar, files, notes, habits_goals, study #brightspace

# Create the FastAPI app
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the routers
app.include_router(tasks.router)
app.include_router(pomodoro.router)
app.include_router(calendar.router)
app.include_router(files.router)
app.include_router(notes.router)
app.include_router(habits_goals.router)
app.include_router(study.router)
#app.include_router(brightspace.router)

# Root endpoint
@app.get("/")
def read_root():
    return {"message": "Welcome to the Organizational Assistant API"}