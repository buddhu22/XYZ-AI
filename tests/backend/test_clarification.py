
"""
XYZ AI Backend — Clarification Logic Tests
"""

import pytest
from unittest.mock import patch
from app.ai.intent import IntentType
from app.ai.entities import ExtractedEntities
from app.ai.clarification import (
    get_missing_fields,
    check_clarification_needed,
    build_clarification_prompt
)


def test_student_attendance_no_missing_fields():
    entities = ExtractedEntities()
    missing = get_missing_fields(IntentType.VIEW_OWN_ATTENDANCE, entities, role="student")
    assert missing == []


def test_parent_attendance_missing_student_name():
    entities = ExtractedEntities()
    missing = get_missing_fields(IntentType.VIEW_CHILD_ATTENDANCE, entities, role="parent")
    assert missing == ["student_name"]


def test_parent_attendance_with_student_name():
    entities = ExtractedEntities(student_name="Rahul")
    missing = get_missing_fields(IntentType.VIEW_CHILD_ATTENDANCE, entities, role="parent")
    assert missing == []


def test_teacher_mark_attendance_missing_date_and_status():
    entities = ExtractedEntities(student_name="Rahul")
    missing = get_missing_fields(IntentType.MARK_ATTENDANCE, entities, role="teacher")
    assert "status" in missing
    assert "date" in missing


def test_teacher_mark_attendance_all_provided():
    entities = ExtractedEntities(student_name="Rahul", status="absent", date="today")
    missing = get_missing_fields(IntentType.MARK_ATTENDANCE, entities, role="teacher")
    assert missing == []


def test_check_clarification_needed_returns_none_when_ready():
    entities = ExtractedEntities(student_name="Rahul", status="absent", date="today")
    result = check_clarification_needed(
        IntentType.MARK_ATTENDANCE,
        entities,
        role="teacher",
        original_message="Mark Rahul absent today"
    )
    assert result is None


def test_check_clarification_needed_generates_question():
    entities = ExtractedEntities(student_name="Rahul")
    
    with patch("app.ai.clarification.gemini_service.generate_response") as mock_generate:
        mock_generate.return_value = "Which date should I mark Rahul absent for?"
        
        result = check_clarification_needed(
            IntentType.MARK_ATTENDANCE,
            entities,
            role="teacher",
            original_message="Mark Rahul absent"
        )
        
        assert result == "Which date should I mark Rahul absent for?"
        mock_generate.assert_called_once()
