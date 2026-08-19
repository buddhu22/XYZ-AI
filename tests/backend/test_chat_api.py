"""
XYZ AI Backend — Chat API Tests (Phase 4 Updated)
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

from app.main import app

client = TestClient(app)



def test_chat_success():
    payload = {
        "user_id": 101,
        "role": "student",
        "message": "Hello assistant"
    }
    
    with patch("app.api.v1.chat.gemini_service.generate_response_with_tools", new_callable=AsyncMock) as mock_gen:
        mock_gen.return_value = "Hello! How can I help you today?"
        
        response = client.post("/api/v1/chat", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert data["response"] == "Hello! How can I help you today?"


def test_chat_empty_message():
    payload = {
        "user_id": 1,
        "role": "student",
        "message": "   "
    }
    response = client.post("/api/v1/chat", json=payload)
    assert response.status_code == 400
    assert "detail" in response.json()


def test_chat_invalid_role():
    payload = {
        "user_id": 1,
        "role": "hacker",
        "message": "Hello"
    }
    response = client.post("/api/v1/chat", json=payload)
    assert response.status_code == 400
    assert "detail" in response.json()


def test_persona_system():
    from app.ai.persona import get_persona, build_persona_system_prompt
    
    student_persona = get_persona("student")
    assert student_persona.title == "Academic Assistant"
    assert "encouraging" in student_persona.tone.lower()
    
    parent_persona = get_persona("parent")
    assert parent_persona.title == "Parent Support Assistant"
    assert "caring" in parent_persona.tone.lower()
    
    teacher_persona = get_persona("teacher")
    assert teacher_persona.title == "Teaching Assistant"
    assert "professional" in teacher_persona.tone.lower()
    
    principal_persona = get_persona("principal")
    assert principal_persona.title == "Management Assistant"
    assert "analytical" in principal_persona.tone.lower()
    
    prompt = build_persona_system_prompt("parent")
    assert "Parent Support Assistant" in prompt
    assert "XYZ AI" in prompt
