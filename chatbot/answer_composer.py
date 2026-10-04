"""
PRAGYA AI — Answer Composer  (v2)
===================================
Produces the final natural-language answer from retrieved data.

Key contract:
  - Every numeric claim comes VERBATIM from retrieved rows.
  - The LLM (if used) sees only the retrieved rows — not the full database.
  - EXPLAIN_PROJECT uses explanation passthrough: text is taken directly
    from the top_reasons field stored by explain_risk(), so it is
    provably identical to what the dashboard shows.
  - If retrieval returned zero rows, we say so plainly.
  - Every answer cites which projects/data it came from (IDs + as_of_date).
"""
from __future__ import annotations

from datetime import date
from typing import Optional


# ── Disclaimer template ───────────────────────────────────────────────────────

def _disclaimer(as_of_date: str) -> str:
    return (
        f"\n\n⚠️ *Answers are generated from stored risk data as of "
        f"{as_of_date} and are for review support only — not a final finding. "
        f"Verify with the dashboard before acting.*"
    )


# ── Main composer ─────────────────────────────────────────────────────────────

def compose_answer(
    retrieved_data: dict,
    original_question: str,
) -> dict:
    """
    Compose a grounded answer from the retrieval result.

    Parameters
    ----------
    retrieved_data : dict
        Output of retriever.retrieve_grounded_data().
    original_question : str
        The officer's original question (used for context, NOT for generation).

    Returns
    -------
    dict with keys:
        answer_text          str
        referenced_projects  list[str]
        clarifying_question  str | None
        as_of_date           str
        query_run            str   (for audit trail)
    """
    as_of_today = str(date.today())
    result_type = retrieved_data.get("type", "error")
    query_run   = retrieved_data.get("query_run", "")

    # ── Error / empty result ─────────────────────────────────────────────────
    if result_type == "error":
        msg = retrieved_data.get("error", "An unknown retrieval error occurred.")
        return {
            "answer_text":         msg,
            "referenced_projects": [],
            "as_of_date":          as_of_today,
            "query_run":           query_run,
        }

    # ── EXPLANATION PASSTHROUGH ───────────────────────────────────────────────
    # When explaining a specific project, we skip LLM generation entirely and
    # format the stored top_reasons directly. This guarantees the chatbot
    # never invents a different explanation from what the dashboard shows.
    if result_type == "explanation":
        pid     = retrieved_data.get("project_id", "?")
        data    = retrieved_data.get("data", {})
        as_of   = retrieved_data.get("as_of_date", as_of_today)

        risk_band   = data.get("risk_band", "Unknown")
        risk_score  = data.get("composite_risk_score", 0.0)
        top_reasons = data.get("top_reasons", [])
        anomaly_f   = data.get("anomaly_flag", False)
        anomaly_r   = data.get("anomaly_reasons", data.get("anomaly_reason", ""))

        # Format risk score as percentage
        score_pct = round(risk_score * 100, 1)

        lines = [
            f"**Project {pid}** is classified as **{risk_band} Risk** "
            f"(composite score: {score_pct}/100).",
            "",
            f"*Data as of: {as_of}*",
            "",
            "**Top reasons flagged by the model:**",
        ]
        if top_reasons:
            for reason in top_reasons:
                lines.append(f"• {reason}")
        else:
            lines.append("• No SHAP reasons available for this project.")

        if anomaly_f and anomaly_r:
            lines += ["", f"⚠️ **Anomaly detected:** {anomaly_r}"]
        elif anomaly_f:
            lines += ["", "⚠️ **An anomaly was detected in recent updates for this project.**"]

        p_cost  = data.get("p_cost", 0)
        p_time  = data.get("p_time", 0)
        p_impl  = data.get("p_impl", 0)
        lines += [
            "",
            f"Individual risk probabilities — "
            f"Cost overrun: {p_cost*100:.1f}% | "
            f"Time delay: {p_time*100:.1f}% | "
            f"Implementation: {p_impl*100:.1f}%",
        ]

        lines.append(_disclaimer(as_of))

        return {
            "answer_text":         "\n".join(lines),
            "referenced_projects": [pid],
            "as_of_date":          as_of,
            "query_run":           query_run,
        }

    # ── COMPARISON ────────────────────────────────────────────────────────────
    if result_type == "comparison":
        data    = retrieved_data.get("data", [])
        missing = retrieved_data.get("missing", [])
        as_of   = retrieved_data.get("as_of_date", as_of_today)
        pids    = [r["project_id"] for r in data]

        if not data:
            return {
                "answer_text":         "None of the requested projects were found in your authorised scope.",
                "referenced_projects": [],
                "as_of_date":          as_of,
                "query_run":           query_run,
            }

        lines = [f"**Project Comparison** (as of {as_of})", ""]
        header = (
            f"{'Project':<20} {'Sector':<15} {'Risk Band':<12} "
            f"{'Score':>6}  {'Progress':>9}  {'Delay (mo)':>11}  {'Cost Growth':>12}"
        )
        lines.append(header)
        lines.append("-" * len(header))

        for r in data:
            lines.append(
                f"{r['project_id']:<20} "
                f"{r.get('sector','?'):<15} "
                f"{r.get('risk_band','?'):<12} "
                f"{r.get('composite_risk_score',0)*100:>5.1f}%  "
                f"{r.get('physical_progress_pct',0):>8.1f}%  "
                f"{r.get('milestone_delay_months',0):>10.1f}  "
                f"{r.get('cost_growth_pct',0):>10.1f}%"
            )

        if missing:
            lines += ["", f"*Note: Projects not found or outside your scope: {', '.join(missing)}*"]

        lines.append(_disclaimer(as_of))
        return {
            "answer_text":         "\n".join(lines),
            "referenced_projects": pids,
            "as_of_date":          as_of,
            "query_run":           query_run,
        }

    # ── FILTERED LIST ─────────────────────────────────────────────────────────
    if result_type == "filtered_list":
        data  = retrieved_data.get("data", [])
        count = retrieved_data.get("count", 0)
        as_of = retrieved_data.get("as_of_date", as_of_today)
        msg   = retrieved_data.get("message", "")

        if not data:
            return {
                "answer_text":         msg or "No projects match the specified criteria in your authorised scope.",
                "referenced_projects": [],
                "as_of_date":          as_of,
                "query_run":           query_run,
            }

        pids = [r["project_id"] for r in data]
        shown = len(data)

        lines = [
            f"Found **{count}** project(s) matching your criteria "
            f"(showing top {shown}, as of {as_of}):",
            "",
        ]
        for r in data:
            score_pct = round(r.get("composite_risk_score", 0) * 100, 1)
            delay     = r.get("milestone_delay_months", 0)
            c_growth  = r.get("cost_growth_pct", 0)
            lines.append(
                f"• **{r['project_id']}** [{r.get('sector','?')}] — "
                f"Risk: {score_pct}/100 ({r.get('risk_band','?')}) | "
                f"Delay: {delay:.1f} mo | "
                f"Cost growth: {c_growth:.1f}%"
            )

        lines.append(_disclaimer(as_of))
        return {
            "answer_text":         "\n".join(lines),
            "referenced_projects": pids,
            "as_of_date":          as_of,
            "query_run":           query_run,
        }

    # ── AGGREGATION ───────────────────────────────────────────────────────────
    if result_type == "aggregation":
        data     = retrieved_data.get("data", [])
        metric   = retrieved_data.get("metric", "cost_overrun")
        group_by = retrieved_data.get("group_by", "sector")

        if not data:
            return {
                "answer_text":         "No aggregation data available.",
                "referenced_projects": [],
                "as_of_date":          as_of_today,
                "query_run":           query_run,
            }

        metric_labels = {
            "cost_overrun": "cost overruns",
            "delay":        "milestone delays",
            "anomaly":      "flagged anomalies",
            "avg_risk":     "average composite risk score",
        }
        label = metric_labels.get(metric, metric)
        count_key = "count" if "count" in data[0] else "avg_risk"

        top = data[0]
        top_sector = top.get(group_by, "?")
        top_value  = top.get(count_key, "?")

        lines = [
            f"**Ranking by {label} per {group_by}** (as of {as_of_today}):",
            "",
        ]
        for i, row in enumerate(data[:10], start=1):
            val = row.get(count_key, 0)
            val_str = f"{val:.3f}" if isinstance(val, float) else str(val)
            lines.append(
                f"{i}. **{row.get(group_by,'?')}** — {label}: {val_str}"
            )

        if metric in ("cost_overrun", "delay"):
            lines += [
                "",
                f"**The {top_sector} sector currently has the most {label}** "
                f"({top_value} flagged project(s)).",
            ]
        else:
            lines += [
                "",
                f"**The {top_sector} sector has the highest {label}** "
                f"({top_value:.3f}).",
            ]

        lines.append(_disclaimer(as_of_today))
        return {
            "answer_text":         "\n".join(lines),
            "referenced_projects": [],
            "as_of_date":          as_of_today,
            "query_run":           query_run,
        }

    # ── Fallback ──────────────────────────────────────────────────────────────
    return {
        "answer_text":         "I could not formulate an answer from the retrieved data.",
        "referenced_projects": [],
        "as_of_date":          as_of_today,
        "query_run":           query_run,
    }
