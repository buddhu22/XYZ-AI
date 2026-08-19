"""
XYZ AI Backend — Text-to-Speech (TTS) Service (Phase 5 Step 5)

Encapsulates speech synthesis logic converting assistant text responses into
high-quality audio streams (MP3 format) encoded in Base64 for web playback.
Supports multilingual output (English, Hindi, etc.).
"""

import io
import base64
import logging
from typing import Optional
from gtts import gTTS

logger = logging.getLogger("app.services.tts_service")

# Map supported language codes to standard gTTS language codes
SUPPORTED_TTS_LANGUAGES = {
    "en": "en",
    "hi": "hi",
    "bn": "bn",
    "ta": "ta",
    "te": "te",
    "mr": "mr",
    "gu": "gu",
    "kn": "kn",
    "ml": "ml",
    "pa": "pa",
    "ur": "ur",
}


async def synthesize_speech(text: str, language: str = "en") -> Optional[str]:
    """
    Convert text to speech and return base64-encoded MP3 audio string.

    Args:
        text: Plain natural language text string to speak.
        language: ISO-639-1 language code (defaults to 'en').

    Returns:
        Base64-encoded audio/mp3 string, or None if text is empty or synthesis fails.
    """
    if not text or not text.strip():
        logger.debug("Empty text received for TTS synthesis; skipping audio generation.")
        return None

    # Clean text: remove markdown formatting, asterisk bullets, emojis that don't pronounce well
    cleaned_text = text.replace("*", "").replace("#", "").strip()
    if not cleaned_text:
        return None

    lang_code = SUPPORTED_TTS_LANGUAGES.get(language.lower().strip(), "en")

    try:
        fp = io.BytesIO()
        tts = gTTS(text=cleaned_text, lang=lang_code, slow=False)
        tts.write_to_fp(fp)
        fp.seek(0)
        
        audio_bytes = fp.read()
        if not audio_bytes:
            logger.warning("TTS generation produced empty byte payload.")
            return None

        audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
        logger.info(f"Synthesized TTS audio ({len(audio_bytes)} bytes, language='{lang_code}').")
        return audio_b64

    except Exception as e:
        # Non-blocking failure: logs error and returns None so text response is not impacted
        logger.error(f"TTS synthesis error for language '{lang_code}': {str(e)}")
        return None
