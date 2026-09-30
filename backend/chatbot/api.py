"""
chatbot/api.py
==============
FastAPI router for the PRAGYA chatbot endpoint.

POST /chatbot/ask
  Body: { question, officer_id, role, scope }
  Response: { answer_text, referenced_projects, clarifying_question?,
              as_of_date, grounding_method, query_log }

The router is mounted onto the main FastAPI app in backend/main.py via:
  from backend.chatbot.api import chatbot_router
  app.include_router(chatbot_router)
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List

from backend.chatbot.intent_parser import parse_intent
from backend.chatbot.retriever import fetch
from backend.chatbot.answer_composer import compose
from backend.chatbot.audit_logger import log_interaction

chatbot_router = APIRouter(prefix="/chatbot", tags=["chatbot"])


class ChatbotRequest(BaseModel):
    question: str
    officer_id: str = "anonymous"
    role: str = "officer"          # 'officer' | 'ministry' | 'agency' | 'public'
    scope: Optional[dict] = None   # e.g. {"ministry": "Ministry of Power"}


class ChatbotResponse(BaseModel):
    answer_text: str
    referenced_projects: List[str]
    clarifying_question: Optional[str] = None
    as_of_date: str
    grounding_method: str
    query_log: str


@chatbot_router.post("/ask", response_model=ChatbotResponse)
def ask(req: ChatbotRequest):
    """
    Grounded question-answering pipeline:
      1. Parse intent (LLM extracts fields only)
      2. Fetch from results store (deterministic, RBAC-scoped)
      3. Compose answer (LLM narrates retrieved data only, or direct SHAP)
      4. Audit log everything
    """
    if req.role == "public":
        return ChatbotResponse(
            answer_text=(
                "The AI assistant is not available for public users. "
                "Please use the public dashboard to browse project information."
            ),
            referenced_projects=[],
            as_of_date="",
            grounding_method="permission_denied",
            query_log="role=public: access denied",
        )

    # 1. Parse intent
    structured_query = parse_intent(req.question)

    # 2. Retrieve grounding data
    retrieval_result = fetch(
        structured_query,
        role=req.role,
        scope=req.scope or {},
    )

    # 3. Compose grounded answer
    answer = compose(req.question, structured_query, retrieval_result)

    # 4. Audit log
    try:
        log_interaction(
            officer_id=req.officer_id,
            role=req.role,
            question=req.question,
            structured_query=structured_query,
            retrieval_result=retrieval_result,
            answer=answer,
        )
    except Exception as e:
        print(f"[chatbot/api] Audit log error (non-fatal): {e}")

    return ChatbotResponse(
        answer_text=answer.get("answer_text", ""),
        referenced_projects=answer.get("referenced_projects", []),
        clarifying_question=structured_query.get("clarifying_question"),
        as_of_date=answer.get("as_of_date", ""),
        grounding_method=answer.get("grounding_method", ""),
        query_log=retrieval_result.get("query_log", ""),
    )
