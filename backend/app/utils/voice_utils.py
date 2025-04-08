# backend/app/utils/voice_utils.py

import speech_recognition as sr
import pyttsx3
import spacy

# Load spaCy model for NLU
nlp = spacy.load("en_core_web_sm")

# Initialize text-to-speech engine
engine = pyttsx3.init()

def speak(text: str):
    """Convert text to speech."""
    engine.say(text)
    engine.runAndWait()

def process_command(command: str):
    """Process voice command and extract intent."""
    doc = nlp(command)
    intent = None
    entities = {}

    # Example: Extract intent and entities
    for token in doc:
        if token.text.lower() in ["create", "add", "make"]:
            intent = "create_task"
        elif token.text.lower() in ["start", "begin"]:
            intent = "start_pomodoro"
        elif token.text.lower() in ["remind", "reminder"]:
            intent = "set_reminder"
        elif token.ent_type_ == "DATE":
            entities["date"] = token.text
        elif token.ent_type_ == "TIME":
            entities["time"] = token.text

    return intent, entities

def recognize_audio(audio_file):
    """Convert audio file to text."""
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        audio = recognizer.record(source)
        command = recognizer.recognize_google(audio)
    return command