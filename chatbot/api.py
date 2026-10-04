from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import logging
from datetime import datetime
from chatbot.intent_parser import parse_intent
from chatbot.retriever import retrieve_grounded_data
from chatbot.answer_composer import compose_answer

app = FastAPI()

# Audit log mock
audit_log = []

class ChatRequest(BaseModel):
    question: str
    officer_id: str
    scope: str = "ALL"

@app.post("/chatbot/ask")
def ask_chatbot(req: ChatRequest):
    # 1. Intent Parsing
    parsed_query = parse_intent(req.question)
    
    if "clarifying_question" in parsed_query:
        return {
            "answer_text": parsed_query["clarifying_question"],
            "referenced_projects": []
        }
        
    # 2. Grounded Retrieval
    retrieved_data = retrieve_grounded_data(parsed_query, scope=req.scope)
    
    # 3. Answer Composition
    final_answer = compose_answer(retrieved_data, req.question)
    
    # 4. Audit Logging
    audit_entry = {
        "timestamp": datetime.now().isoformat(),
        "officer_id": req.officer_id,
        "scope": req.scope,
        "question": req.question,
        "parsed_query": parsed_query,
        "retrieved_data": retrieved_data,
        "final_answer": final_answer
    }
    audit_log.append(audit_entry)
    logging.info(f"AUDIT LOG: {audit_entry}")
    
    return final_answer

# To run: uvicorn chatbot.api:app --reload
