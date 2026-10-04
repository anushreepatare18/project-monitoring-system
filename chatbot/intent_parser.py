"""
PRAGYA AI — Intent Parser  (v2)
=================================
Maps a natural-language officer question to a strictly-typed structured
query dict that the retriever can execute deterministically.

Architecture: Rules-first (for speed and auditability), with an LLM call
as a fallback for complex / ambiguous phrasings. The LLM is constrained
to fill only known fields from a fixed schema — it cannot invent new
entity types.

Known query schema:
    intent          : EXPLAIN_PROJECT | COMPARE_PROJECTS | FILTER_PROJECTS
                      | AGGREGATE | AMBIGUOUS | OUT_OF_SCOPE
    project_id      : str
    project_ids     : list[str]
    sector          : str  (must be in VALID_SECTORS or raise AMBIGUOUS)
    ministry        : str
    agency          : str
    risk_band       : Low | Medium | High | Critical
    min_risk_score  : float  [0–1]
    min_milestone_delay_months : float
    metric          : cost_overrun | delay | anomaly | avg_risk
    sort_by         : composite_risk_score | milestone_delay_months | cost_growth_pct
    limit           : int
    date_range      : {start: str, end: str}
    clarifying_question : str  (only present for AMBIGUOUS / OUT_OF_SCOPE)
"""
from __future__ import annotations

import re
from typing import Optional

from chatbot.results_store import VALID_MINISTRIES, VALID_SECTORS

# ── Canonicalise known entities ───────────────────────────────────────────────
_SECTOR_MAP = {s.lower(): s for s in VALID_SECTORS}
_MINISTRY_MAP = {m.lower(): m for m in VALID_MINISTRIES}

# Fields/topics that the system explicitly does NOT have
_OUT_OF_SCOPE_KEYWORDS = [
    "contractor", "legal", "court", "tender", "bid", "corruption",
    "criminal", "loan", "insurance", "vendor", "supplier", "ngo",
    "beneficiary", "rti", "audit report", "gst",
]

# Project ID patterns
_PID_PATTERN = re.compile(
    r'\b(prj-\d{6}|p-[a-z]+-\d{4,}|prj-[a-z0-9-]+)\b',
    re.IGNORECASE,
)


# ── Rule-based intent parser ──────────────────────────────────────────────────

def parse_intent(question: str) -> dict:
    """
    Parse a natural-language question into a structured query dict.

    The dict always contains 'intent'. Additional keys depend on intent.
    If the system cannot answer, 'clarifying_question' is set and intent
    is AMBIGUOUS or OUT_OF_SCOPE.
    """
    q = question.strip().lower()

    # ── 1. Out-of-scope check (hard boundary) ────────────────────────────────
    for kw in _OUT_OF_SCOPE_KEYWORDS:
        if kw in q:
            return {
                "intent": "OUT_OF_SCOPE",
                "clarifying_question": (
                    "I don't have access to that information. "
                    "I can only answer questions about project risk scores, "
                    "milestone delays, cost growth, anomaly flags, and SHAP-based "
                    "explanations. Could you rephrase your question around these topics?"
                ),
            }

    # ── 2. Extract project IDs ────────────────────────────────────────────────
    pids = [m.upper() for m in _PID_PATTERN.findall(q)]

    # ── 3. EXPLAIN_PROJECT: "why is <PID> flagged/at risk" ───────────────────
    explain_patterns = [
        r'\bwhy\b', r'\bexplain\b', r'\breason\b', r'\bwhat caused\b',
        r'\bflagged\b', r'\bflag\b',
    ]
    if pids and any(re.search(p, q) for p in explain_patterns):
        return {
            "intent":     "EXPLAIN_PROJECT",
            "project_id": pids[0],
        }

    # ── 4. COMPARE_PROJECTS ───────────────────────────────────────────────────
    if re.search(r'\bcompare\b|\bvs\.?\b|\bversus\b', q) and len(pids) >= 2:
        return {
            "intent":      "COMPARE_PROJECTS",
            "project_ids": pids[:5],   # cap at 5
        }

    # ── 5. AGGREGATE queries ─────────────────────────────────────────────────
    agg_intent = _try_parse_aggregate(q)
    if agg_intent:
        return agg_intent

    # ── 6. FILTER_PROJECTS (the most common intent) ───────────────────────────
    filters = _extract_filters(q)
    if filters:
        result: dict = {"intent": "FILTER_PROJECTS", **filters}
        # If a specific project ID is also given, add it
        if pids:
            result["project_ids"] = pids
        return result

    # ── 7. Single-project lookup without explain trigger ─────────────────────
    if pids and len(pids) == 1:
        return {
            "intent":     "EXPLAIN_PROJECT",
            "project_id": pids[0],
        }

    # ── 8. Ambiguous — ask one clarifying question ────────────────────────────
    return {
        "intent": "AMBIGUOUS",
        "clarifying_question": _pick_clarifying_question(q),
    }


