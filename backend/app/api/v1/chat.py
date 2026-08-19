"""
XYZ AI Backend — Chat API Router (Phase 4 End-to-End Pipeline)

Implements the full end-to-end conversation flow:
    User Message
        │
        ▼
    1. Identify User Context (Mock / Auth)
        │
        ▼
    2. Detect Intent (Phase 3 AI)
        │
        ▼
    3. Extract Entities (Phase 3 AI)
        │
        ▼
    4. Clarification Check (Missing required params)
        │
        ▼
    5. Python Permission Layer (RBAC check)
        │
        ▼
    6. Gemini Tool Selection & Interception
        │
        ▼
    7. Tool Execution via ERP API Client (httpx)
        │
        ▼
    8. Phase 2 ERP Backend -> PostgreSQL
        │
        ▼
    9. Receive Structured Result
        │
        ▼
    10. Gemini Synthesizes Natural Language Response
        │
        ▼
    Return ChatResponse
"""

from fastapi import APIRouter, HTTPException, File, UploadFile, Form, Header
import logging
from typing import Optional

from app.schemas.chat import ChatRequest, ChatResponse
from app.ai.gemini import gemini_service
from app.ai.intent import detect_intent, IntentType
from app.ai.entities import extract_entities
from app.ai.clarification import check_clarification_needed
from app.ai.persona import build_persona_system_prompt
from app.security.context import get_current_user_context, build_user_context_from_erp
from app.security.permissions import is_allowed, get_permission_denied_message, VALID_ROLES
from app.utils.error_handler import format_user_friendly_error
from app.services.stt_service import transcribe_audio
from app.services.tts_service import synthesize_speech

logger = logging.getLogger("app.api.v1.chat")

router = APIRouter()


async def run_chat_pipeline(message: str, role: str, user_id: Optional[int] = None, language: Optional[str] = "en") -> str:
    """
    Core Phase 4 conversational execution pipeline.
    Reused by both JSON text chat and Voice chat endpoints.
    """
    norm_role = role.lower().strip()
    if norm_role not in VALID_ROLES:
        raise ValueError(f"Invalid role. Must be one of {sorted(VALID_ROLES)}")

    if not message.strip():
        return "Please ask a question or speak into your microphone."

    # 1-3. Resolve Dynamic User Context, Detect Intent, and Extract Entities in parallel
    import asyncio
    user_ctx_task = build_user_context_from_erp(role=norm_role, user_id=user_id or 101)
    intent_task = asyncio.to_thread(detect_intent, message, norm_role)
    entities_task = asyncio.to_thread(extract_entities, message, norm_role)

    user_ctx, intent_result, entities = await asyncio.gather(
        user_ctx_task, intent_task, entities_task
    )
    intent = intent_result.intent

    # 4. Check for Missing Critical Fields (Clarification)
    clarification_msg = check_clarification_needed(
        intent=intent,
        entities=entities,
        role=norm_role,
        original_message=message,
    )
    if clarification_msg:
        logger.info(f"Clarification triggered for query '{message}': {clarification_msg}")
        return clarification_msg

    # 5. Application Permission Gate (Intent Level RBAC check)
    if not is_allowed(norm_role, intent):
        denial_msg = get_permission_denied_message(norm_role, intent)
        logger.warning(f"Permission denied for role '{norm_role}' on intent '{intent}': {denial_msg}")
        return denial_msg

    # 5b. Handle Human Escalation — create a ticket and short-circuit
    if intent == IntentType.HUMAN_ESCALATION:
        try:
            from app.db.session import SessionLocal
            from app.schemas.escalation import EscalationCreate
            from app.services.escalation_service import create_escalation as _create_esc

            db = SessionLocal()
            try:
                ticket = _create_esc(db, EscalationCreate(
                    user_id=user_id or 0,
                    role=norm_role,
                    reason=message,
                ))
                return (
                    f"I've created a support ticket (#{ticket.id}) and a staff member will "
                    f"reach out to you shortly. Your request has been noted."
                )
            finally:
                db.close()
        except Exception as esc_err:
            logger.error(f"Failed to create escalation ticket: {esc_err}")
            return (
                "I understand you'd like to speak with someone. "
                "Please contact the school front desk directly. I apologize for the inconvenience."
            )

    # 6-10. Gemini Tool Calling Loop + Persona & Multilingual Instructions
    persona_prompt = build_persona_system_prompt(norm_role, language=language or "en")
    
    response_text = await gemini_service.generate_response_with_tools(
        prompt=message,
        user_context=user_ctx.to_dict(),
        system_instruction=persona_prompt,
    )
    
    return response_text


