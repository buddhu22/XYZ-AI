"""
XYZ AI Backend — AI Tool Orchestrator

Manages tool registration, authorization gating, and execution for Gemini.
Guarantees that NO tool can be executed without passing application-level RBAC & ownership checks.
"""

from typing import Dict, Any, Callable
import logging

from app.security.permissions import authorize_tool_execution
from app.tools.attendance import (
    get_student_attendance,
    get_child_attendance,
    mark_attendance,
    get_overall_attendance,
)

logger = logging.getLogger("app.ai.tool_orchestrator")

# Registry of executable tool functions
TOOL_REGISTRY: Dict[str, Callable] = {
    "get_student_attendance": get_student_attendance,
    "get_child_attendance": get_child_attendance,
    "mark_attendance": mark_attendance,
    "get_overall_attendance": get_overall_attendance,
}


async def execute_tool_with_security(
    tool_name: str,
    tool_args: Dict[str, Any],
    user_context: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Executes a tool requested by Gemini, guarded by application authorization.
    
    Flow:
        1. Validate tool existence in registry.
        2. Enforce Python authorization check (RBAC + Ownership).
        3. Execute tool via ERP API Client -> Phase 2 ERP -> PostgreSQL.
        4. Return structured result.
    """
    if tool_name not in TOOL_REGISTRY:
        logger.warning(f"Attempted execution of unknown tool '{tool_name}'.")
        return {"error": f"Unknown tool '{tool_name}'."}

    # 1. Authorize execution
    is_authorized, error_msg = authorize_tool_execution(
        user_context=user_context,
        tool_name=tool_name,
        tool_kwargs=tool_args,
    )

    if not is_authorized:
        logger.warning(
            f"Security Gate Blocked Tool '{tool_name}' for user {user_context.get('id')} ({user_context.get('role')}): {error_msg}"
        )
        return {"error": error_msg}

    # 2. Execute authorized tool
    tool_func = TOOL_REGISTRY[tool_name]
    try:
        result = await tool_func(**tool_args)
        return result
    except Exception as e:
        logger.error(f"Error executing tool '{tool_name}': {e}")
        return {"error": f"Failed to execute action '{tool_name}'."}
