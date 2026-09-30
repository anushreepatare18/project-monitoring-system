"""
chatbot/intent_parser.py
========================
Parses a natural-language officer question into a *structured query* dict.
The LLM is used ONLY to extract field values — it never supplies facts.

Output schema (all fields optional / None if not mentioned):
{
  "intent": "list_projects" | "explain_project" | "compare_projects"
           | "sector_summary" | "unknown" | "cannot_answer",
  "sector": str | None,
  "ministry": str | None,
  "agency": str | None,
  "risk_band": "Low"|"Medium"|"High"|"Critical" | None,
  "min_risk_score": float | None,
  "max_risk_score": float | None,
  "milestone_delay_months_min": float | None,
  "cost_overrun_pct_min": float | None,
  "project_ids": list[str],        # empty list if none
  "sort_by": str | None,           # e.g. "risk_score", "delay_months"
  "limit": int,                    # default 10
  "clarifying_question": str | None,   # set if question is ambiguous
  "out_of_scope_reason": str | None,   # set if intent == "cannot_answer"
}
"""

import json
import re
import os
from typing import Optional

# ── known vocabulary the parser validates against ──────────────────────────
KNOWN_SECTORS = {
    "roads", "highways", "railways", "power", "energy",
    "water", "urban", "housing", "ports", "airports", "telecom",
    "irrigation", "defence", "health", "education",
}

KNOWN_RISK_BANDS = {"low", "medium", "high", "critical"}

KNOWN_SORT_FIELDS = {
    "risk_score", "delay_months", "cost_overrun_pct",
    "physical_progress_pct", "expenditure_cr",
}

# Fields/topics that are NOT in the data store — always "cannot_answer"
OUT_OF_SCOPE_TOPICS = [
    "contractor name", "contractor details", "legal status", "court case",
    "rti", "tender details", "payment terms", "blacklist", "employee",
    "salary", "bank account", "contact number", "email", "phone",
    "weather", "stock", "share price",
]


def _call_gemini(prompt: str) -> str:
    """Call Gemini for intent extraction only. Returns raw text."""
    try:
        import google.generativeai as genai
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return ""
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"[intent_parser] Gemini call failed: {e}")
        return ""


def _rules_precheck(question: str) -> Optional[dict]:
    """
    Fast rules-based pre-check before calling the LLM.
    Returns a partial or complete structured query if a rule fires,
    otherwise None (fall through to LLM).
    """
    q = question.lower().strip()

    # Out-of-scope check
    for topic in OUT_OF_SCOPE_TOPICS:
        if topic in q:
            return {
                "intent": "cannot_answer",
                "out_of_scope_reason": (
                    f"I don't have information about '{topic}'. "
                    "This system only covers risk scores, SHAP explanations, "
                    "anomaly flags, milestone delays, and cost overruns."
                ),
            }

    # Single project "why flagged / explain" pattern
    pid_match = re.search(
        r"\b(p-[a-z]+-\d+|prj-\d+|[a-z]{2,}-\d{3,})\b", q, re.IGNORECASE
    )
    if pid_match and any(w in q for w in ("why", "explain", "reason", "flag", "risk factor")):
        return {
            "intent": "explain_project",
            "project_ids": [pid_match.group(0).upper()],
        }

    return None


