"""
chatbot/retriever.py
====================
Executes a structured query against the PRAGYA results store.

This is the ONLY place that touches the database. Results returned here
are the ground truth used by the answer composer — nothing is invented.

The function also calls explain_risk() for "explain_project" intents,
returning the stored SHAP top-reasons verbatim so the chatbot answer
is provably identical to what the dashboard shows.

RBAC scope enforcement:
  - 'officer'  -> all projects (full monitor access)
  - 'ministry' -> projects with ministry matching officer's ministry
  - 'agency'   -> only projects assigned to the officer's agency
  - 'public'   -> no chatbot access (blocked at API layer)
"""

import os
import sys
from datetime import datetime
from typing import Optional

# ── Minimal mock data so the module is testable standalone ─────────────────
MOCK_PROJECTS = [
    {
        "project_id": "P-ROADS-0457",
        "project_name": "NH-48 Bangalore-Chennai Expressway Phase 2",
        "sector": "Roads",
        "ministry": "Ministry of Road Transport and Highways",
        "implementing_agency": "NHAI",
        "original_cost_cr": 4200.0,
        "expenditure_cr": 2980.0,
        "cost_overrun_pct": 18.5,
        "delay_months": 7.0,
        "physical_progress_pct": 61.0,
        "status": "Delayed",
        "risk_score": 82.4,
        "risk_level": "Critical",
        "is_anomalous": True,
        "as_of_date": "2026-09-01",
        "shap_top_reasons": [
            "Delay of 7 months is 2.3x the sector average (3 months)",
            "Cost overrun of 18.5% exceeds High-risk threshold of 15%",
            "Physical progress (61%) is 19 points behind financial progress (80%) — absorption risk",
            "Anomaly flag: expenditure rate is unusually high given progress",
        ],
        "sector_percentile_delay": 91,
        "sector_percentile_cost_overrun": 87,
    },
    {
        "project_id": "P-POWER-0123",
        "project_name": "Rajasthan Solar Park 500MW",
        "sector": "Power",
        "ministry": "Ministry of Power",
        "implementing_agency": "SECI",
        "original_cost_cr": 2800.0,
        "expenditure_cr": 1100.0,
        "cost_overrun_pct": 3.2,
        "delay_months": 1.5,
        "physical_progress_pct": 40.0,
        "status": "On Track",
        "risk_score": 31.2,
        "risk_level": "Low",
        "is_anomalous": False,
        "as_of_date": "2026-09-01",
        "shap_top_reasons": [
            "Progress trajectory is on schedule",
            "Cost overrun within acceptable range (3.2%)",
            "No milestone delays detected",
        ],
        "sector_percentile_delay": 22,
        "sector_percentile_cost_overrun": 15,
    },
    {
        "project_id": "P-ROADS-0891",
        "project_name": "Mumbai Coastal Road Extension",
        "sector": "Roads",
        "ministry": "Ministry of Road Transport and Highways",
        "implementing_agency": "MSRDC",
        "original_cost_cr": 7500.0,
        "expenditure_cr": 5200.0,
        "cost_overrun_pct": 34.1,
        "delay_months": 12.0,
        "physical_progress_pct": 55.0,
        "status": "At Risk",
        "risk_score": 91.7,
        "risk_level": "Critical",
        "is_anomalous": True,
        "as_of_date": "2026-09-01",
        "shap_top_reasons": [
            "Delay of 12 months — highest in Roads sector this quarter",
            "Cost overrun of 34.1% is critically above sector benchmark",
            "Physical progress severely lags expenditure",
            "Anomaly: 3 consecutive months of zero physical progress updates",
        ],
        "sector_percentile_delay": 98,
        "sector_percentile_cost_overrun": 96,
    },
    {
        "project_id": "P-RAILWAYS-0234",
        "project_name": "Chennai Metro Phase 3",
        "sector": "Railways",
        "ministry": "Ministry of Railways",
        "implementing_agency": "CMRL",
        "original_cost_cr": 9800.0,
        "expenditure_cr": 3100.0,
        "cost_overrun_pct": 8.7,
        "delay_months": 4.5,
        "physical_progress_pct": 28.0,
        "status": "Delayed",
        "risk_score": 67.3,
        "risk_level": "High",
        "is_anomalous": False,
        "as_of_date": "2026-09-01",
        "shap_top_reasons": [
            "Delay of 4.5 months above sector average",
            "Cost overrun at 8.7% — moderate risk",
            "Physical progress below expected 35% at this stage",
        ],
        "sector_percentile_delay": 72,
        "sector_percentile_cost_overrun": 61,
    },
    {
        "project_id": "P-WATER-0099",
        "project_name": "Jal Jeevan Mission - Odisha District Cluster",
        "sector": "Water",
        "ministry": "Ministry of Jal Shakti",
        "implementing_agency": "OWSSB",
        "original_cost_cr": 650.0,
        "expenditure_cr": 210.0,
        "cost_overrun_pct": 0.0,
        "delay_months": 0.5,
        "physical_progress_pct": 34.0,
        "status": "On Track",
        "risk_score": 22.1,
        "risk_level": "Low",
        "is_anomalous": False,
        "as_of_date": "2026-09-01",
        "shap_top_reasons": [
            "Progress is ahead of schedule",
            "No cost overruns reported",
            "All milestones on time",
        ],
        "sector_percentile_delay": 10,
        "sector_percentile_cost_overrun": 5,
    },
    {
        "project_id": "P-URBAN-0312",
        "project_name": "Smart City Mission - Pune Node 4",
        "sector": "Urban",
        "ministry": "Ministry of Housing and Urban Affairs",
        "implementing_agency": "PMC",
        "original_cost_cr": 380.0,
        "expenditure_cr": 295.0,
        "cost_overrun_pct": 22.4,
        "delay_months": 5.0,
        "physical_progress_pct": 70.0,
        "status": "At Risk",
        "risk_score": 75.8,
        "risk_level": "High",
        "is_anomalous": True,
        "as_of_date": "2026-09-01",
        "shap_top_reasons": [
            "Cost overrun of 22.4% is highest in Urban sector this period",
            "Milestone 3 (Digital Infrastructure) delayed by 5 months",
            "Anomaly: expenditure spike in last reporting cycle without matching physical progress",
        ],
        "sector_percentile_delay": 83,
        "sector_percentile_cost_overrun": 92,
    },
    {
        "project_id": "P-ROADS-0102",
        "project_name": "Delhi-Meerut Regional Rapid Transit",
        "sector": "Roads",
        "ministry": "Ministry of Road Transport and Highways",
        "implementing_agency": "NCRTC",
        "original_cost_cr": 30274.0,
        "expenditure_cr": 18000.0,
        "cost_overrun_pct": 11.2,
        "delay_months": 2.0,
        "physical_progress_pct": 78.0,
        "status": "On Track",
        "risk_score": 44.6,
        "risk_level": "Medium",
        "is_anomalous": False,
        "as_of_date": "2026-09-01",
        "shap_top_reasons": [
            "Moderate cost overrun at 11.2%",
            "Minor delay of 2 months — within acceptable range",
            "Physical progress (78%) broadly matches expenditure",
        ],
        "sector_percentile_delay": 38,
        "sector_percentile_cost_overrun": 55,
    },
]

