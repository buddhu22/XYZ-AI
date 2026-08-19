"""
XYZ AI Backend — Speech-to-Text (STT) Service Abstraction (Phase 5)

Encapsulates audio transcription logic using Google Gemini's multimodal capabilities.
Supports all 11 required Indian and global languages natively.
"""

import logging
from google.genai import types
from google.genai.errors import APIError
from app.ai.gemini import gemini_service

logger = logging.getLogger("app.services.stt_service")

# Prompt instructing Gemini to transcribe strictly what it hears
TRANSCRIPTION_SYSTEM_INSTRUCTION = (
    "You are an expert audio transcription tool. "
    "Listen to the provided audio file carefully and return ONLY the exact text "
    "spoken, matching the language of the speaker. "
    "Do not translate, do not add conversational filler, do not add headers, "
    "and do not explain anything. If the audio contains only noise or is completely silent, "
    "return an empty response."
)

async def transcribe_audio(audio_bytes: bytes, mime_type: str = "audio/webm") -> str:
    """
    Transcribe raw audio bytes into plain text using Gemini.
    
    Args:
        audio_bytes: Raw binary content of the recorded voice file.
        mime_type: Format of the audio (defaults to audio/webm).
        
    Returns:
        Transcribed plain text string (or empty string if silence/unclear).
    """
    if not audio_bytes or len(audio_bytes) == 0:
        logger.warning("Empty audio bytes payload received for transcription.")
        return ""

    try:
        # Pass raw audio content using Part.from_bytes type matching
        audio_part = types.Part.from_bytes(
            data=audio_bytes,
            mime_type=mime_type,
        )

        config = types.GenerateContentConfig(
            system_instruction=TRANSCRIPTION_SYSTEM_INSTRUCTION,
            temperature=0.0,  # Zero temperature for deterministic transcription
        )

        # Call the wrapped generate_content (which automatically benefits from Tenacity retry!)
        response = gemini_service.client.models.generate_content(
            model=gemini_service.model_name,
            contents=[audio_part],
            config=config,
        )

        transcription = response.text.strip() if response.text else ""
        logger.info(f"Successfully transcribed audio. Result: '{transcription}'")
        return transcription

    except APIError as e:
        logger.error(f"Gemini API error during STT transcription: {str(e)}")
        # Raise standard error representing API communication issue
        raise RuntimeError("Speech-to-Text service is temporarily unavailable. Please try again.")
    except Exception as e:
        logger.error(f"Unexpected exception during STT transcription: {str(e)}")
        raise RuntimeError("Unclear audio or Speech-to-Text transcription failure.")
