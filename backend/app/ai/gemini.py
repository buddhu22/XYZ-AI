"""
XYZ AI Backend — Gemini Service

Handles all interactions with the Google Gemini API using the official google-genai SDK,
supporting natural text generation and tool/function calling workflows.
"""

from google import genai
from google.genai import types
from google.genai.errors import APIError
from typing import Optional, Dict, Any, List
import logging
import tenacity

from app.core.config import get_settings
from app.ai.prompts import BASE_SYSTEM_INSTRUCTION

logger = logging.getLogger("app.ai.gemini")

def _is_retryable_gemini_exception(exception: Exception) -> bool:
    """Helper to detect temporary or rate-limit API errors from Gemini."""
    if isinstance(exception, APIError):
        code = getattr(exception, "code", None)
        if code in [429, 500, 503]:
            return True
        msg = str(exception).lower()
        if "429" in msg or "resource exhausted" in msg or "overloaded" in msg or "503" in msg or "500" in msg:
            return True
    return False

# Bounded retry: exponential backoff starting at 1s, max 6s, 3 attempts max
_gemini_retry_decorator = tenacity.retry(
    retry=tenacity.retry_if_exception(_is_retryable_gemini_exception),
    wait=tenacity.wait_exponential(multiplier=1.5, min=1, max=6),
    stop=tenacity.stop_after_attempt(3),
    reraise=True,
    before_sleep=lambda retry_state: logger.warning(
        f"Gemini API call failed (attempt {retry_state.attempt_number}). Retrying in {retry_state.next_action.sleep} seconds..."
    )
)


# Explicit Gemini Function Declarations for Attendance Tools
ATTENDANCE_FUNCTION_DECLARATIONS = types.Tool(
    function_declarations=[
        types.FunctionDeclaration(
            name="get_student_attendance",
            description="Fetch attendance summary (total classes, present, absent, percentage) for a student.",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "student_id": types.Schema(
                        type=types.Type.INTEGER,
                        description="The numeric student ID.",
                    )
                },
                required=["student_id"],
            ),
        ),
        types.FunctionDeclaration(
            name="get_child_attendance",
            description="Fetch attendance summary of a child student for a parent.",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "student_id": types.Schema(
                        type=types.Type.INTEGER,
                        description="The numeric student ID of the child.",
                    )
                },
                required=["student_id"],
            ),
        ),
        types.FunctionDeclaration(
            name="mark_attendance",
            description="Mark daily attendance (present/absent) for a student.",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "student_id": types.Schema(
                        type=types.Type.INTEGER,
                        description="The numeric student ID.",
                    ),
                    "date": types.Schema(
                        type=types.Type.STRING,
                        description="The date in YYYY-MM-DD format or 'today'.",
                    ),
                    "status": types.Schema(
                        type=types.Type.STRING,
                        description="Attendance status: 'present' or 'absent'.",
                    ),
                },
                required=["student_id", "date", "status"],
            ),
        ),
        types.FunctionDeclaration(
            name="get_overall_attendance",
            description="Fetch overall school-wide attendance metrics for principal/management.",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={},
            ),
        ),
    ]
)


