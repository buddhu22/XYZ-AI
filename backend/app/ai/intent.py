"""
XYZ AI Backend — Structured Intent Detection

Uses Gemini's structured output capability (via Pydantic response_schema)
to accurately classify user queries into specific school operations.
"""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field
from google.genai import types
import logging

from app.ai.gemini import gemini_service

logger = logging.getLogger("app.ai.intent")


class IntentType(str, Enum):
    VIEW_OWN_ATTENDANCE = "VIEW_OWN_ATTENDANCE"
    VIEW_CHILD_ATTENDANCE = "VIEW_CHILD_ATTENDANCE"
    MARK_ATTENDANCE = "MARK_ATTENDANCE"
    VIEW_OVERALL_ATTENDANCE = "VIEW_OVERALL_ATTENDANCE"
    HUMAN_ESCALATION = "HUMAN_ESCALATION"
    GENERAL_QUERY = "GENERAL_QUERY"
    UNKNOWN = "UNKNOWN"


class IntentResult(BaseModel):
    """
    Structured model output representation of user intent.
    """
    intent: IntentType = Field(
        ...,
        description="The primary categorized intent of the user's message."
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score between 0.0 and 1.0 indicating certainty."
    )
    reasoning: Optional[str] = Field(
        default=None,
        description="Brief reasoning or thought process behind the intent selection."
    )


INTENT_DETECTION_SYSTEM_PROMPT = """You are an intent classification engine for a School ERP assistant.
Classify the user's natural language input into one of the following exact intents:

1. VIEW_OWN_ATTENDANCE: The user wants to check their own personal attendance (e.g. "What is my attendance?", "How many days was I present?").
2. VIEW_CHILD_ATTENDANCE: A parent or guardian is asking to check their child's attendance (e.g. "How much attendance does Rahul have?", "Show my child's attendance record").
3. MARK_ATTENDANCE: A user wants to record or mark student attendance (e.g. "Mark Rahul absent today", "Record Priya present for today").
4. VIEW_OVERALL_ATTENDANCE: A user wants to view school-wide or overall institutional attendance metrics/analytics (e.g. "What is the overall attendance?", "School attendance summary").
5. HUMAN_ESCALATION: The user explicitly wants to speak with or be connected to a human staff member (e.g. "I want to talk to a human", "Connect me to a teacher", "Escalate this", "I need to speak with someone").
6. GENERAL_QUERY: General chit-chat, greetings, questions about how the assistant works, or school inquiries not involving attendance tools (e.g. "Hello", "Who are you?", "What time does school start?").
7. UNKNOWN: The input is gibberish, completely incomprehensible, or outside the school domain.

Analyze the user's message objectively.
"""


def detect_intent(message: str, role: Optional[str] = None) -> IntentResult:
    """
    Classifies the user message into a structured IntentResult using Gemini.
    """
    if not message or not message.strip():
        return IntentResult(
            intent=IntentType.UNKNOWN,
            confidence=1.0,
            reasoning="Empty message provided."
        )

    try:
        user_prompt = f"User Message: {message}"
        if role:
            user_prompt += f"\nUser Role: {role}"

        response = gemini_service.client.models.generate_content(
            model=gemini_service.model_name,
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=INTENT_DETECTION_SYSTEM_PROMPT,
                response_mime_type="application/json",
                response_schema=IntentResult,
                temperature=0.0,
            ),
        )

        if hasattr(response, "parsed") and response.parsed:
            return response.parsed

        # Fallback if parsed is not directly populated
        if response.text:
            return IntentResult.model_validate_json(response.text)

        return IntentResult(
            intent=IntentType.UNKNOWN,
            confidence=0.5,
            reasoning="No content returned from classification model."
        )

    except Exception as e:
        logger.error(f"Error during intent detection: {str(e)}")
        # Graceful fallback: return UNKNOWN with low confidence
        return IntentResult(
            intent=IntentType.UNKNOWN,
            confidence=0.0,
            reasoning=f"Intent classification failed: {str(e)}"
        )
