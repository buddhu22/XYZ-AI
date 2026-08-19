"""
XYZ AI Backend — Entity Extraction Tests
"""

import pytest
from unittest.mock import patch, MagicMock
from app.ai.entities import extract_entities, ExtractedEntities


def test_extract_entities_empty():
    result = extract_entities("   ")
    assert result.student_name is None
    assert result.status is None
    assert result.date is None


def test_extract_entities_mark_attendance():
    mock_parsed = ExtractedEntities(
        student_name="Rahul",
        status="absent",
        date="today"
    )
    
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.parsed = mock_parsed
    mock_client.models.generate_content.return_value = mock_response
    
    with patch("app.ai.entities.gemini_service._client", mock_client):
        result = extract_entities("Mark Rahul absent today", intent="MARK_ATTENDANCE")
        
        assert result.student_name == "Rahul"
        assert result.status == "absent"
        assert result.date == "today"


def test_extract_entities_parent_query():
    mock_parsed = ExtractedEntities(
        student_name="Priya Verma",
        class_name="Class 10",
        section="A"
    )
    
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.parsed = mock_parsed
    mock_client.models.generate_content.return_value = mock_response
    
    with patch("app.ai.entities.gemini_service._client", mock_client):
        result = extract_entities("How is Priya Verma doing in Class 10 Section A?")
        
        assert result.student_name == "Priya Verma"
        assert result.class_name == "Class 10"
        assert result.section == "A"


def test_extract_entities_failure_graceful():
    mock_client = MagicMock()
    mock_client.models.generate_content.side_effect = Exception("Service error")
    
    with patch("app.ai.entities.gemini_service._client", mock_client):
        result = extract_entities("Mark student absent")
        assert result.student_name is None