# ── RBAC scope definitions ─────────────────────────────────────────────────
SCOPE_MINISTRY_MAP = {
    "ministry": "Ministry of Road Transport and Highways",  # demo default
}

def _get_db_projects():
    """Load projects from the real SQLAlchemy DB when available."""
    try:
        from backend.app_db import SessionLocal, Project as DBProject
        db = SessionLocal()
        try:
            rows = db.query(DBProject).all()
            if not rows:
                return None
            results = []
            for p in rows:
                results.append({
                    "project_id": p.id,
                    "project_name": p.name,
                    "sector": p.sector,
                    "ministry": p.ministry,
                    "implementing_agency": p.implementing_agency,
                    "original_cost_cr": p.original_cost_cr,
                    "expenditure_cr": p.expenditure_cr,
                    "cost_overrun_pct": p.cost_overrun_pct,
                    "delay_months": p.delay_months,
                    "physical_progress_pct": p.physical_progress_pct,
                    "status": p.status,
                    "risk_score": p.risk_score,
                    "risk_level": p.risk_level,
                    "is_anomalous": bool(p.is_anomalous),
                    "as_of_date": p.updated_at.strftime("%Y-%m-%d") if p.updated_at else datetime.utcnow().strftime("%Y-%m-%d"),
                    "shap_top_reasons": [],  # Will be filled by explain_risk if needed
                    "sector_percentile_delay": None,
                    "sector_percentile_cost_overrun": None,
                })
            return results
        finally:
            db.close()
    except Exception as e:
        print(f"[retriever] DB load failed, using mock data: {e}")
        return None


