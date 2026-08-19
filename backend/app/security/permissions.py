"""
XYZ AI Backend — Application Authorization & Permission Layer

Enforces Role-Based Access Control (RBAC) and Resource Ownership checks
at the application layer in Python BEFORE any tool executes.

Security Guarantee:
    - Never relies solely on Gemini system prompts for security.
    - Intercepts and validates all tool execution requests.
"""

from typing import Dict, Set, Any, Tuple, Optional
import logging

logger = logging.getLogger("app.security.permissions")

# Supported system roles
VALID_ROLES: Set[str] = {"student", "parent", "teacher", "principal"}

# Mapping of roles to allowed Intent string values (Phase 3 Compatibility)
ROLE_PERMISSIONS: Dict[str, Set[str]] = {
    "student": {
        "view_own_attendance",
        "human_escalation",
        "general_query",
        "unknown",
    },
    "parent": {
        "view_child_attendance",
        "human_escalation",
        "general_query",
        "unknown",
    },
    "teacher": {
        "mark_attendance",
        "view_own_attendance",
        "view_overall_attendance",
        "human_escalation",
        "general_query",
        "unknown",
    },
    "principal": {
        "view_overall_attendance",
        "view_child_attendance",
        "view_own_attendance",
        "mark_attendance",
        "human_escalation",
        "general_query",
        "unknown",
    },
}

# Mapping of roles to allowed tool names (Phase 4 RBAC)
ROLE_TOOL_PERMISSIONS: Dict[str, Set[str]] = {
    "student": {
        "get_student_attendance",
    },
    "parent": {
        "get_child_attendance",
    },
    "teacher": {
        "get_student_attendance",
        "mark_attendance",
    },
    "principal": {
        "get_student_attendance",
        "get_child_attendance",
        "mark_attendance",
        "get_overall_attendance",
    },
}


def _normalize_intent_str(intent: Any) -> str:
    """Helper to safely convert an Intent (enum or str) to lowercase value string."""
    if hasattr(intent, "value"):
        val = intent.value
    else:
        val = str(intent)
    return str(val).lower().strip()


def is_allowed(role: str, intent: Any) -> bool:
    """Checks whether a user with the specified role is permitted to execute the given intent."""
    if not role:
        return False
    norm_role = role.lower().strip()
    allowed_intents = ROLE_PERMISSIONS.get(norm_role, set())
    intent_str = _normalize_intent_str(intent)
    return intent_str in allowed_intents


def get_permission_denied_message(role: str, intent: Any) -> str:
    """Returns a polite refusal message when intent permission is denied."""
    norm_role = role.lower().strip() if role else "user"
    intent_str = _normalize_intent_str(intent)
    
    if norm_role == "student" and intent_str == "mark_attendance":
        return "I'm sorry, but students are not authorized to mark attendance. Only teachers have permission to record attendance."
    if norm_role == "student" and intent_str == "view_overall_attendance":
        return "I'm sorry, but students cannot access school-wide attendance metrics."
    if norm_role == "parent" and intent_str == "mark_attendance":
        return "I'm sorry, but parents cannot mark attendance records."
    return f"I'm sorry, but your role as a {norm_role} does not have permission for this action."


def is_tool_allowed_for_role(role: str, tool_name: str) -> bool:
    """Check if a given role is allowed to invoke the named tool."""
    if not role:
        return False
    norm_role = role.lower().strip()
    allowed_tools = ROLE_TOOL_PERMISSIONS.get(norm_role, set())
    return tool_name in allowed_tools


def authorize_tool_execution(
    user_context: Dict[str, Any],
    tool_name: str,
    tool_kwargs: Dict[str, Any],
) -> Tuple[bool, Optional[str]]:
    """
    Enforces application-level authorization before executing a tool.
    
    Checks:
        1. Role-based tool access (RBAC)
        2. Data resource ownership (e.g. student accessing only own data)
        
    Returns:
        (is_authorized: bool, error_message: Optional[str])
    """
    role = user_context.get("role", "").lower().strip()
    student_id = user_context.get("student_id")
    parent_id = user_context.get("parent_id")
    linked_children = user_context.get("linked_children_ids", [])

    if role not in VALID_ROLES:
        logger.warning(f"Authorization denied: Unknown role '{role}'.")
        return False, f"Access denied. User role '{role}' is not recognized."

    # 1. Check RBAC tool permission
    if not is_tool_allowed_for_role(role, tool_name):
        logger.warning(f"RBAC Denied: Role '{role}' attempted to execute tool '{tool_name}'.")
        if role == "student" and tool_name == "mark_attendance":
            return False, "Access denied. Students are not authorized to mark attendance."
        if role == "student" and tool_name == "get_overall_attendance":
            return False, "Access denied. Students cannot access school-wide attendance metrics."
        if role == "parent" and tool_name == "mark_attendance":
            return False, "Access denied. Parents are not authorized to mark attendance records."
        return False, f"Access denied. Role '{role}' does not have permission to execute '{tool_name}'."

    # 2. Check Resource Ownership
    target_student_id = tool_kwargs.get("student_id")

    if role == "student":
        if target_student_id is not None and student_id is not None:
            if int(target_student_id) != int(student_id):
                logger.warning(
                    f"Ownership Denied: Student user (student_id={student_id}) tried to access student_id={target_student_id}."
                )
                return False, "Access denied. You are only authorized to view your own attendance data."

    elif role == "parent":
        if target_student_id is not None and linked_children:
            if int(target_student_id) not in [int(c) for c in linked_children]:
                logger.warning(
                    f"Ownership Denied: Parent user (parent_id={parent_id}) tried to access unlinked student_id={target_student_id}."
                )
                return False, "Access denied. You can only view attendance for your linked children."

    return True, None
