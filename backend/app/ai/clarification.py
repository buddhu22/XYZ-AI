"""
XYZ AI Backend — Clarification Engine

Identifies missing critical entities for school operations and generates
role-aligned, natural clarification questions rather than guessing or hallucinating.
"""

from typing import List, Optional
import logging

from app.ai.intent import IntentType
from app.ai.entities import ExtractedEntities
from app.ai.persona import get_persona
from app.ai.gemini import gemini_service

logger = logging.getLogger("app.ai.clarification")


def get_missing_fields(intent: IntentType, entities: ExtractedEntities, role: str) -> List[str]:
    """
    Evaluates what required parameters are missing for a given intent and role.
    """
    missing: List[str] = []
    
    if intent == IntentType.VIEW_CHILD_ATTENDANCE:
        # A parent needs to specify which child if not specified
        if not entities.student_name and not entities.student_id:
            missing.append("student_name")
            
    elif intent == IntentType.MARK_ATTENDANCE:
        # Teacher marking attendance needs: student, status, and date
        if not entities.student_name and not entities.student_id:
            missing.append("student_name")
        if not entities.status:
            missing.append("status")
        if not entities.date:
            missing.append("date")
            
    return missing


def build_clarification_prompt(missing_fields: List[str], role: str, original_message: str) -> str:
    """
    Generates a natural, human-like clarification question using Gemini tailored to persona.
    """
    persona = get_persona(role)
    missing_desc = ", ".join(missing_fields)
    
    prompt = (
        f"You are speaking as the {persona.title} ({persona.role.upper()}). "
        f"Tone: {persona.tone}. Style: {persona.communication_style}.\n"
        f"The user said: \"{original_message}\"\n"
        f"To fulfill this action, we are missing the following required information: {missing_desc}.\n"
        f"Ask a short, polite, human-like clarification question to request this missing information."
    )
    
    try:
        response = gemini_service.generate_response(prompt=prompt)
        return response
    except Exception as e:
        logger.error(f"Error generating clarification from Gemini: {e}")
        # Fallback template
        if "student_name" in missing_fields and len(missing_fields) == 1:
            return "Sure. Whose attendance would you like me to check?"
        if "date" in missing_fields and len(missing_fields) == 1:
            return "Which date should I record this for?"
        if "status" in missing_fields and len(missing_fields) == 1:
            return "Should I mark them present or absent?"
        return f"Could you please specify the {missing_desc}?"


def check_clarification_needed(
    intent: IntentType,
    entities: ExtractedEntities,
    role: str,
    original_message: str
) -> Optional[str]:
    """
    Returns a clarification question if critical information is missing, or None if ready to proceed.
    """
    missing_fields = get_missing_fields(intent, entities, role)
    if not missing_fields:
        return None
        
    return build_clarification_prompt(missing_fields, role, original_message)
