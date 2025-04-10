import speech_recognition as sr
import pyttsx3
from openai import OpenAI
from datetime import datetime, timedelta
import re
import json
from fastapi.testclient import TestClient
from backend.app.main import app  # Import your FastAPI app

# ----------------------
# Initialize Components
# ----------------------
engine = pyttsx3.init()  # TTS engine
client = TestClient(app)  # FastAPI test client (for local calls)

import os
from dotenv import load_dotenv
from .stt_tts import VoiceEngine
from .nlp_processor import NLPProcessor
from .api_dispatcher import APIDispatcher


class VoiceAssistant:
    def __init__(self):
        load_dotenv()
        self.voice = VoiceEngine()
        self.nlp = NLPProcessor(api_key=os.getenv("sk-e0c63a62bc694d079faa01fbd1a2a7d9"))
        self.api = APIDispatcher()

    def run(self):
        self.voice.speak("Voice assistant ready. How can I help?")
        while True:
            try:
                command = self.voice.listen()
                if not command:
                    continue
                if "exit" in command:
                    self.voice.speak("Goodbye!")
                    break

                parsed = self.nlp.parse(command)
                if "error" in parsed:
                    self.voice.speak("Sorry, I didn't understand that.")
                    continue

                response = self.api.dispatch(parsed)
                self.voice.speak(response)

            except KeyboardInterrupt:
                break
            except Exception as e:
                self.voice.speak(f"Error: {str(e)}")


if __name__ == "__main__":
    assistant = VoiceAssistant()
    assistant.run()