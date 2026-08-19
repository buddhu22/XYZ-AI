"""
XYZ AI Backend — ERP API Client

Asynchronous HTTP client built with `httpx` to interface securely
with the Phase 2 ERP FastAPI backend.

Handles HTTP request creation, timeout management, error wrapping,
and JSON parsing without exposing internal credentials or tracebacks.
"""

import httpx
import urllib.parse
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Any, Optional, List
from app.core.config import get_settings

settings = get_settings()


class StudentResolutionStatus(str, Enum):
    FOUND = "found"           # Exactly one match
    NOT_FOUND = "not_found"   # Zero matches
    AMBIGUOUS = "ambiguous"   # Multiple matches — DO NOT execute tool


@dataclass
class StudentResolutionResult:
    status: StudentResolutionStatus
    student_id: int | None = None
    student_name: str | None = None
    matches: List[dict] | None = None
    message: str = ""


class ERPClientError(Exception):
    """Base exception class for ERP API Client errors."""
    def __init__(self, message: str, status_code: int = 500):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class ERPClient:
    """Async HTTP Client for communicating with the Phase 2 ERP Backend APIs."""

    def __init__(self, base_url: Optional[str] = None, timeout: float = 5.0):
        self.base_url = (base_url or settings.ERP_BASE_URL).rstrip("/")
        self.timeout = timeout

    async def _request(
        self, method: str, endpoint: str, json: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generic async HTTP request helper with error & timeout handling."""
        url = f"{self.base_url}{endpoint}"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.request(method=method, url=url, json=json)
                response.raise_for_status()
                return response.json()
            except httpx.TimeoutException:
                raise ERPClientError("ERP backend request timed out.", status_code=504)
            except httpx.HTTPStatusError as exc:
                status_code = exc.response.status_code
                if status_code == 404:
                    raise ERPClientError("Requested resource not found in ERP system.", status_code=404)
                elif status_code == 403:
                    raise ERPClientError("Unauthorized action on ERP system.", status_code=403)
                elif status_code == 400:
                    detail = exc.response.json().get("detail", "Invalid request parameter.")
                    raise ERPClientError(f"ERP bad request: {detail}", status_code=400)
                else:
                    raise ERPClientError(f"ERP system error (HTTP {status_code}).", status_code=status_code)
            except httpx.RequestError:
                raise ERPClientError("Unable to connect to ERP backend service.", status_code=503)

    async def resolve_student_by_name(self, name: str) -> "StudentResolutionResult":
        """
        Resolve a student name to a numeric student_id via the Phase 2 ERP API.

        Returns a StudentResolutionResult with one of three statuses:
          - FOUND:     Exactly one student matched → safe to proceed with tool
          - NOT_FOUND: No student matched → return safe error, do not execute tool
          - AMBIGUOUS: Multiple students matched → ask user for clarification (class/section)
        """
        encoded = urllib.parse.quote(name.strip())
        try:
            results = await self._request("GET", f"/api/v1/students?name={encoded}")
        except ERPClientError:
            return StudentResolutionResult(
                status=StudentResolutionStatus.NOT_FOUND,
                message=f"I could not connect to the school system to find student '{name}'.",
            )

        if not results or not isinstance(results, list) or len(results) == 0:
            return StudentResolutionResult(
                status=StudentResolutionStatus.NOT_FOUND,
                message=f"No student named '{name}' was found in the school system.",
            )

        if len(results) == 1:
            s = results[0]
            return StudentResolutionResult(
                status=StudentResolutionStatus.FOUND,
                student_id=s["id"],
                student_name=s["name"],
                message="Student found.",
            )

        # Multiple matches — do NOT randomly pick one
        matches = [{"id": s["id"], "name": s["name"], "class": s.get("class_name"), "section": s.get("section")} for s in results]
        names_list = ", ".join(f"{s['name']} ({s.get('class_name', '')} {s.get('section', '')})" for s in results)
        return StudentResolutionResult(
            status=StudentResolutionStatus.AMBIGUOUS,
            matches=matches,
            message=f"I found {len(results)} students named '{name}': {names_list}. Please specify the student's class or section.",
        )

    async def get_student(self, student_id: int) -> Dict[str, Any]:
        """Fetch student details by student ID."""
        return await self._request("GET", f"/api/v1/students/{student_id}")

    # --- Attendance APIs ---
    async def get_student_attendance(self, student_id: int) -> Dict[str, Any]:
        """Fetch student attendance summary."""
        return await self._request("GET", f"/api/v1/attendance/student/{student_id}")

    async def get_child_attendance(self, student_id: int) -> Dict[str, Any]:
        """Fetch child attendance summary for parents."""
        return await self._request("GET", f"/api/v1/attendance/child/{student_id}")

    async def mark_attendance(
        self, student_id: int, date: str, status: str, teacher_id: int = 1
    ) -> Dict[str, Any]:
        """Mark attendance for a student."""
        payload = {
            "student_id": student_id,
            "date": date,
            "status": status,
            "marked_by_teacher_id": teacher_id,
        }
        return await self._request("POST", "/api/v1/attendance/mark", json=payload)

    async def get_overall_attendance(self) -> Dict[str, Any]:
        """Fetch school-wide overall attendance summary."""
        return await self._request("GET", "/api/v1/attendance/overall")

    # --- Parent APIs ---
    async def get_parent(self, parent_id: int) -> Dict[str, Any]:
        """Fetch parent profile and list of linked children."""
        return await self._request("GET", f"/api/v1/parents/{parent_id}")

    async def get_student_by_user(self, user_id: int) -> Dict[str, Any]:
        """Fetch student details by user ID."""
        return await self._request("GET", f"/api/v1/students/user/{user_id}")

    async def get_parent_by_user(self, user_id: int) -> Dict[str, Any]:
        """Fetch parent details by user ID."""
        return await self._request("GET", f"/api/v1/parents/user/{user_id}")

    async def get_teacher_by_user(self, user_id: int) -> Dict[str, Any]:
        """Fetch teacher details by user ID."""
        return await self._request("GET", f"/api/v1/teachers/user/{user_id}")


# Global client instance
erp_client = ERPClient()