class GeminiService:
    """
    Service class to handle connection and interactions with the Gemini API.
    """
    def __init__(self):
        self.settings = get_settings()
        self.api_key = self.settings.GEMINI_API_KEY
        self.model_name = self.settings.GEMINI_MODEL
        self._client = None

    @property
    def client(self) -> genai.Client:
        """Lazily initialize and return the Google GenAI Client with dynamic retry wrapping."""
        if self._client is None:
            if not self.api_key:
                logger.error("GEMINI_API_KEY is missing from environment/config settings.")
                raise ValueError("Gemini API key is not configured. Please set GEMINI_API_KEY in the .env file.")
            
            client_inst = genai.Client(api_key=self.api_key)
            
            # Wrap the generate_content method dynamically to apply tenacity retry
            orig_generate = client_inst.models.generate_content
            
            @_gemini_retry_decorator
            def wrapped_generate(*args, **kwargs):
                return orig_generate(*args, **kwargs)
                
            client_inst.models.generate_content = wrapped_generate
            self._client = client_inst
            
        return self._client


    def generate_response(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        """Generates a simple natural text response from the configured Gemini model."""
        try:
            instruction = system_instruction if system_instruction is not None else BASE_SYSTEM_INSTRUCTION
            config = types.GenerateContentConfig(
                system_instruction=instruction,
                temperature=0.7,
            )
            
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=config
            )
            
            if not response.text:
                logger.warning("Gemini returned an empty response.")
                return "I received an empty response. How can I assist you further?"
                
            return response.text
            
        except APIError as e:
            logger.error(f"Gemini API Error: {str(e)}")
            return "I'm having trouble communicating with my AI model right now. Please try again in a moment."
        except Exception as e:
            logger.error(f"Unexpected error in Gemini Service: {str(e)}")
            return "An unexpected error occurred while processing your request. Please try again."

    async def generate_response_with_tools(
        self,
        prompt: str,
        user_context: Dict[str, Any],
        system_instruction: Optional[str] = None,
    ) -> str:
        """
        Executes a complete Tool-Calling conversation loop with Gemini.
        
        Flow:
            1. Pass query & Function Declarations to Gemini.
            2. If Gemini requests tool execution:
               a. If tool needs student_id and we only have a name:
                  → Resolve name via ERP API (NOT direct DB)
                  → Handle: 0 matches (not found), 1 match (proceed), N matches (ask clarification)
               b. Pass request through application permission gate (RBAC + Ownership).
               c. Execute tool via ERP API Client -> PostgreSQL.
               d. Feed tool result back to Gemini to synthesize natural response.
            3. Return final response text.
        """
        try:
            from app.ai.tool_orchestrator import execute_tool_with_security
            from app.services.erp_client import erp_client as _erp_client, StudentResolutionStatus

            # Enrich system instruction with user context so Gemini knows student_id, etc.
            ctx_info = f"\nUser Context: Role={user_context.get('role')}, Student_ID={user_context.get('student_id')}, Name={user_context.get('name')}"
            instruction = (system_instruction or BASE_SYSTEM_INSTRUCTION) + ctx_info

            config = types.GenerateContentConfig(
                system_instruction=instruction,
                temperature=0.2,
                tools=[ATTENDANCE_FUNCTION_DECLARATIONS],
            )

            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=config
            )

            # Check if Gemini triggered function calls
            if response.function_calls:
                tool_results = []
                for call in response.function_calls:
                    logger.info(f"Gemini requested tool execution: '{call.name}' with args {call.args}")

                    # Convert args to standard Python types
                    raw_args = dict(call.args) if call.args else {}
                    tool_args = {}
                    for k, v in raw_args.items():
                        if isinstance(v, float) and v.is_integer():
                            tool_args[k] = int(v)
                        else:
                            tool_args[k] = v

                    # ─── NAME-TO-ID RESOLUTION ───────────────────────────────────────
                    # If Gemini passed student_name but not student_id, resolve it first
                    if "student_id" not in tool_args or tool_args.get("student_id") is None:
                        # Try to use the authenticated user's own student_id
                        if user_context.get("student_id"):
                            tool_args["student_id"] = user_context.get("student_id")
                        elif "student_name" in tool_args and tool_args["student_name"]:
                            # Resolve by name via ERP API (correct architecture)
                            resolution = await _erp_client.resolve_student_by_name(tool_args.pop("student_name"))
                            if resolution.status == StudentResolutionStatus.NOT_FOUND:
                                return resolution.message
                            if resolution.status == StudentResolutionStatus.AMBIGUOUS:
                                return resolution.message
                            # FOUND — inject the confirmed student_id
                            tool_args["student_id"] = resolution.student_id
                        # Also try to extract from the raw prompt entities
                        else:
                            # Try extracting from last word in prompt as fallback
                            pass

                    # Security gate check & execution
                    result = await execute_tool_with_security(
                        tool_name=call.name,
                        tool_args=tool_args,
                        user_context=user_context,
                    )
                    tool_results.append((call.name, result))

                # Synthesize final natural language answer using tool results
                synthesis_prompt = (
                    f"User Query: {prompt}\n"
                    f"Tool Execution Results: {tool_results}\n"
                    "Please provide a polite, natural language response to the user based on these results."
                )

                final_response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=synthesis_prompt,
                    config=types.GenerateContentConfig(system_instruction=instruction, temperature=0.7)
                )
                return final_response.text or "Completed requested action."

            return response.text or "I have processed your request."

        except APIError as e:
            logger.error(f"Gemini API Tool Calling Error: {str(e)}")
            return "I'm having trouble communicating with my AI model right now. Please try again."
        except Exception as e:
            logger.error(f"Unexpected error in Gemini Tool Calling: {str(e)}")
            return "An error occurred while executing the requested action."



# Singleton instance
gemini_service = GeminiService()
