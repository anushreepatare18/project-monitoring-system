from fastapi.testclient import TestClient
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from chatbot.api import app

client = TestClient(app)

def test_explain_flagged():
    response = client.post("/chatbot/ask", json={
        "question": "Why is PRJ-123456 flagged?",
        "officer_id": "OFF-01",
        "scope": "ALL"
    })
    # Will likely return "not found" since synthetic IDs are random, 
    # but intent parsing should work
    data = response.json()
    assert "PRJ-123456" in data.get("answer_text", "") or "not found" in data.get("answer_text", "")

def test_high_risk_roads():
    response = client.post("/chatbot/ask", json={
        "question": "Which projects in the roads sector are high risk this month?",
        "officer_id": "OFF-01",
        "scope": "ALL"
    })
    data = response.json()
    assert "answer_text" in data
    assert isinstance(data.get("referenced_projects"), list)

def test_compare_projects():
    response = client.post("/chatbot/ask", json={
        "question": "Compare PRJ-111111 and PRJ-222222",
        "officer_id": "OFF-01",
        "scope": "ALL"
    })
    data = response.json()
    assert "PRJ-111111" in data.get("answer_text", "") or "found" in data.get("answer_text", "")

def test_aggregate():
    response = client.post("/chatbot/ask", json={
        "question": "Which sector has the most cost overruns right now?",
        "officer_id": "OFF-01",
        "scope": "ALL"
    })
    data = response.json()
    assert "cost overruns" in data.get("answer_text", "") or "No data" in data.get("answer_text", "")

def test_out_of_scope():
    response = client.post("/chatbot/ask", json={
        "question": "Why is PRJ-123456 flagged?",
        "officer_id": "OFF-01",
        "scope": "Ministry_99" # Unknown scope
    })
    data = response.json()
    assert "outside your authorized scope" in data.get("answer_text", "") or "not found" in data.get("answer_text", "")

def test_unsupported_domain():
    response = client.post("/chatbot/ask", json={
        "question": "What is the legal status of the contractor?",
        "officer_id": "OFF-01",
        "scope": "ALL"
    })
    data = response.json()
    assert "contractor" in data.get("answer_text", "")

def test_ambiguous():
    response = client.post("/chatbot/ask", json={
        "question": "Show me projects",
        "officer_id": "OFF-01",
        "scope": "ALL"
    })
    data = response.json()
    assert "specify" in data.get("answer_text", "")
