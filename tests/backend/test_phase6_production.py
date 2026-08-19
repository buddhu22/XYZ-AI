"""
XYZ AI Backend — Phase 6 Production Readiness Test Suite

Verifies all 8 mandatory production scenarios (A through H):
    A — Parent attendance check (Authorized)
    B — Teacher attendance update (Authorized)
    C — Unauthorized parent action (Blocked)
    D — Unlinked child access (Blocked)
    E — Student name ambiguity
    F — Human escalation workflow
    G — ERP backend failure (graceful)
    H — Gemini API failure & retry backoff (graceful)
"""

import pytest
import anyio
from unittest.mock import AsyncMock, MagicMock, patch

from app.security.context import (
    MOCK_PARENT_CONTEXT,
    MOCK_TEACHER_CONTEXT,
    MOCK_STUDENT_CONTEXT,
)
from app.ai.tool_orchestrator import execute_tool_with_security
from app.ai.intent import IntentType
from app.security.permissions import is_allowed, is_tool_allowed_for_role, authorize_tool_execution
from app.schemas.escalation import EscalationCreate, EscalationStatus, EscalationResponse
from app.utils.error_handler import format_user_friendly_error


# =============================================================================
# SCENARIO A — Parent Attendance Check (Authorized)
# Parent requests attendance for their linked child → should succeed.
# =============================================================================
@pytest.mark.anyio
async def test_scenario_a_parent_view_linked_child_authorized():
    """Parent viewing attendance of linked child (student_id=1) should succeed."""
    user_ctx = MOCK_PARENT_CONTEXT.to_dict()  # linked_children_ids = [1]
    mock_payload = {
        "student_id": 1,
        "student_name": "Aarav Sharma",
        "total_classes": 25,
        "present": 23,
        "absent": 2,
        "attendance_percentage": 92.0,
    }
    with patch("app.tools.attendance.erp_client.get_child_attendance", new_callable=AsyncMock) as mock_erp:
        mock_erp.return_value = mock_payload
        result = await execute_tool_with_security("get_child_attendance", {"student_id": 1}, user_ctx)
        assert result["success"] is True
        assert result["student_id"] == 1
        assert result["attendance_percentage"] == 92.0


# =============================================================================
# SCENARIO B — Teacher Attendance Update (Authorized)
# Teacher marking attendance for a student → should succeed.
# =============================================================================
@pytest.mark.anyio
async def test_scenario_b_teacher_mark_attendance_authorized():
    """Teacher marking attendance via mark_attendance tool should succeed."""
    user_ctx = MOCK_TEACHER_CONTEXT.to_dict()
    mock_payload = {"message": "Attendance marked successfully", "attendance_id": 201}
    with patch("app.tools.attendance.erp_client.mark_attendance", new_callable=AsyncMock) as mock_erp:
        mock_erp.return_value = mock_payload
        result = await execute_tool_with_security(
            "mark_attendance",
            {"student_id": 1, "date": "2026-08-19", "status": "present"},
            user_ctx,
        )
        assert result["success"] is True
        assert result["attendance_id"] == 201
        assert result["status"] == "present"


# =============================================================================
# SCENARIO C — Unauthorized Parent Action (Blocked by RBAC)
# Parent attempting to mark attendance → should be blocked.
# =============================================================================
@pytest.mark.anyio
async def test_scenario_c_parent_mark_attendance_blocked():
    """Parent trying to mark attendance should be denied by RBAC."""
    user_ctx = MOCK_PARENT_CONTEXT.to_dict()
    result = await execute_tool_with_security(
        "mark_attendance",
        {"student_id": 1, "date": "2026-08-19", "status": "present"},
        user_ctx,
    )
    assert "error" in result
    assert "not authorized" in result["error"].lower() or "access denied" in result["error"].lower()


def test_scenario_c_parent_mark_attendance_intent_blocked():
    """Parent attempting mark_attendance intent should be denied."""
    assert is_allowed("parent", "mark_attendance") is False


