"""
XYZ AI Backend — Voice Chat API & STT Integration Tests (Phase 5 Step 4)

Verifies the convergence of Audio/STT into the existing Phase 3-4 XYZ AI pipeline:
1. Audio successfully transcribed
2. Transcribed text reaches existing XYZ AI pipeline
3. Existing intent detection is triggered
4. Existing permission layer is triggered (RBAC blocking)
5. Existing ERP tool can still execute
6. Existing text chat functionality is unaffected
7. STT failure does not call the AI pipeline
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock, patch

from app.main import app
from app.ai.intent import IntentType, IntentResult
from app.security.context import UserContext

client = TestClient(app)


# =============================================================================
# 1 & 2. Audio transcribed and exact text reaches existing XYZ AI pipeline
# =============================================================================
def test_voice_stt_transcription_and_pipeline_reach():
    """
    Test 1 & 2: Audio is transcribed and exact text reaches run_chat_pipeline.
    """
    payload = {
        "role": "teacher",
        "user_id": 1
    }
    files = {
        "audio": ("recording.webm", b"mock-audio-recording-bytes", "audio/webm")
    }
    
    with patch("app.api.v1.chat.transcribe_audio", new_callable=AsyncMock) as mock_stt, \
         patch("app.api.v1.chat.run_chat_pipeline", new_callable=AsyncMock) as mock_pipeline:
        
        # Audio transcription returns exact spoken utterance
        mock_stt.return_value = "Rahul ki attendance batao"
        mock_pipeline.return_value = "Rahul is present today with 92% attendance."
        
        response = client.post("/api/v1/chat/voice", data=payload, files=files)
        
        assert response.status_code == 200
        data = response.json()
        
        # 1. Verify STT was invoked with the exact uploaded audio bytes
        mock_stt.assert_called_once_with(b"mock-audio-recording-bytes", mime_type="audio/webm")
        
        # 2. Verify existing pipeline received the exact transcribed text (meaning unchanged)
        mock_pipeline.assert_called_once_with(
            message="Rahul ki attendance batao",
            role="teacher",
            user_id=1,
            language="en"
        )
        
        assert data["transcription"] == "Rahul ki attendance batao"
        assert data["response"] == "Rahul is present today with 92% attendance."


# =============================================================================
# 3. Existing Intent Detection is triggered for voice-transcribed query
# =============================================================================
def test_voice_triggers_existing_intent_detection():
    """
    Test 3: Voice transcription flows into existing intent detection module.
    """
    from app.ai.intent import detect_intent

    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.parsed = IntentResult(
        intent=IntentType.VIEW_CHILD_ATTENDANCE,
        confidence=0.95,
        reasoning="Voice query asking for child attendance"
    )
    mock_client.models.generate_content.return_value = mock_response

    with patch("app.ai.intent.gemini_service._client", mock_client):
        # Spoken text transcribed from audio
        spoken_text = "Rahul ki attendance batao"
        detected = detect_intent(spoken_text, role="parent")
        
        assert detected.intent == IntentType.VIEW_CHILD_ATTENDANCE
        assert detected.confidence == 0.95


# =============================================================================
# 4. Existing Permission Layer is triggered via Voice Endpoint
# =============================================================================
def test_voice_triggers_existing_permission_layer():
    """
    Test 4: Unauthorized voice command is blocked by the existing RBAC permission layer.
    Student attempts to mark attendance via voice -> Blocked.
    """
    payload = {
        "role": "student",
        "user_id": 101
    }
    files = {
        "audio": ("voice.webm", b"audio-student-mark-attendance", "audio/webm")
    }

    mock_student_context = UserContext(
        id=101,
        name="Aarav Sharma",
        email="aarav@school.edu",
        role="student",
        student_id=1,
    )

    with patch("app.api.v1.chat.transcribe_audio", new_callable=AsyncMock) as mock_stt, \
         patch("app.api.v1.chat.build_user_context_from_erp", new_callable=AsyncMock) as mock_ctx, \
         patch("app.api.v1.chat.detect_intent") as mock_intent, \
         patch("app.api.v1.chat.extract_entities") as mock_entities:
        
        mock_stt.return_value = "Mark attendance for class 10A"
        mock_ctx.return_value = mock_student_context
        mock_intent.return_value = IntentResult(
            intent=IntentType.MARK_ATTENDANCE,
            confidence=0.99,
            reasoning="Voice request to mark class attendance"
        )
        mock_entities.return_value = MagicMock(student_name=None, class_name="Class 10", date="today", status="present")

        response = client.post("/api/v1/chat/voice", data=payload, files=files)
        
        assert response.status_code == 200
        data = response.json()
        assert data["transcription"] == "Mark attendance for class 10A"
        # Must be blocked by the existing permission gate
        assert "not have permission" in data["response"].lower() or "only teachers" in data["response"].lower()


# =============================================================================
# 5. Existing ERP Tool execution can still execute from Voice query
# =============================================================================
def test_voice_can_execute_existing_erp_tool():
    """
    Test 5: Transcribed voice query executes existing ERP tools through Gemini tool calling.
    """
    payload = {
        "role": "student",
        "user_id": 101
    }
    files = {
        "audio": ("voice.webm", b"audio-view-attendance", "audio/webm")
    }

    mock_student_context = UserContext(
        id=101,
        name="Aarav Sharma",
        email="aarav@school.edu",
        role="student",
        student_id=1,
    )

    with patch("app.api.v1.chat.transcribe_audio", new_callable=AsyncMock) as mock_stt, \
         patch("app.api.v1.chat.build_user_context_from_erp", new_callable=AsyncMock) as mock_ctx, \
         patch("app.api.v1.chat.detect_intent") as mock_intent, \
         patch("app.api.v1.chat.extract_entities") as mock_entities, \
         patch("app.api.v1.chat.gemini_service.generate_response_with_tools", new_callable=AsyncMock) as mock_tools:
        
        mock_stt.return_value = "Show my attendance percentage"
        mock_ctx.return_value = mock_student_context
        mock_intent.return_value = IntentResult(
            intent=IntentType.VIEW_OWN_ATTENDANCE,
            confidence=0.99,
            reasoning="Voice request for own attendance"
        )
        mock_entities.return_value = MagicMock(student_name=None, date=None, timeframe=None)
        mock_tools.return_value = "Your current attendance is 95% with 19 out of 20 classes attended."

        response = client.post("/api/v1/chat/voice", data=payload, files=files)

        assert response.status_code == 200
        data = response.json()
        assert data["transcription"] == "Show my attendance percentage"
        assert "95%" in data["response"]
        mock_tools.assert_called_once()


# =============================================================================
# 6. Existing Text Chat functionality is completely unaffected
# =============================================================================
def test_text_chat_functionality_unaffected():
    """
    Test 6: POST /api/v1/chat continues to work unchanged.
    """
    payload = {
        "user_id": 101,
        "role": "student",
        "message": "What is the holiday schedule?"
    }
    
    with patch("app.api.v1.chat.gemini_service.generate_response_with_tools", new_callable=AsyncMock) as mock_gen, \
         patch("app.api.v1.chat.build_user_context_from_erp", new_callable=AsyncMock) as mock_ctx, \
         patch("app.api.v1.chat.detect_intent") as mock_intent, \
         patch("app.api.v1.chat.extract_entities") as mock_entities:
        
        mock_ctx.return_value = UserContext(
            id=101,
            name="Aarav Sharma",
            email="aarav@school.edu",
            role="student",
            student_id=1,
        )
        mock_intent.return_value = IntentResult(
            intent=IntentType.GENERAL_QUERY,
            confidence=0.99,
            reasoning="General question about school holidays"
        )
        mock_entities.return_value = MagicMock(student_name=None, date=None, timeframe=None)
        mock_gen.return_value = "The next school holiday is Diwali on November 1st."
        
        response = client.post("/api/v1/chat", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["response"] == "The next school holiday is Diwali on November 1st."


# =============================================================================
# 7. STT failure does NOT call the AI pipeline
# =============================================================================
def test_stt_silence_failure_does_not_call_pipeline():
    """
    Test 7a: When STT produces empty transcription (silence), AI pipeline is not called.
    """
    payload = {
        "role": "student",
        "user_id": 101
    }
    files = {
        "audio": ("silent.webm", b"silent-audio-bytes", "audio/webm")
    }

    with patch("app.api.v1.chat.transcribe_audio", new_callable=AsyncMock) as mock_stt, \
         patch("app.api.v1.chat.run_chat_pipeline", new_callable=AsyncMock) as mock_pipeline:
        
        mock_stt.return_value = "" # No transcription produced
        
        response = client.post("/api/v1/chat/voice", data=payload, files=files)
        
        assert response.status_code == 200
        data = response.json()
        assert data["transcription"] == ""
        assert "couldn't hear or understand" in data["response"]
        
        # Pipeline must NOT be called
        mock_pipeline.assert_not_called()


def test_stt_exception_does_not_call_pipeline():
    """
    Test 7b: When STT raises an exception (e.g. Gemini API error), AI pipeline is not called.
    """
    payload = {
        "role": "student",
        "user_id": 101
    }
    files = {
        "audio": ("corrupted.webm", b"corrupted-bytes", "audio/webm")
    }

    with patch("app.api.v1.chat.transcribe_audio", new_callable=AsyncMock) as mock_stt, \
         patch("app.api.v1.chat.run_chat_pipeline", new_callable=AsyncMock) as mock_pipeline:
        
        mock_stt.side_effect = RuntimeError("Speech-to-Text service is temporarily unavailable.")
        
        response = client.post("/api/v1/chat/voice", data=payload, files=files)
        
        assert response.status_code == 200
        data = response.json()
        assert data["transcription"] == ""
        assert "temporarily unavailable" in data["response"] or "service" in data["response"].lower()
        
        # Pipeline must NOT be called
        mock_pipeline.assert_not_called()


def test_chat_voice_invalid_role_rejected_early():
    """
    Invalid role is rejected immediately with 400 without running STT or pipeline.
    """
    payload = {
        "role": "hacker_role",
        "user_id": 999
    }
    files = {
        "audio": ("voice.webm", b"audio-bytes-data", "audio/webm")
    }
    with patch("app.api.v1.chat.transcribe_audio", new_callable=AsyncMock) as mock_stt:
        response = client.post("/api/v1/chat/voice", data=payload, files=files)
        assert response.status_code == 400
        assert "Invalid role" in response.json()["detail"]
        mock_stt.assert_not_called()
