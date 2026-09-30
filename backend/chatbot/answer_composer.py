"""
chatbot/answer_composer.py
==========================
Composes a grounded answer from retrieved data rows.

Architecture:
  1. For "explain_project": directly format the stored SHAP top_reasons
     WITHOUT any LLM call — the answer is provably identical to what
     the dashboard shows. LLM is skipped entirely.

  2. For everything else: pass ONLY the retrieved rows (not the whole DB)
     to the LLM with a strict data-only prompt. The LLM structures/narrates
     the data — it is explicitly forbidden from adding numbers, projects,
     or reasons not in the supplied rows.

  3. If zero rows: return a plain "no data" message, never a guess.

Returns:
  {
    "answer_text": str,
    "referenced_projects": list[str],  # project IDs cited
    "as_of_date": str,
    "grounding_method": "direct_shap" | "llm_grounded" | "zero_results" | "no_llm",
  }
"""

import json
import os
from datetime import datetime


def _call_gemini_grounded(prompt: str) -> str:
    """Call Gemini for answer composition only. Never for facts."""
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
        print(f"[answer_composer] Gemini call failed: {e}")
        return ""


def _format_project_card(p: dict) -> str:
    """Format a single project's data as a structured text block."""
    lines = [
        f"Project ID: {p['project_id']}",
        f"Name: {p['project_name']}",
        f"Sector: {p['sector']}",
        f"Ministry: {p['ministry']}",
        f"Agency: {p['implementing_agency']}",
        f"Risk Score: {p['risk_score']:.1f}/100",
        f"Risk Level: {p['risk_level']}",
        f"Anomaly Flag: {'YES - flagged by anomaly detector' if p['is_anomalous'] else 'No'}",
        f"Delay: {p['delay_months']:.1f} months",
        f"Cost Overrun: {p['cost_overrun_pct']:.1f}%",
        f"Physical Progress: {p['physical_progress_pct']:.1f}%",
        f"Status: {p['status']}",
    ]
    if p.get("sector_percentile_delay") is not None:
        lines.append(f"Delay Percentile (sector): {p['sector_percentile_delay']}th")
    if p.get("sector_percentile_cost_overrun") is not None:
        lines.append(f"Cost Overrun Percentile (sector): {p['sector_percentile_cost_overrun']}th")
    if p.get("shap_top_reasons"):
        lines.append("AI Risk Reasons (SHAP):")
        for i, reason in enumerate(p["shap_top_reasons"], 1):
            lines.append(f"  {i}. {reason}")
    return "\n".join(lines)


def _format_sector_summary_card(s: dict) -> str:
    """Format a sector summary row."""
    return (
        f"Sector: {s['sector']} | "
        f"Projects: {s['project_count']} | "
        f"Critical: {s['critical_projects']} | "
        f"High: {s['high_risk_projects']} | "
        f"Avg Cost Overrun: {s['avg_cost_overrun_pct']}% | "
        f"Avg Delay: {s['avg_delay_months']} months"
    )


