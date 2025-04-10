import pytest
from unittest.mock import Mock, patch, MagicMock
from backend.app.voice.stt_tts import VoiceEngine
from backend.app.voice.nlp_processor import NLPProcessor
from backend.app.voice.api_dispatcher import APIDispatcher
from fastapi.testclient import TestClient
from backend.app.main import app


@pytest.fixture
def mock_voice_engine():
    with patch('speech_recognition.Microphone') as mock_mic, \
         patch('pyttsx3.init') as mock_tts:
        engine = VoiceEngine()
        engine.recognizer.recognize_google = Mock(return_value="test command")
        yield engine

@pytest.fixture
def mock_nlp_processor():
    processor = NLPProcessor(api_key="test_key")
    processor.client.chat.completions.create = Mock(return_value=Mock(
        choices=[Mock(message=Mock(content='{"intent":"test"}'))]
    ))
    return processor

@pytest.fixture
def mock_api_dispatcher():
    dispatcher = APIDispatcher()
    dispatcher.client = Mock()
    dispatcher.client.post.return_value.json.return_value = {"status": "success"}
    return dispatcher


# backend/tests/voice/conftest.py



@pytest.fixture
def test_client():
    return TestClient(app)


@pytest.fixture
def mock_assistant():
    with patch('backend.app.voice.voice_assistant.VoiceEngine'), \
            patch('backend.app.voice.voice_assistant.NLPProcessor'), \
            patch('backend.app.voice.voice_assistant.APIDispatcher'):
        from backend.app.voice.voice_assistant import VoiceAssistant
        assistant = VoiceAssistant()

        # Configure default mocks
        assistant.voice = MagicMock()
        assistant.nlp = MagicMock()
        assistant.api = MagicMock()

        yield assistant