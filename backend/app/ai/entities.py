"""
XYZ AI Backend — Entity Extraction

Extracts operational parameters (student names, dates, attendance status, etc.)
from user natural language messages using Gemini structured outputs.
"""

from typing import Optional
from pydantic import BaseModel, Field
from google.genai import types
import logging

from app.ai.gemini import gemini_service

logger = logging.getLogger("app.ai.entities")


class ExtractedEntities(BaseModel):
    """
    Structured entity representation extracted from user conversation.
    """
    student_name: Optional[str] = Field(
        default=None,
        description="Name of the student mentioned in the query (e.g. 'Rahul', 'Priya Verma')."
    )
    student_id: Optional[int] = Field(
        default=None,
        description="Explicit numeric student ID if mentioned."
    )
    date: Optional[str] = Field(
        default=None,
        description="Target date or relative date string (e.g. 'today', 'yesterday', '2026-08-16')."
    )
    status: Optional[str] = Field(
        default=None,
        description="Attendance status if applicable (must be 'present' or 'absent')."
    )
    class_name: Optional[str] = Field(
        default=None,
        description="Class or grade mentioned (e.g. 'Class 10')."
    )
    section: Optional[str] = Field(
        default=None,
        description="Section letter if mentioned (e.g. 'A', 'B')."
    )
    timeframe: Optional[str] = Field(
        default=None,
        description="Time period or timeframe (e.g. 'last month', 'this week', 'overall')."
    )


ENTITY_EXTRACTION_SYSTEM_PROMPT = """You are an entity extraction engine for a School ERP assistant.
Extract any relevant parameters needed to fulfill school operations from the user's message.

Target fields:
- student_name: Exact student name or first name if referenced (e.g. "Rahul", "Priya").
- student_id: Numeric student ID if explicitly provided.
- date: Mentioned date or relative term (e.g. "today", "yesterday", "2026-08-15").
- status: Attendance status being set ('present' or 'absent'). Normalize to lowercase.
- class_name: Grade/Class (e.g. "Class 10").
- section: Section (e.g. "A", "B").
- timeframe: Period referenced (e.g. "last month", "overall").

If a field is NOT present or cannot be determined with certainty, leave it as null.
Do NOT invent or guess missing names, dates, or values.
"""


def extract_entities(message: str, intent: Optional[str] = None, role: Optional[str] = None) -> ExtractedEntities:
    """
    Extracts structured entities from the user message using Gemini structured output.
    """
    if not message or not message.strip():
        return ExtractedEntities()

    try:
        user_prompt = f"User Message: {message}"
        if intent:
            user_prompt += f"\nDetected Intent: {intent}"

        response = gemini_service.client.models.generate_content(
            model=gemini_service.model_name,
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=ENTITY_EXTRACTION_SYSTEM_PROMPT,
                response_mime_type="application/json",
                response_schema=ExtractedEntities,
                temperature=0.0,
            ),
        )

        if hasattr(response, "parsed") and response.parsed:
            return response.parsed

        if response.text:
            return ExtractedEntities.model_validate_json(response.text)

        return ExtractedEntities()

    except Exception as e:
        logger.error(f"Error during entity extraction: {str(e)}")
        return ExtractedEntities()
