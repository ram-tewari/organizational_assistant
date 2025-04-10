from unittest.mock import patch, Mock

from backend.app.voice.nlp_processor import NLPProcessor


def test_nlp_parsing(mock_nlp_processor):
    test_command = "create task Finish project"
    result = mock_nlp_processor.parse(test_command)
    assert result == {"intent": "test"}

def test_date_normalization():
    processor = NLPProcessor(api_key="test_key")
    with patch.object(processor.client.chat.completions, 'create', return_value=Mock(
        choices=[Mock(message=Mock(content='{"intent":"create_task","due_date":"tomorrow"}'))]
    )):
        result = processor.parse("dummy")
        assert "202" in result["due_date"]  # Checks ISO format

def test_invalid_command():
    processor = NLPProcessor(api_key="test_key")
    with patch.object(processor.client.chat.completions, 'create', return_value=Mock(
        choices=[Mock(message=Mock(content='INVALID_JSON'))]
    )):
        result = processor.parse("dummy")
        assert "error" in result