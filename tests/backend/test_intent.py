"""
XYZ AI Backend — Intent Detection Tests
"""

import pytest
from unittest.mock import patch, MagicMock
from app.ai.intent import detect_intent, IntentType, IntentResult


def test_detect_intent_empty_message():
    result = detect_intent("   ")
    assert result.intent == IntentType.UNKNOWN
    assert result.confidence == 1.0


def test_detect_intent_view_own_attendance():
    mock_parsed = IntentResult(
        intent=IntentType.VIEW_OWN_ATTENDANCE,
        confidence=0.98,
        reasoning="Student asking about their own attendance"
    )
    
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.parsed = mock_parsed
    mock_client.models.generate_content.return_value = mock_response
    
    with patch("app.ai.intent.gemini_service._client", mock_client):
        result = detect_intent("What is my attendance?", role="student")
        
        assert result.intent == IntentType.VIEW_OWN_ATTENDANCE
        assert result.confidence == 0.98
        assert "own attendance" in result.reasoning


def test_detect_intent_mark_attendance():
    mock_parsed = IntentResult(
        intent=IntentType.MARK_ATTENDANCE,
        confidence=0.95,
        reasoning="Teacher requesting to record absent status"
    )
    
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.parsed = mock_parsed
    mock_client.models.generate_content.return_value = mock_response
    
    with patch("app.ai.intent.gemini_service._client", mock_client):
        result = detect_intent("Mark Rahul absent today", role="teacher")
        
        assert result.intent == IntentType.MARK_ATTENDANCE
        assert result.confidence == 0.95


def test_detect_intent_api_failure_fallback():
    mock_client = MagicMock()
    mock_client.models.generate_content.side_effect = Exception("API connection dropped")
    
    with patch("app.ai.intent.gemini_service._client", mock_client):
        result = detect_intent("Check attendance")
        
        assert result.intent == IntentType.UNKNOWN
        assert result.confidence == 0.0
        assert "classification failed" in result.reasoning.lower()