def _llm_parse(question: str) -> dict:
    """Ask the LLM to extract structured query fields. Never ask it for facts."""
    system_prompt = """You are a query-structure extractor for the PRAGYA AI government project monitoring system.
Your ONLY job is to extract query parameters from the officer's question into JSON.
You must NEVER answer the question yourself, invent project names, or supply data.

Known sectors (use ONLY these, or null): roads, highways, railways, power, energy, water, urban, housing, ports, airports, telecom, irrigation, defence, health, education
Known risk_band values: Low, Medium, High, Critical
Known sort_by fields: risk_score, delay_months, cost_overrun_pct, physical_progress_pct, expenditure_cr
Known intents: list_projects, explain_project, compare_projects, sector_summary, unknown, cannot_answer

Rules:
- If the officer mentions a sector not in the known list, set clarifying_question to ask which sector they mean.
- If the question asks about contractor names, legal status, court cases, contact details, employee info, or anything not in the risk/financial/milestone data, set intent=cannot_answer.
- If the question is ambiguous (could mean multiple things), set clarifying_question.
- project_ids must be an array (empty if none mentioned).
- limit defaults to 10.
- All other fields default to null.

Return ONLY a valid JSON object - no markdown, no explanation."""

    user_prompt = f"""Extract query parameters from this question:
"{question}"

Return JSON with these fields (all optional, use null if not present):
{{
  "intent": "<one of the known intents>",
  "sector": "<sector or null>",
  "ministry": "<ministry name or null>",
  "agency": "<agency name or null>",
  "risk_band": "<Low|Medium|High|Critical or null>",
  "min_risk_score": null,
  "max_risk_score": null,
  "milestone_delay_months_min": null,
  "cost_overrun_pct_min": null,
  "project_ids": [],
  "sort_by": "<field or null>",
  "limit": 10,
  "clarifying_question": "<one clarifying question or null>",
  "out_of_scope_reason": "<reason or null>"
}}"""

    raw = _call_gemini(system_prompt + "\n\n" + user_prompt)

    # Strip markdown code fences if present
    raw = re.sub(r"```(?:json)?", "", raw).strip().rstrip("`").strip()

    try:
        parsed = json.loads(raw)
        return parsed
    except json.JSONDecodeError:
        # Fallback: try to find any JSON object in the response
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except Exception:
                pass
        return {"intent": "unknown"}


def _apply_defaults(parsed: dict) -> dict:
    """Ensure all expected keys exist with sensible defaults."""
    defaults = {
        "intent": "unknown",
        "sector": None,
        "ministry": None,
        "agency": None,
        "risk_band": None,
        "min_risk_score": None,
        "max_risk_score": None,
        "milestone_delay_months_min": None,
        "cost_overrun_pct_min": None,
        "project_ids": [],
        "sort_by": None,
        "limit": 10,
        "clarifying_question": None,
        "out_of_scope_reason": None,
    }
    for k, v in defaults.items():
        if k not in parsed or parsed[k] is None:
            parsed.setdefault(k, v)
    # Ensure project_ids is always a list
    if not isinstance(parsed.get("project_ids"), list):
        parsed["project_ids"] = []
    # Clamp limit
    try:
        parsed["limit"] = max(1, min(int(parsed.get("limit") or 10), 50))
    except (TypeError, ValueError):
        parsed["limit"] = 10
    # Validate sector
    if parsed.get("sector") and parsed["sector"].lower() not in KNOWN_SECTORS:
        parsed["clarifying_question"] = (
            f"I don't recognise '{parsed['sector']}' as a known sector. "
            f"Did you mean one of: {', '.join(sorted(KNOWN_SECTORS))}?"
        )
        parsed["sector"] = None
    # Validate risk_band
    if parsed.get("risk_band") and parsed["risk_band"].lower() not in KNOWN_RISK_BANDS:
        parsed["risk_band"] = None
    return parsed


def parse_intent(question: str) -> dict:
    """
    Main entry point.
    Returns a structured query dict suitable for retriever.fetch().
    """
    # 1. Fast rules precheck
    rules_result = _rules_precheck(question)
    if rules_result:
        return _apply_defaults(rules_result)

    # 2. LLM extraction
    parsed = _llm_parse(question)

    # 3. Apply defaults and validation
    return _apply_defaults(parsed)


# Self-test
if __name__ == "__main__":
    test_questions = [
        "Which projects in the roads sector are high risk this month?",
        "Why is project P-ROADS-0457 flagged?",
        "Show me projects with milestone delays over 3 months in the railways sector",
        "Compare project P-ROADS-0457 and P-POWER-0123",
        "Which sector has the most cost overruns right now?",
        "What is the contractor name for project PRJ-001?",
        "Who is the legal representative for the Delhi metro case?",
        "Show me all critical risk projects under Ministry of Power",
    ]
    for q in test_questions:
        result = parse_intent(q)
        print(f"\nQ: {q}")
        print(f"-> {json.dumps(result, indent=2)}")
