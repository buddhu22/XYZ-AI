"""
XYZ AI Backend — Application Permissions Tests
"""

import pytest
from app.ai.intent import IntentType
from app.security.permissions import is_allowed, get_permission_denied_message


def test_student_permissions():
    # Student ALLOWED to view own attendance
    assert is_allowed("student", IntentType.VIEW_OWN_ATTENDANCE) is True
    assert is_allowed("student", IntentType.GENERAL_QUERY) is True
    
    # Student DENIED from marking or viewing overall/child attendance
    assert is_allowed("student", IntentType.MARK_ATTENDANCE) is False
    assert is_allowed("student", IntentType.VIEW_OVERALL_ATTENDANCE) is False
    assert is_allowed("student", IntentType.VIEW_CHILD_ATTENDANCE) is False


def test_parent_permissions():
    # Parent ALLOWED to view child attendance
    assert is_allowed("parent", IntentType.VIEW_CHILD_ATTENDANCE) is True
    assert is_allowed("parent", IntentType.GENERAL_QUERY) is True
    
    # Parent DENIED from marking attendance or viewing school-wide analytics
    assert is_allowed("parent", IntentType.MARK_ATTENDANCE) is False
    assert is_allowed("parent", IntentType.VIEW_OVERALL_ATTENDANCE) is False


def test_teacher_permissions():
    # Teacher ALLOWED to mark attendance and view records
    assert is_allowed("teacher", IntentType.MARK_ATTENDANCE) is True
    assert is_allowed("teacher", IntentType.VIEW_OWN_ATTENDANCE) is True
    assert is_allowed("teacher", IntentType.VIEW_OVERALL_ATTENDANCE) is True


def test_principal_permissions():
    # Principal ALLOWED to view overall attendance and perform management actions
    assert is_allowed("principal", IntentType.VIEW_OVERALL_ATTENDANCE) is True
    assert is_allowed("principal", IntentType.VIEW_CHILD_ATTENDANCE) is True
    assert is_allowed("principal", IntentType.MARK_ATTENDANCE) is True


def test_permission_denied_message():
    msg = get_permission_denied_message("student", IntentType.MARK_ATTENDANCE)
    assert "students are not authorized" in msg.lower()
    
    msg_parent = get_permission_denied_message("parent", IntentType.MARK_ATTENDANCE)
    assert "parents cannot mark attendance" in msg_parent.lower()