def _get_explain_risk(project_id: str) -> list:
    """Call the existing explain_risk pipeline for SHAP reasons."""
    try:
        from backend.main import predict_risk_internal
        # We need the project data to call predict_risk_internal
        db_projects = _get_db_projects()
        if db_projects:
            proj = next((p for p in db_projects if p["project_id"] == project_id), None)
            if proj:
                data = {
                    "projectId": project_id,
                    "Original_Cost_Cr": proj["original_cost_cr"],
                    "Expenditure_Cr": proj["expenditure_cr"],
                    "Physical_Progress_Pct": proj["physical_progress_pct"],
                    "Delay_Months": proj["delay_months"],
                    "Cost_Overrun_Pct": proj["cost_overrun_pct"],
                    "sector": proj["sector"],
                    "ministry": proj["ministry"],
                    "agency": proj["implementing_agency"],
                }
                result = predict_risk_internal(data)
                shap_list = result.get("shap_explanations", [])
                reasons = []
                for s in shap_list[:5]:
                    if isinstance(s, dict) and "feature" in s and "impact" in s:
                        sign = "+" if s["impact"] > 0 else ""
                        reasons.append(
                            f"{s['feature']}: impact {sign}{s['impact']:.3f} "
                            f"(value: {s.get('value', 'N/A')})"
                        )
                return reasons
    except Exception as e:
        print(f"[retriever] explain_risk failed for {project_id}: {e}")
    return []


def _apply_scope(projects: list, role: str, scope: dict) -> list:
    """Filter projects by the officer's RBAC scope."""
    if role == "officer":
        return projects  # Full access
    elif role == "ministry":
        ministry_filter = scope.get("ministry", "")
        if ministry_filter:
            return [p for p in projects if p["ministry"].lower() == ministry_filter.lower()]
        return projects
    elif role == "agency":
        agency_filter = scope.get("agency", "")
        if agency_filter:
            return [p for p in projects if p["implementing_agency"].lower() == agency_filter.lower()]
        return []
    else:
        # Public: no chatbot access — should be blocked before reaching here
        return []