@router.post("", response_model=ChatResponse, summary="Send a message to the XYZ AI assistant")
async def chat(
    request: ChatRequest,
    authorization: Optional[str] = Header(None),
) -> ChatResponse:
    """
    Text assistant chat endpoint.
    If an Authorization Bearer token is provided, verified token identity takes precedence.
    """
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message content cannot be empty.")

    # Extract verified role and user_id from JWT if present
    effective_role = request.role
    effective_user_id = request.user_id

    if authorization and authorization.startswith("Bearer "):
        from app.core.security import decode_access_token
        token = authorization.split(" ")[1]
        payload = decode_access_token(token)
        if payload and "sub" in payload:
            effective_user_id = int(payload["sub"])
            effective_role = payload.get("role", effective_role)

    try:
        response_text = await run_chat_pipeline(
            message=request.message,
            role=effective_role,
            user_id=effective_user_id,
            language=request.language,
        )
        return ChatResponse(response=response_text)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Chat API execution error: {str(e)}")
        safe_message = format_user_friendly_error(status_code=500, detail=str(e))
        return ChatResponse(response=safe_message)


@router.post("/voice", summary="Send an audio recording to the XYZ AI assistant")
async def chat_voice(
    audio: UploadFile = File(...),
    role: str = Form(...),
    user_id: Optional[int] = Form(None),
    language: Optional[str] = Form("en"),
    authorization: Optional[str] = Header(None),
) -> dict:
    """
    Voice assistant chat endpoint.
    Accepts recorded voice file, transcribes it via STT service,
    routes the exact transcription to the existing Phase 4 chat execution pipeline,
    and returns both the transcription text and AI response.
    """
    effective_role = role
    effective_user_id = user_id

    if authorization and authorization.startswith("Bearer "):
        from app.core.security import decode_access_token
        token = authorization.split(" ")[1]
        payload = decode_access_token(token)
        if payload and "sub" in payload:
            effective_user_id = int(payload["sub"])
            effective_role = payload.get("role", effective_role)

    norm_role = effective_role.lower().strip()
    if norm_role not in VALID_ROLES:
        raise HTTPException(status_code=400, detail=f"Invalid role. Must be one of {sorted(VALID_ROLES)}")

    try:
        # Read raw audio bytes
        audio_bytes = await audio.read()
        
        # 1. Speech-to-Text (STT): Transcribe voice to plain text
        transcription = await transcribe_audio(audio_bytes, mime_type=audio.content_type)
        
        if not transcription or not transcription.strip():
            return {
                "transcription": "",
                "response": "I couldn't hear or understand the audio. Please try speaking clearly.",
                "audio_base64": None
            }
            
        # 2. Connect directly to existing XYZ AI pipeline (single convergence point)
        response_text = await run_chat_pipeline(
            message=transcription,
            role=norm_role,
            user_id=effective_user_id,
            language=language,
        )
        
        # 3. Text-to-Speech (TTS): Synthesize voice response to Base64 MP3
        audio_b64 = await synthesize_speech(response_text, language=language or "en")
        
        return {
            "transcription": transcription,
            "response": response_text,
            "audio_base64": audio_b64
        }

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        logger.error(f"Voice Chat STT runtime error: {str(e)}")
        return {
            "transcription": "",
            "response": str(e),
            "audio_base64": None
        }
    except Exception as e:
        logger.error(f"Voice Chat API error: {str(e)}")
        safe_message = format_user_friendly_error(status_code=500, detail=str(e))
        return {
            "transcription": "",
            "response": safe_message,
            "audio_base64": None
        }

