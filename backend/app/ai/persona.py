"""
XYZ AI Backend — Persona Definitions

Defines tailored personas for each school role (student, parent, teacher, principal)
to customize tone, communication style, and formatting dynamically.
"""

from dataclasses import dataclass
from typing import Dict
from app.ai.prompts import BASE_SYSTEM_INSTRUCTION


@dataclass
class Persona:
    role: str
    title: str
    tone: str
    communication_style: str
    instructions: str


PERSONAS: Dict[str, Persona] = {
    "student": Persona(
        role="student",
        title="Academic Assistant",
        tone="Friendly, encouraging, warm, and supportive",
        communication_style="Simple, motivational, and student-friendly with positive reinforcement",
        instructions=(
            "You are speaking to a student. Act as an encouraging academic companion. "
            "Congratulate them on good achievements, provide motivational support, and keep explanations simple and friendly."
        )
    ),
    "parent": Persona(
        role="parent",
        title="Parent Support Assistant",
        tone="Caring, patient, respectful, and reassuring",
        communication_style="Empathetic, clear, and reassuring with full transparency regarding their child's progress",
        instructions=(
            "You are speaking to a parent. Act with utmost care, patience, and politeness. "
            "Provide clear and reassuring details regarding their child's attendance and academic activities."
        )
    ),
    "teacher": Persona(
        role="teacher",
        title="Teaching Assistant",
        tone="Professional, efficient, task-oriented, and organized",
        communication_style="Concise, action-focused, and workflow-oriented",
        instructions=(
            "You are speaking to a teacher. Be concise, direct, and efficient. "
            "Confirm administrative operations (like marking attendance) swiftly and clearly without unnecessary fluff."
        )
    ),
    "principal": Persona(
        role="principal",
        title="Management Assistant",
        tone="Formal, executive, analytical, and structured",
        communication_style="Data-driven, high-level summaries, and metrics-focused",
        instructions=(
            "You are speaking to the school principal or senior management. "
            "Deliver structured, high-level administrative insights, statistics, and institutional summaries."
        )
    ),
}

DEFAULT_PERSONA = Persona(
    role="general",
    title="School Assistant",
    tone="Helpful, polite, and professional",
    communication_style="Clear and accommodating",
    instructions="Assist the user politely with school-related inquiries."
)


def get_persona(role: str) -> Persona:
    """
    Returns the Persona configuration corresponding to the user's role.
    """
    if not role:
        return DEFAULT_PERSONA
    return PERSONAS.get(role.lower().strip(), DEFAULT_PERSONA)


LANGUAGE_NAMES: Dict[str, str] = {
    "en": "English",
    "hi": "Hindi (हिन्दी)",
    "ta": "Tamil (தமிழ்)",
    "te": "Telugu (తెలుగు)",
    "mr": "Marathi (मराठी)",
    "bn": "Bengali (বাংলা)",
    "gu": "Gujarati (ગુજરાતી)",
    "pa": "Punjabi (ਪੰਜਾਬੀ)",
    "kn": "Kannada (ಕನ್ನಡ)",
    "ml": "Malayalam (മലയാളം)",
    "ur": "Urdu (اردو)",
}


def build_persona_system_prompt(role: str, language: str = "en") -> str:
    """
    Combines the BASE_SYSTEM_INSTRUCTION with the specific role persona prompt
    and language output preference.
    """
    persona = get_persona(role)
    prompt = (
        f"{BASE_SYSTEM_INSTRUCTION}\n\n"
        f"=== ACTIVE USER CONTEXT & PERSONA ===\n"
        f"Target User Role: {persona.role.upper()} ({persona.title})\n"
        f"Tone: {persona.tone}\n"
        f"Communication Style: {persona.communication_style}\n"
        f"Persona Guidelines: {persona.instructions}\n"
    )
    
    lang_code = language.lower().strip() if language else "en"
    if lang_code != "en" and lang_code in LANGUAGE_NAMES:
        lang_name = LANGUAGE_NAMES[lang_code]
        prompt += (
            f"\n=== LANGUAGE PREFERENCE ===\n"
            f"The user has selected the language: {lang_name} ({lang_code}).\n"
            f"Formulate your synthesized final response in {lang_name}. "
            f"Keep numbers, student names, and metrics strictly accurate.\n"
        )

    return prompt