def compose(
    question: str,
    structured_query: dict,
    retrieval_result: dict,
) -> dict:
    """
    Main entry point.

    Args:
        question: original officer question
        structured_query: output of intent_parser.parse_intent()
        retrieval_result: output of retriever.fetch()

    Returns:
        answer dict with answer_text, referenced_projects, as_of_date,
        grounding_method
    """
    intent = structured_query.get("intent", "unknown")
    rows = retrieval_result.get("rows", [])
    as_of_date = retrieval_result.get("as_of_date", datetime.utcnow().strftime("%Y-%m-%d"))

    # ── CANNOT ANSWER / OUT OF SCOPE ────────────────────────────────────────
    if intent == "cannot_answer":
        return {
            "answer_text": structured_query.get(
                "out_of_scope_reason",
                "I don't have that information in the PRAGYA risk data store."
            ),
            "referenced_projects": [],
            "as_of_date": as_of_date,
            "grounding_method": "cannot_answer",
        }

    # ── CLARIFYING QUESTION NEEDED ──────────────────────────────────────────
    if structured_query.get("clarifying_question"):
        return {
            "answer_text": structured_query["clarifying_question"],
            "referenced_projects": [],
            "as_of_date": as_of_date,
            "grounding_method": "clarification",
        }

    # ── ZERO RESULTS ────────────────────────────────────────────────────────
    if not rows:
        query_desc = retrieval_result.get("query_log", "your query")
        return {
            "answer_text": (
                f"No projects matched your query ({query_desc}). "
                "This could mean no projects in the current data store meet those criteria, "
                "or the project ID you mentioned doesn't exist in your accessible scope."
            ),
            "referenced_projects": [],
            "as_of_date": as_of_date,
            "grounding_method": "zero_results",
        }

    # ── EXPLAIN PROJECT — direct SHAP pass-through, no LLM ─────────────────
    if intent == "explain_project":
        proj = rows[0]
        reasons = proj.get("shap_top_reasons", [])
        anomaly_note = (
            "\n\n**Anomaly Flag:** This project has been flagged by the PRAGYA anomaly detector, "
            "indicating statistically unusual behaviour relative to its peer group."
            if proj.get("is_anomalous") else ""
        )
        if reasons:
            reasons_text = "\n".join(f"  {i}. {r}" for i, r in enumerate(reasons, 1))
            answer = (
                f"**{proj['project_name']}** ({proj['project_id']}) "
                f"has a risk score of **{proj['risk_score']:.1f}/100** "
                f"(band: **{proj['risk_level']}**).\n\n"
                f"**Top AI Risk Reasons (from SHAP explainability):**\n{reasons_text}"
                f"{anomaly_note}"
            )
        else:
            answer = (
                f"**{proj['project_name']}** ({proj['project_id']}) "
                f"has a risk score of **{proj['risk_score']:.1f}/100** "
                f"(band: **{proj['risk_level']}**). "
                f"Detailed SHAP explanations are not yet available for this project. "
                f"Please use the AI Risk Insights page for the full breakdown."
                f"{anomaly_note}"
            )
        return {
            "answer_text": answer,
            "referenced_projects": [proj["project_id"]],
            "as_of_date": proj.get("as_of_date", as_of_date),
            "grounding_method": "direct_shap",
        }

    # ── SECTOR SUMMARY — LLM narrates only what retriever returned ──────────
    if intent == "sector_summary":
        referenced_ids = []
        for row in rows:
            referenced_ids.extend(row.get("project_ids", []))

        data_block = "\n".join(_format_sector_summary_card(s) for s in rows)
        prompt = f"""You are composing a brief factual summary for a government monitoring officer.

STRICT RULES:
1. Use ONLY the data provided below. Do NOT add any numbers, sectors, or projects not in this data.
2. If the data doesn't answer the question, say so plainly.
3. Do NOT invent risk reasons, project names, or percentages.
4. Keep the answer under 200 words.
5. Cite sector names and counts directly from the data.

Data (as of {as_of_date}):
{data_block}

Officer's question: "{question}"

Write a concise factual answer:"""

        answer_text = _call_gemini_grounded(prompt)
        if not answer_text:
            # Fallback: plain text summary without LLM
            lines = [f"Sector risk summary as of {as_of_date}:"]
            for s in rows:
                lines.append(
                    f"  • {s['sector']}: {s['project_count']} projects, "
                    f"{s['critical_projects']} Critical, {s['high_risk_projects']} High, "
                    f"avg delay {s['avg_delay_months']} months, avg cost overrun {s['avg_cost_overrun_pct']}%"
                )
            answer_text = "\n".join(lines)
            grounding_method = "no_llm"
        else:
            grounding_method = "llm_grounded"

        return {
            "answer_text": answer_text,
            "referenced_projects": referenced_ids[:20],
            "as_of_date": as_of_date,
            "grounding_method": grounding_method,
        }

    # ── COMPARE / LIST PROJECTS — LLM narrates only the retrieved rows ──────
    referenced_ids = [p["project_id"] for p in rows]
    data_block = "\n\n---\n\n".join(_format_project_card(p) for p in rows)

    prompt = f"""You are composing a brief factual answer for a government monitoring officer using the PRAGYA AI system.

STRICT RULES:
1. Use ONLY the project data provided below. Do NOT add any numbers, projects, risk scores, or reasons not in this data.
2. If the data doesn't fully answer the question, say so explicitly — do not guess.
3. Do NOT invent explanations, paraphrase risk scores loosely, or add context not in the data.
4. Reference each project by its ID.
5. Keep the answer clear and under 300 words.
6. For comparisons: structure the answer to clearly compare the specific metrics mentioned.

Retrieved project data (as of {as_of_date}):
{data_block}

Officer's question: "{question}"

Write a concise factual answer based ONLY on the data above:"""

    answer_text = _call_gemini_grounded(prompt)
    if not answer_text:
        # Fallback: plain text listing without LLM
        lines = [f"Found {len(rows)} project(s) as of {as_of_date}:"]
        for p in rows:
            lines.append(
                f"  • {p['project_id']} — {p['project_name']}: "
                f"Risk {p['risk_score']:.1f}/100 ({p['risk_level']}), "
                f"Delay {p['delay_months']} months, Cost Overrun {p['cost_overrun_pct']}%"
            )
        answer_text = "\n".join(lines)
        grounding_method = "no_llm"
    else:
        grounding_method = "llm_grounded"

    return {
        "answer_text": answer_text,
        "referenced_projects": referenced_ids,
        "as_of_date": as_of_date,
        "grounding_method": grounding_method,
    }