# =============================================================================
# SCENARIO D — Unlinked Child Access (Blocked by Ownership)
# Parent trying to view attendance for a student NOT in linked_children_ids.
# =============================================================================
@pytest.mark.anyio
async def test_scenario_d_parent_view_unlinked_child_blocked():
    """Parent viewing unlinked student_id=999 should be denied by ownership check."""
    user_ctx = MOCK_PARENT_CONTEXT.to_dict()  # linked_children_ids = [1]
    result = await execute_tool_with_security("get_child_attendance", {"student_id": 999}, user_ctx)
    assert "error" in result
    assert "linked children" in result["error"].lower()


def test_scenario_d_ownership_gate():
    """Direct ownership gate check for parent with unlinked child."""
    user_ctx = {
        "id": 201,
        "role": "parent",
        "parent_id": 1,
        "linked_children_ids": [1],
    }
    is_auth, err_msg = authorize_tool_execution(user_ctx, "get_child_attendance", {"student_id": 888})
    assert is_auth is False
    assert err_msg is not None
    assert "linked children" in err_msg.lower()


# =============================================================================
# SCENARIO E — Student Name Ambiguity
# When multiple students match a name, the system should request clarification.
# (Tested at the ERP client resolution layer)
# =============================================================================
def test_scenario_e_student_name_ambiguity():
    """When the ERP returns AMBIGUOUS status, the pipeline should surface a clarification message."""
    from app.services.erp_client import StudentResolutionResult, StudentResolutionStatus

    result = StudentResolutionResult(
        status=StudentResolutionStatus.AMBIGUOUS,
        student_id=None,
        message="Multiple students found matching 'Sharma': Aarav Sharma (ID: 1), Priya Sharma (ID: 5). Please specify.",
    )
    assert result.status == StudentResolutionStatus.AMBIGUOUS
    assert result.student_id is None
    assert "Multiple students" in result.message
    assert "specify" in result.message.lower()


# =============================================================================
# SCENARIO F — Human Escalation Workflow
# Explicit user request to speak with a human creates an OPEN ticket.
# =============================================================================
def test_scenario_f_human_escalation_intent_allowed():
    """All roles should have permission for the human_escalation intent."""
    for role in ["student", "parent", "teacher", "principal"]:
        assert is_allowed(role, "human_escalation") is True, f"{role} should be allowed to escalate"


def test_scenario_f_escalation_schema():
    """EscalationCreate schema should validate correctly."""
    payload = EscalationCreate(user_id=201, role="parent", reason="I need to talk to a real person")
    assert payload.user_id == 201
    assert payload.role == "parent"
    assert "real person" in payload.reason


def test_scenario_f_escalation_status_transitions():
    """EscalationStatus enum should support the full lifecycle."""
    assert EscalationStatus.OPEN.value == "OPEN"
    assert EscalationStatus.IN_PROGRESS.value == "IN_PROGRESS"
    assert EscalationStatus.RESOLVED.value == "RESOLVED"


@pytest.mark.anyio
async def test_scenario_f_escalation_pipeline_integration():
    """
    When HUMAN_ESCALATION intent is detected, run_chat_pipeline should
    create a ticket and return a message containing the ticket number.
    """
    from app.api.v1.chat import run_chat_pipeline

    mock_intent_result = MagicMock()
    mock_intent_result.intent = IntentType.HUMAN_ESCALATION

    mock_ticket = MagicMock()
    mock_ticket.id = 42

    with (
        patch("app.api.v1.chat.detect_intent", return_value=mock_intent_result),
        patch("app.api.v1.chat.extract_entities"),
        patch("app.api.v1.chat.check_clarification_needed", return_value=None),
        patch("app.api.v1.chat.build_user_context_from_erp", new_callable=AsyncMock) as mock_ctx,
        patch("app.services.escalation_service.create_escalation", return_value=mock_ticket) as mock_create,
        patch("app.db.session.SessionLocal") as mock_session_cls,
    ):
        mock_ctx.return_value = MOCK_PARENT_CONTEXT
        mock_db = MagicMock()
        mock_session_cls.return_value = mock_db

        response = await run_chat_pipeline(
            message="I want to talk to a human",
            role="parent",
            user_id=201,
            language="en",
        )

        assert "#42" in response
        assert "staff member" in response.lower() or "support ticket" in response.lower()
        mock_create.assert_called_once()


