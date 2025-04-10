import speech_recognition as sr
import pyttsx3
from typing import Optional

class VoiceEngine:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.engine = pyttsx3.init()
        # Configure voice properties
        self.engine.setProperty('rate', 150)
        self.engine.setProperty('volume', 0.9)

    def listen(self) -> Optional[str]:
        """Capture and transcribe microphone input"""
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source)
            try:
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                return self.recognizer.recognize_google(audio).lower()
            except (sr.UnknownValueError, sr.WaitTimeoutError):
                return None
            except sr.RequestError as e:
                raise ConnectionError(f"Speech service error: {e}")

    def speak(self, text: str) -> None:
        """Convert text to speech"""
        self.engine.say(text)
        self.engine.runAndWait()