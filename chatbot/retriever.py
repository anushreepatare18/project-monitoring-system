"""
PRAGYA AI — Grounded Retriever  (v2)
======================================
Executes structured query dicts (from intent_parser) against the results
store. Enforces RBAC scope. Logs every query run for auditability.

This step is purely deterministic: no LLM involved.
"""
from __future__ import annotations

import json
import logging
from typing import Optional

import pandas as pd

from chatbot.results_store import (
    aggregate_by_sector,
    get_project_record,
    get_store,
    query_store,
)

logger = logging.getLogger(__name__)


def retrieve_grounded_data(
    parsed_query: dict,
    scope: Optional[str] = None,
) -> dict:
    """
    Execute the structured query against the results store.

    Parameters
    ----------
    parsed_query : dict
        Output of intent_parser.parse_intent().
    scope : str, optional
        RBAC scope for the requesting officer.
        "ALL" or None = no restriction.
        A ministry name = restrict to that ministry only.

    Returns
    -------
    dict with 'type' key describing the result shape, plus 'data' and
    optionally 'count', 'as_of_date', 'query_run' (for audit).
    """
    intent = parsed_query.get("intent")
    scope_ministry = scope if (scope and scope.upper() != "ALL") else None

    # Audit: log the exact query
    logger.info("[retriever] intent=%s query=%s scope=%s", intent, parsed_query, scope)

    # ── EXPLAIN_PROJECT ───────────────────────────────────────────────────────
    if intent == "EXPLAIN_PROJECT":
        pid = parsed_query.get("project_id", "")
        record = get_project_record(pid, scope_ministry=scope_ministry)
        if record is None:
            msg = (
                f"Project '{pid}' was not found in your authorised scope."
                if scope_ministry
                else f"Project '{pid}' was not found in the results store."
            )
            return {
                "type":  "error",
                "error": msg,
                "query_run": f"get_project_record('{pid}', scope='{scope_ministry}')",
            }
        return {
            "type":       "explanation",
            "project_id": pid,
            "data":       record,
            "as_of_date": record.get("as_of_date", "unknown"),
            "query_run":  f"get_project_record('{pid}')",
        }

    # ── COMPARE_PROJECTS ──────────────────────────────────────────────────────
    if intent == "COMPARE_PROJECTS":
        pids   = parsed_query.get("project_ids", [])
        store  = get_store()
        if scope_ministry:
            store = store[store["ministry"] == scope_ministry]

        rows   = store[store["project_id"].isin(pids)]
        found  = list(rows["project_id"].unique())
        missing = [p for p in pids if p not in found]

        if rows.empty:
            return {
                "type":  "error",
                "error": (
                    f"None of the requested projects "
                    f"({', '.join(pids)}) were found in your authorised scope."
                ),
                "query_run": f"query_store(project_ids={pids})",
            }

        comparison_cols = [
            "project_id", "sector", "ministry", "risk_band",
            "composite_risk_score", "physical_progress_pct",
            "milestone_delay_months", "cost_growth_pct",
            "anomaly_flag", "as_of_date",
        ]
        data = rows[comparison_cols].to_dict(orient="records")
        return {
            "type":      "comparison",
            "data":      data,
            "missing":   missing,
            "as_of_date": rows["as_of_date"].max(),
            "query_run": f"query_store(project_ids={pids})",
        }

    # ── FILTER_PROJECTS ───────────────────────────────────────────────────────
    if intent == "FILTER_PROJECTS":
        sector      = parsed_query.get("sector")
        ministry    = parsed_query.get("ministry")
        agency      = parsed_query.get("agency")
        risk_band   = parsed_query.get("risk_band")
        min_score   = parsed_query.get("min_risk_score")
        min_delay   = parsed_query.get("min_milestone_delay_months")
        anomaly_flg = parsed_query.get("anomaly_flag")
        proj_ids    = parsed_query.get("project_ids")
        limit       = int(parsed_query.get("limit", 15))
        sort_by     = parsed_query.get("sort_by", "composite_risk_score")

        # Build audit query string
        q_parts: list[str] = []
        if sector:    q_parts.append(f"sector='{sector}'")
        if ministry:  q_parts.append(f"ministry='{ministry}'")
        if risk_band: q_parts.append(f"risk_band='{risk_band}'")
        if min_score: q_parts.append(f"risk_score>={min_score}")
        if min_delay: q_parts.append(f"milestone_delay>={min_delay}")
        if anomaly_flg: q_parts.append("anomaly=True")
        query_str = "query_store(" + ", ".join(q_parts) + f", limit={limit})"

        rows = query_store(
            sector=sector,
            ministry=ministry,
            agency=agency,
            risk_band=risk_band,
            min_risk_score=min_score,
            min_milestone_delay_months=min_delay,
            project_ids=proj_ids,
            anomaly_flag=anomaly_flg,
            sort_by=sort_by,
            sort_asc=False,
            limit=limit,
            scope_ministry=scope_ministry,
        )

        if rows.empty:
            return {
                "type":      "filtered_list",
                "data":      [],
                "count":     0,
                "message":   "No projects match the specified criteria.",
                "query_run": query_str,
            }

        # Keep minimal columns for the answer composer
        display_cols = [
            "project_id", "sector", "ministry", "risk_band",
            "composite_risk_score", "physical_progress_pct",
            "milestone_delay_months", "cost_growth_pct", "as_of_date",
        ]
        data = rows[[c for c in display_cols if c in rows.columns]].to_dict(orient="records")
        total_before_limit = len(query_store(
            sector=sector, ministry=ministry, agency=agency, risk_band=risk_band,
            min_risk_score=min_score, min_milestone_delay_months=min_delay,
            project_ids=proj_ids, anomaly_flag=anomaly_flg,
            scope_ministry=scope_ministry, limit=9999,
        ))
        return {
            "type":      "filtered_list",
            "data":      data,
            "count":     total_before_limit,
            "as_of_date": rows["as_of_date"].max() if "as_of_date" in rows.columns else "unknown",
            "query_run": query_str,
        }

    # ── AGGREGATE ─────────────────────────────────────────────────────────────
    if intent == "AGGREGATE":
        metric   = parsed_query.get("metric", "cost_overrun")
        group_by = parsed_query.get("group_by", "sector")

        if group_by == "sector":
            data = aggregate_by_sector(metric)
        else:
            data = []

        return {
            "type":      "aggregation",
            "metric":    metric,
            "group_by":  group_by,
            "data":      data,
            "query_run": f"aggregate_by_sector('{metric}')",
        }

    # ── Fallback ──────────────────────────────────────────────────────────────
    return {
        "type":  "error",
        "error": "Could not execute query: unhandled intent.",
        "query_run": str(parsed_query),
    }
