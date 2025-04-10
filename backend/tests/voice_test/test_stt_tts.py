from unittest.mock import patch


def test_voice_engine_listen_success(mock_voice_engine):
    with patch.object(mock_voice_engine.recognizer, 'recognize_google', return_value="hello"):
        assert mock_voice_engine.listen() == "hello"

def test_voice_engine_listen_failure(mock_voice_engine):
    with patch.object(mock_voice_engine.recognizer, 'recognize_google', side_effect=Exception("Error")):
        assert mock_voice_engine.listen() is None

def test_voice_engine_speak(mock_voice_engine):
    with patch.object(mock_voice_engine.engine, 'say') as mock_say:
        mock_voice_engine.speak("test")
        mock_say.assert_called_once_with("test")