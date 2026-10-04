"""
PRAGYA AI — Chatbot API  (v2)
==============================
FastAPI endpoint: POST /chatbot/ask

Request:
    question   : str        — officer's natural-language question
    officer_id : str        — for audit log
    scope      : str        — RBAC scope: ministry name or "ALL"

Response:
    answer_text          : str
    referenced_projects  : list[str]
    clarifying_question  : str | None
    as_of_date           : str
    disclaimer           : str

Every interaction is written to the append-only audit JSONL log.
"""
from __future__ import annotations

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from chatbot.answer_composer import compose_answer
from chatbot.intent_parser import parse_intent
from chatbot.retriever import retrieve_grounded_data

# ── Logging setup ─────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("pragya.chatbot")

# ── Audit log file ────────────────────────────────────────────────────────────
AUDIT_LOG_PATH = Path(os.environ.get("PRAGYA_AUDIT_LOG", "backend/chatbot_audit.jsonl"))
AUDIT_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

DISCLAIMER = (
    "Answers are generated from stored risk data and are for review support only — "
    "not a final finding. Verify with the dashboard before acting."
)


def _write_audit(entry: dict) -> None:
    """Append one audit record to the JSONL file (append-only, never edited)."""
    try:
        with open(AUDIT_LOG_PATH, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, ensure_ascii=False, default=str) + "\n")
    except Exception as exc:
        logger.error("[audit] Failed to write audit log: %s", exc)


# ── FastAPI app ────────────────────────────────────────────────────────────────
app = FastAPI(
    title="PRAGYA AI — Chatbot API",
    description=(
        "Retrieval-grounded risk-query assistant for government project-monitoring officers. "
        "Answers are grounded in stored XAI outputs — never fabricated."
    ),
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)


# ── Request / Response models ─────────────────────────────────────────────────

class ChatRequest(BaseModel):
    question:   str = Field(..., description="Officer's natural-language question")
    officer_id: str = Field(..., description="Unique officer identifier for audit")
    scope:      str = Field("ALL", description="RBAC scope — ministry name or 'ALL'")
    role:       str = Field("officer", description="Officer role (officer / admin)")


class ChatResponse(BaseModel):
    answer_text:          str
    referenced_projects:  list[str]
    clarifying_question:  Optional[str]
    as_of_date:           str
    disclaimer:           str
    query_run:            str     # auditable record of the exact query executed


# ── Main endpoint ─────────────────────────────────────────────────────────────

@app.post("/chatbot/ask", response_model=ChatResponse)
def ask_chatbot(req: ChatRequest) -> ChatResponse:
    """
    Process an officer's question through the 4-step grounded pipeline:
      1. Intent parsing  (deterministic rules, no LLM)
      2. Grounded retrieval  (query results store, log exact query)
      3. Answer composition  (format retrieved data, explanation passthrough)
      4. Audit logging  (question + query + retrieved_data + answer → JSONL)
    """
    ts = datetime.utcnow().isoformat() + "Z"

    # ── Step 1: Intent Parsing ────────────────────────────────────────────────
    parsed_query = parse_intent(req.question)

    # Return clarifying question immediately if needed
    if parsed_query.get("intent") in ("AMBIGUOUS", "OUT_OF_SCOPE"):
        cq = parsed_query.get("clarifying_question", "Could you please rephrase?")
        audit = {
            "ts":           ts,
            "officer_id":   req.officer_id,
            "scope":        req.scope,
            "role":         req.role,
            "question":     req.question,
            "parsed_query": parsed_query,
            "retrieved":    None,
            "answer":       cq,
            "intent":       parsed_query.get("intent"),
        }
        _write_audit(audit)
        logger.info("[ask] %s | intent=%s | clarifying", req.officer_id, parsed_query.get("intent"))
        return ChatResponse(
            answer_text=cq,
            referenced_projects=[],
            clarifying_question=cq,
            as_of_date=str(datetime.utcnow().date()),
            disclaimer=DISCLAIMER,
            query_run="[clarifying question — no retrieval performed]",
        )

    # ── Step 2: Grounded Retrieval ────────────────────────────────────────────
    retrieved_data = retrieve_grounded_data(parsed_query, scope=req.scope)

    # ── Step 3: Answer Composition ────────────────────────────────────────────
    composed = compose_answer(retrieved_data, req.question)

    # ── Step 4: Audit Logging ─────────────────────────────────────────────────
    audit = {
        "ts":                ts,
        "officer_id":        req.officer_id,
        "scope":             req.scope,
        "role":              req.role,
        "question":          req.question,
        "parsed_query":      parsed_query,
        "query_run":         composed.get("query_run", ""),
        "retrieved_type":    retrieved_data.get("type"),
        "retrieved_count":   (
            len(retrieved_data.get("data", []))
            if isinstance(retrieved_data.get("data"), list)
            else 1
        ),
        "referenced_projects": composed.get("referenced_projects", []),
        "answer_preview":    composed["answer_text"][:200],
    }
    _write_audit(audit)

    logger.info(
        "[ask] officer=%s | intent=%s | refs=%s",
        req.officer_id,
        parsed_query.get("intent"),
        composed.get("referenced_projects"),
    )

    return ChatResponse(
        answer_text=composed["answer_text"],
        referenced_projects=composed.get("referenced_projects", []),
        clarifying_question=None,
        as_of_date=composed.get("as_of_date", str(datetime.utcnow().date())),
        disclaimer=DISCLAIMER,
        query_run=composed.get("query_run", ""),
    )


@app.get("/chatbot/health")
def health():
    return {"status": "ok", "service": "PRAGYA-Chatbot", "version": "2.0.0"}


# ── Run locally ───────────────────────────────────────────────────────────────
# uvicorn chatbot.api:app --reload --port 8000
