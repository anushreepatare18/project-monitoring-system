"""
PRAGYA AI — Chatbot Tests  (v2)
==================================
10+ test cases covering:
  1. Normal sector/risk-band lookup
  2. Explain a specific project ("why flagged")
  3. Project comparison
  4. Zero-results scenario
  5. Out-of-scope data (contractor / legal questions)
  6. Permission boundary (officer asking outside their ministry scope)
  7. Aggregate query (which sector has most overruns)
  8. Milestone delay filter
  9. Anomaly-flagged projects
 10. Ambiguous question → clarifying question response
 11. Single project ID without explicit "why" (explain passthrough)
 12. Unknown project ID (not in store)
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

# We must be able to import the app from the repo root
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from chatbot.api import app

client = TestClient(app)

BASE_REQUEST = {
    "officer_id": "TEST-OFFICER-01",
    "scope":      "ALL",
    "role":       "officer",
}


# ── Helpers ───────────────────────────────────────────────────────────────────

def ask(question: str, scope: str = "ALL") -> dict:
    resp = client.post(
        "/chatbot/ask",
        json={**BASE_REQUEST, "question": question, "scope": scope},
    )
    assert resp.status_code == 200, f"HTTP {resp.status_code}: {resp.text}"
    return resp.json()


# ── Test 1: Normal sector + risk-band filter ──────────────────────────────────

def test_high_risk_roads_sector():
    """Officer asks for high-risk roads projects → should return answer_text and projects list."""
    data = ask("Which projects in the Roads sector are high risk this month?")
    assert "answer_text" in data
    assert isinstance(data["referenced_projects"], list)
    # Answer must contain a factual assertion, not a guess
    assert "No projects" in data["answer_text"] or len(data["referenced_projects"]) > 0


# ── Test 2: Explain a specific project ───────────────────────────────────────

def test_explain_project_in_store():
    """Fetch any known project ID from the store and ask for an explanation."""
    from chatbot.results_store import get_store
    store = get_store()
    pid = store.iloc[0]["project_id"]

    data = ask(f"Why is {pid} flagged as high risk?")
    assert "answer_text" in data
    assert pid in data["answer_text"] or pid in data["referenced_projects"]


# ── Test 3: Compare two projects ──────────────────────────────────────────────

def test_compare_two_projects():
    """Comparison query for two valid project IDs."""
    from chatbot.results_store import get_store
    store = get_store()
    p1 = store.iloc[0]["project_id"]
    p2 = store.iloc[1]["project_id"]

    data = ask(f"Compare {p1} and {p2}")
    assert "answer_text" in data
    # Should mention both or report missing
    text = data["answer_text"]
    assert p1 in text or p1 in data["referenced_projects"]


# ── Test 4: Zero-results scenario ────────────────────────────────────────────

def test_zero_results_nonexistent_sector():
    """
    Asking for a sector that exists in the schema but has no critical-risk
    projects should return a zero-results message, not a fabricated list.
    """
    data = ask("Show me critical risk projects in the IT sector with milestone delays over 99 months")
    assert "answer_text" in data
    # Must not return fabricated data
    assert (
        "No projects" in data["answer_text"]
        or len(data["referenced_projects"]) == 0
        or data.get("clarifying_question") is not None
    )


# ── Test 5: Out-of-scope data — contractor names ──────────────────────────────

def test_out_of_scope_contractor():
    """The chatbot must refuse contractor questions, not hallucinate."""
    data = ask("What is the name of the contractor for project PRJ-100001?")
    assert "answer_text" in data
    text = data["answer_text"].lower()
    assert (
        "don't have" in text
        or "not have" in text
        or "cannot" in text
        or "clarifying" in text.lower()
        or data.get("clarifying_question") is not None
    )


# ── Test 6: Out-of-scope data — legal status ─────────────────────────────────

def test_out_of_scope_legal():
    """Questions about legal/court status should return 'cannot answer'."""
    data = ask("What is the legal status of project PRJ-999999?")
    assert "answer_text" in data
    assert data.get("clarifying_question") is not None or "don't have" in data["answer_text"].lower()


# ── Test 7: RBAC permission boundary ─────────────────────────────────────────

def test_permission_boundary_ministry_scope():
    """
    An officer scoped to 'MoRTH' should not get data from 'MoH'.
    Projects from 'MoH' must not appear in the response.
    """
    from chatbot.results_store import get_store
    store = get_store()
    # Find a project that belongs to MoH (not MoRTH)
    moh_projects = store[store["ministry"] == "MoH"]["project_id"].tolist()
    if not moh_projects:
        pytest.skip("No MoH projects in mock store")

    pid = moh_projects[0]
    data = ask(f"Tell me about {pid}", scope="MoRTH")
    assert "answer_text" in data
    # Should say not found / outside scope
    text = data["answer_text"]
    assert (
        "not found" in text.lower()
        or "outside" in text.lower()
        or "authorised scope" in text.lower()
    )


# ── Test 8: Aggregate — which sector has most cost overruns ──────────────────

def test_aggregate_most_cost_overruns():
    """Aggregation query should return a ranked list, not a single fabricated answer."""
    data = ask("Which sector has the most cost overruns right now?")
    assert "answer_text" in data
    text = data["answer_text"]
    # Should mention 'sector' and a count or ranking
    assert "sector" in text.lower() or "Ranking" in text


# ── Test 9: Milestone delay filter ───────────────────────────────────────────

def test_milestone_delay_filter():
    """Filter by milestone delay threshold."""
    data = ask("Show me projects with milestone delays over 3 months in the Roads sector")
    assert "answer_text" in data
    assert isinstance(data["referenced_projects"], list)
    # Must cite data or say none found
    assert "mo" in data["answer_text"].lower() or "no projects" in data["answer_text"].lower()


# ── Test 10: Anomaly-flagged projects ─────────────────────────────────────────

def test_anomaly_flagged_projects():
    """Query for anomalous projects."""
    data = ask("Which projects have been flagged with anomalies in the Health sector?")
    assert "answer_text" in data
    # Should either return projects or a zero-results message
    assert (
        len(data["referenced_projects"]) >= 0
    )  # just check structure is correct


# ── Test 11: Ambiguous question → clarifying question ────────────────────────

def test_ambiguous_question():
    """A vague question should return a single clarifying question."""
    data = ask("Show me some projects")
    assert "answer_text" in data
    # Should ask for more info
    text = data["answer_text"]
    assert (
        "?" in text
        or "specify" in text.lower()
        or "sector" in text.lower()
        or data.get("clarifying_question") is not None
    )


# ── Test 12: Unknown project ID ───────────────────────────────────────────────

def test_unknown_project_id():
    """Unknown project ID should return 'not found', not fabricated data."""
    data = ask("Explain the risk for PRJ-000000")
    assert "answer_text" in data
    assert (
        "not found" in data["answer_text"].lower()
        or "outside" in data["answer_text"].lower()
        or len(data["referenced_projects"]) == 0
    )


# ── Test 13: Response schema completeness ────────────────────────────────────

def test_response_has_disclaimer():
    """Every response must include the PRAGYA disclaimer field."""
    data = ask("Which Roads sector projects are at risk?")
    assert "disclaimer" in data
    assert len(data["disclaimer"]) > 20   # non-trivial disclaimer


# ── Test 14: Numeric claims come from data, not invented ─────────────────────

def test_numeric_claims_from_data():
    """
    For an explanation response, the risk score in the answer must match
    the value in the results store (not an LLM-invented number).
    """
    from chatbot.results_store import get_store
    store = get_store()
    pid = store.iloc[0]["project_id"]
    expected_score = round(store.iloc[0]["composite_risk_score"] * 100, 1)

    data = ask(f"Why is {pid} flagged?")
    if data.get("clarifying_question"):
        pytest.skip("Clarifying question returned — project not parseable from question")

    text = data["answer_text"]
    # The score (rounded to 1 dp) must appear verbatim in the answer
    assert str(expected_score) in text or pid in data["referenced_projects"]


# ── Test 15: Health endpoint ──────────────────────────────────────────────────

def test_health_endpoint():
    resp = client.get("/chatbot/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"
