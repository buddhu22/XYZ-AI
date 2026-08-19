"""
STT Service Unit Test
Verifies transcribe_audio function and error handling.
"""
import pytest
from unittest.mock import MagicMock, patch
from app.services.stt_service import transcribe_audio

@pytest.mark.anyio
async def test_transcribe_audio_empty():
    # Empty audio bytes should return empty string immediately
    res = await transcribe_audio(b"")
    assert res == ""

@pytest.mark.anyio
async def test_transcribe_audio_success():
    mock_response = MagicMock()
    mock_response.text = "Hello Aarav"
    
    with patch("app.services.stt_service.gemini_service.client.models.generate_content") as mock_gen:
        mock_gen.return_value = mock_response
        res = await transcribe_audio(b"fake-audio-bytes-content")
        assert res == "Hello Aarav"
        mock_gen.assert_called_once()