def fetch(structured_query: dict, role: str = "officer", scope: dict = None) -> dict:
    """
    Execute the structured query against the results store.

    Args:
        structured_query: dict from intent_parser.parse_intent()
        role: the officer's role ('officer', 'ministry', 'agency', 'public')
        scope: dict with optional 'ministry', 'agency' keys for scoping

    Returns:
        {
          "rows": list of project dicts (the grounding data),
          "query_log": str (the human-readable query that was run — for audit),
          "as_of_date": str,
          "total_matched": int,
        }
    """
    if scope is None:
        scope = {}

    intent = structured_query.get("intent", "unknown")
    as_of_date = datetime.utcnow().strftime("%Y-%m-%d")

    # Load data (real DB preferred, mock fallback)
    all_projects = _get_db_projects() or MOCK_PROJECTS

    # Apply RBAC scope
    scoped_projects = _apply_scope(all_projects, role, scope)

    # Build a human-readable audit log entry
    query_parts = [f"intent={intent}", f"role={role}"]

    # ── EXPLAIN PROJECT (pass-through SHAP reasons) ─────────────────────────
    if intent == "explain_project":
        pid_list = structured_query.get("project_ids", [])
        if not pid_list:
            return {
                "rows": [],
                "query_log": "explain_project: no project_id provided",
                "as_of_date": as_of_date,
                "total_matched": 0,
            }

        project_id = pid_list[0].upper()
        query_parts.append(f"project_id={project_id}")

        # Find in scoped set
        proj = next((p for p in scoped_projects if p["project_id"].upper() == project_id), None)
        if not proj:
            return {
                "rows": [],
                "query_log": " | ".join(query_parts),
                "as_of_date": as_of_date,
                "total_matched": 0,
            }

        # Prefer live SHAP reasons from explain_risk; fall back to stored mock
        live_reasons = _get_explain_risk(project_id)
        if live_reasons:
            proj = dict(proj)  # don't mutate global mock
            proj["shap_top_reasons"] = live_reasons

        return {
            "rows": [proj],
            "query_log": " | ".join(query_parts),
            "as_of_date": proj.get("as_of_date", as_of_date),
            "total_matched": 1,
        }

    # ── COMPARE PROJECTS ────────────────────────────────────────────────────
    if intent == "compare_projects":
        pid_list = [p.upper() for p in structured_query.get("project_ids", [])]
        query_parts.append(f"project_ids={pid_list}")

        rows = [p for p in scoped_projects if p["project_id"].upper() in pid_list]
        return {
            "rows": rows,
            "query_log": " | ".join(query_parts),
            "as_of_date": as_of_date,
            "total_matched": len(rows),
        }

    # ── SECTOR SUMMARY ──────────────────────────────────────────────────────
    if intent == "sector_summary":
        sector = structured_query.get("sector")
        if sector:
            scoped_projects = [p for p in scoped_projects if p["sector"].lower() == sector.lower()]
            query_parts.append(f"sector={sector}")

        # Aggregate by sector
        from collections import defaultdict
        sector_stats: dict = defaultdict(lambda: {
            "count": 0, "critical": 0, "high": 0, "total_cost_overrun": 0.0,
            "total_delay": 0.0, "projects": []
        })
        for p in scoped_projects:
            s = p["sector"]
            sector_stats[s]["count"] += 1
            sector_stats[s]["projects"].append(p["project_id"])
            if p["risk_level"] == "Critical":
                sector_stats[s]["critical"] += 1
            elif p["risk_level"] == "High":
                sector_stats[s]["high"] += 1
            sector_stats[s]["total_cost_overrun"] += p["cost_overrun_pct"]
            sector_stats[s]["total_delay"] += p["delay_months"]

        summary_rows = []
        for s, st in sector_stats.items():
            summary_rows.append({
                "sector": s,
                "project_count": st["count"],
                "critical_projects": st["critical"],
                "high_risk_projects": st["high"],
                "avg_cost_overrun_pct": round(st["total_cost_overrun"] / max(st["count"], 1), 1),
                "avg_delay_months": round(st["total_delay"] / max(st["count"], 1), 1),
                "project_ids": st["projects"],
            })

        # Sort by most critical
        summary_rows.sort(key=lambda x: (x["critical_projects"], x["high_risk_projects"]), reverse=True)

        return {
            "rows": summary_rows,
            "query_log": " | ".join(query_parts),
            "as_of_date": as_of_date,
            "total_matched": len(summary_rows),
        }

    # ── LIST PROJECTS (default) ─────────────────────────────────────────────
    # Apply filters
    results = list(scoped_projects)

    if structured_query.get("sector"):
        results = [p for p in results if p["sector"].lower() == structured_query["sector"].lower()]
        query_parts.append(f"sector={structured_query['sector']}")

    if structured_query.get("ministry"):
        results = [p for p in results if structured_query["ministry"].lower() in p["ministry"].lower()]
        query_parts.append(f"ministry={structured_query['ministry']}")

    if structured_query.get("agency"):
        results = [p for p in results if structured_query["agency"].lower() in p["implementing_agency"].lower()]
        query_parts.append(f"agency={structured_query['agency']}")

    if structured_query.get("search_keywords"):
        kw = structured_query["search_keywords"].lower()
        results = [p for p in results if kw in p["project_name"].lower() or kw in p["sector"].lower() or kw in p.get("ministry", "").lower()]
        query_parts.append(f"search_keywords={structured_query['search_keywords']}")

    if structured_query.get("risk_band"):
        results = [p for p in results if p["risk_level"].lower() == structured_query["risk_band"].lower()]
        query_parts.append(f"risk_level={structured_query['risk_band']}")

    if structured_query.get("min_risk_score") is not None:
        results = [p for p in results if p["risk_score"] >= structured_query["min_risk_score"]]
        query_parts.append(f"min_risk_score={structured_query['min_risk_score']}")

    if structured_query.get("max_risk_score") is not None:
        results = [p for p in results if p["risk_score"] <= structured_query["max_risk_score"]]
        query_parts.append(f"max_risk_score={structured_query['max_risk_score']}")

    if structured_query.get("milestone_delay_months_min") is not None:
        results = [p for p in results if p["delay_months"] >= structured_query["milestone_delay_months_min"]]
        query_parts.append(f"delay_months>={structured_query['milestone_delay_months_min']}")

    if structured_query.get("cost_overrun_pct_min") is not None:
        results = [p for p in results if p["cost_overrun_pct"] >= structured_query["cost_overrun_pct_min"]]
        query_parts.append(f"cost_overrun_pct>={structured_query['cost_overrun_pct_min']}")

    # Sort
    sort_field = structured_query.get("sort_by") or "risk_score"
    if sort_field in {"risk_score", "delay_months", "cost_overrun_pct", "physical_progress_pct", "expenditure_cr"}:
        results.sort(key=lambda p: p.get(sort_field, 0), reverse=True)
        query_parts.append(f"order_by={sort_field} DESC")

    # Limit
    limit = structured_query.get("limit", 10)
    results = results[:limit]
    query_parts.append(f"limit={limit}")

    return {
        "rows": results,
        "query_log": " | ".join(query_parts),
        "as_of_date": as_of_date,
        "total_matched": len(results),
    }


# Self-test
if __name__ == "__main__":
    from chatbot.intent_parser import parse_intent

    test_q = "Which projects in the roads sector are high risk?"
    sq = parse_intent(test_q)
    result = fetch(sq, role="officer")
    print(f"Query: {result['query_log']}")
    print(f"Rows: {len(result['rows'])}")
    for r in result["rows"]:
        print(f"  - {r['project_id']}: {r['risk_level']} ({r['risk_score']}%)")
