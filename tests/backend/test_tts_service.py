"""
XYZ AI Backend — Text-to-Speech (TTS) Service Tests (Phase 5 Step 5)

Verifies:
1. Empty and whitespace text handling
2. Successful English speech synthesis to Base64 MP3
3. Successful Hindi speech synthesis to Base64 MP3
4. Markdown cleaning / formatting sanitization
5. Error resiliency (returns None instead of throwing)
"""

import pytest
import base64
from unittest.mock import patch, MagicMock

from app.services.tts_service import synthesize_speech, SUPPORTED_TTS_LANGUAGES


@pytest.mark.anyio
async def test_synthesize_speech_empty():
    assert await synthesize_speech("") is None
    assert await synthesize_speech("   ") is None
    assert await synthesize_speech(None) is None


@pytest.mark.anyio
async def test_synthesize_speech_english_success():
    text = "Hello Aarav, your attendance for this month is 95 percent."
    b64_audio = await synthesize_speech(text, language="en")
    
    assert b64_audio is not None
    assert isinstance(b64_audio, str)
    assert len(b64_audio) > 100
    
    # Verify it decodes to valid binary data
    raw_bytes = base64.b64decode(b64_audio)
    assert len(raw_bytes) > 0


@pytest.mark.anyio
async def test_synthesize_speech_hindi_success():
    text = "नमस्ते, आपकी उपस्थिति 95 प्रतिशत है।"
    b64_audio = await synthesize_speech(text, language="hi")
    
    assert b64_audio is not None
    assert isinstance(b64_audio, str)
    assert len(b64_audio) > 100


@pytest.mark.anyio
async def test_synthesize_speech_cleans_markdown():
    text = "**Attendance Summary**:\n- Total: 20\n- Present: 19 #good"
    b64_audio = await synthesize_speech(text, language="en")
    assert b64_audio is not None
    assert len(b64_audio) > 50


@pytest.mark.anyio
async def test_synthesize_speech_error_resiliency():
    with patch("app.services.tts_service.gTTS") as mock_gtts:
        mock_gtts.side_effect = Exception("TTS service network unreachable")
        
        # Must return None gracefully rather than throwing an exception
        result = await synthesize_speech("Valid text", language="en")
        assert result is None


def test_supported_tts_languages():
    assert "en" in SUPPORTED_TTS_LANGUAGES
    assert "hi" in SUPPORTED_TTS_LANGUAGES
    assert "ta" in SUPPORTED_TTS_LANGUAGES
    assert "te" in SUPPORTED_TTS_LANGUAGES