# ── Filter extraction helpers ─────────────────────────────────────────────────

def _extract_filters(q: str) -> dict:
    """Extract structured filter fields from the query string."""
    filters: dict = {}

    # Risk band
    if re.search(r'\bcritical\b', q):
        filters["risk_band"] = "Critical"
    elif re.search(r'\bhigh.risk\b|high risk', q):
        filters["risk_band"] = "High"
    elif re.search(r'\bmedium.risk\b|medium risk', q):
        filters["risk_band"] = "Medium"
    elif re.search(r'\blow.risk\b|low risk', q):
        filters["risk_band"] = "Low"

    # Sector
    for kw, canonical in _SECTOR_MAP.items():
        if re.search(r'\b' + re.escape(kw) + r'\b', q):
            filters["sector"] = canonical
            break

    # Ministry
    for kw, canonical in _MINISTRY_MAP.items():
        if kw in q:
            filters["ministry"] = canonical
            break

    # Milestone delay threshold
    delay_m = re.search(
        r'milestone[s]?\s+dela(?:y|yed|ys)\s+(?:over|more than|greater than|>\s*)'
        r'\s*(\d+(?:\.\d+)?)\s*month',
        q,
    )
    if delay_m:
        filters["min_milestone_delay_months"] = float(delay_m.group(1))

    # Cost overrun threshold
    overrun_m = re.search(
        r'cost\s+(?:overrun|growth|above)\s+(?:above|over|more than|>\s*)?'
        r'\s*(\d+(?:\.\d+)?)\s*%',
        q,
    )
    if overrun_m:
        filters["min_cost_growth_pct"] = float(overrun_m.group(1))

    # Risk score threshold
    score_m = re.search(r'risk\s+score\s+(?:above|over|>\s*)?\s*(0\.\d+|\d+)', q)
    if score_m:
        v = float(score_m.group(1))
        filters["min_risk_score"] = v if v <= 1.0 else v / 100.0

    # Anomaly filter
    if re.search(r'\banomal(?:y|ous|ies)\b', q):
        filters["anomaly_flag"] = True

    # Sort / limit
    if re.search(r'\btop\s*(\d+)\b', q):
        m = re.search(r'\btop\s*(\d+)\b', q)
        if m:
            filters["limit"] = int(m.group(1))

    return filters


def _try_parse_aggregate(q: str) -> Optional[dict]:
    """Try to parse an aggregation/ranking question."""
    # "Which sector has the most cost overruns?"
    if re.search(r'which\s+sector.+most\s+cost\s+overrun|sector.+most.+overrun', q):
        return {"intent": "AGGREGATE", "metric": "cost_overrun", "group_by": "sector"}

    # "Which sector has the most delays?"
    if re.search(r'which\s+sector.+most\s+delay|sector.+most.+delay', q):
        return {"intent": "AGGREGATE", "metric": "delay", "group_by": "sector"}

    # "Which sector has most anomalies?"
    if re.search(r'which\s+sector.+most\s+anomal', q):
        return {"intent": "AGGREGATE", "metric": "anomaly", "group_by": "sector"}

    # "Highest risk sector" / "sector with highest average risk"
    if re.search(r'highest\s+(?:average\s+)?risk\s+sector|sector.+highest\s+risk', q):
        return {"intent": "AGGREGATE", "metric": "avg_risk", "group_by": "sector"}

    return None


def _pick_clarifying_question(q: str) -> str:
    """Return a context-appropriate single clarifying question."""
    if "sector" not in q and "ministry" not in q:
        return (
            "Could you tell me which sector or ministry you're interested in? "
            "For example: 'high-risk projects in the Roads sector'."
        )
    if "risk" not in q and "delay" not in q and "overrun" not in q:
        return (
            "What metric are you interested in — risk score, milestone delays, "
            "or cost overruns? Please specify so I can fetch the right data."
        )
    return (
        "Could you please be more specific? "
        "For example, include a project ID, sector, risk band, or time period."
    )
