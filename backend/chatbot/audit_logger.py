"""
chatbot/audit_logger.py
=======================
Logs every chatbot interaction — question, parsed query, retrieved data,
and final answer — to the PRAGYA audit log table and to a chatbot-specific
JSONL file for full reproducibility.
"""

import json
import os
from datetime import datetime


CHATBOT_AUDIT_LOG = os.path.join(
    os.path.dirname(__file__), "..", "chatbot_audit.jsonl"
)


def log_interaction(
    officer_id: str,
    role: str,
    question: str,
    structured_query: dict,
    retrieval_result: dict,
    answer: dict,
) -> None:
    """
    Write a complete audit record. Each record is one JSON line so the file
    can be grepped / streamed without loading the whole thing.
    """
    record = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "officer_id": officer_id,
        "role": role,
        "question": question,
        "parsed_query": structured_query,
        "db_query_log": retrieval_result.get("query_log", ""),
        "rows_retrieved": retrieval_result.get("total_matched", 0),
        "referenced_projects": answer.get("referenced_projects", []),
        "grounding_method": answer.get("grounding_method", ""),
        "as_of_date": answer.get("as_of_date", ""),
        "answer_text": answer.get("answer_text", ""),
    }

    # Append to JSONL file
    try:
        with open(CHATBOT_AUDIT_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")
    except Exception as e:
        print(f"[audit_logger] Failed to write JSONL audit: {e}")

    # Also write to the SQLAlchemy AuditLog table when available
    try:
        from backend.app_db import SessionLocal, AuditLog
        db = SessionLocal()
        try:
            log_entry = AuditLog(
                action="Chatbot Query",
                user_role=role,
                details=(
                    f"Officer={officer_id} | Q={question[:100]} | "
                    f"Intent={structured_query.get('intent')} | "
                    f"Projects={record['referenced_projects']} | "
                    f"Method={record['grounding_method']}"
                ),
            )
            db.add(log_entry)
            db.commit()
        finally:
            db.close()
    except Exception as e:
        print(f"[audit_logger] Failed to write DB audit: {e}")