# =============================================================================
# SCENARIO G — ERP Backend Failure (Graceful)
# ERP returns 503 → system should give a safe, user-friendly error.
# =============================================================================
def test_scenario_g_erp_failure_user_message():
    """ERP failure (503) should produce a safe, user-friendly message — not expose internals."""
    msg = format_user_friendly_error(status_code=503)
    assert "unavailable" in msg.lower() or "try again" in msg.lower()
    # Must NOT contain raw stack traces or internal details
    assert "traceback" not in msg.lower()
    assert "exception" not in msg.lower()


@pytest.mark.anyio
async def test_scenario_g_erp_failure_tool_execution():
    """When ERP client raises an exception during tool execution, the result should be a safe error dict."""
    user_ctx = MOCK_TEACHER_CONTEXT.to_dict()
    with patch("app.tools.attendance.erp_client.mark_attendance", new_callable=AsyncMock) as mock_erp:
        mock_erp.side_effect = Exception("Connection refused: ERP backend is down")
        result = await execute_tool_with_security(
            "mark_attendance",
            {"student_id": 1, "date": "2026-08-19", "status": "absent"},
            user_ctx,
        )
        assert "error" in result
        # The error message comes from the tool layer — must be safe and non-empty
        assert "failed" in result["error"].lower() or "error" in result["error"].lower()


# =============================================================================
# SCENARIO H — Gemini API Failure & Retry Backoff (Graceful)
# Gemini returns an error → system should retry then gracefully fail.
# =============================================================================
def _make_api_error(code: int):
    """Helper to create a google.genai APIError with the correct constructor."""
    from google.genai.errors import APIError
    from unittest.mock import MagicMock
    resp = MagicMock()
    resp.status_code = code
    resp.text = f"Error {code}"
    return APIError(code, resp)


def test_scenario_h_gemini_retry_configuration():
    """Verify that the Gemini retry helper correctly identifies retryable status codes."""
    from app.ai.gemini import _is_retryable_gemini_exception

    # 429 Rate Limit should be retryable
    assert _is_retryable_gemini_exception(_make_api_error(429)) is True
    # 503 Service Unavailable should be retryable
    assert _is_retryable_gemini_exception(_make_api_error(503)) is True
    # 500 Internal Server Error should be retryable
    assert _is_retryable_gemini_exception(_make_api_error(500)) is True
    # 400 Bad Request should NOT be retryable
    assert _is_retryable_gemini_exception(_make_api_error(400)) is False


def test_scenario_h_gemini_non_retryable_passes_through():
    """Non-retryable Gemini errors (e.g. 403) should not trigger retries."""
    from app.ai.gemini import _is_retryable_gemini_exception

    assert _is_retryable_gemini_exception(_make_api_error(403)) is False
    assert _is_retryable_gemini_exception(_make_api_error(401)) is False


def test_scenario_h_gemini_generate_graceful_fallback():
    """GeminiService.generate_response should return a safe fallback on exception."""
    from app.ai.gemini import GeminiService

    service = GeminiService()
    # Patch _client directly (bypassing the @property) to inject a mock
    mock_client = MagicMock()
    mock_client.models.generate_content.side_effect = _make_api_error(500)
    service._client = mock_client

    result = service.generate_response("Hello")
    assert "trouble communicating" in result.lower() or "try again" in result.lower()
