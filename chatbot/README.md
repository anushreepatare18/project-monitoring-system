# PRAGYA AI — Natural Language Risk Query Assistant

Retrieval-grounded chatbot for government monitoring officers. Answers questions about project risk **strictly from stored XAI outputs** — never from free-form LLM generation.

---

## Why Retrieval-Grounded, Not Free-Form LLM?

Government dashboards require **extreme auditability**. If an LLM independently guesses why a project is delayed or invents a risk score, it:

1. Breaks officer trust when it contradicts the dashboard
2. Is legally indefensible in a government context
3. Cannot be audited or traced

Our architecture solves this by treating the chatbot as a **structured query interface**, not a conversational agent:

```
Officer question
      │
      ▼
┌─────────────────────────────────────────┐
│  Step 1: INTENT PARSING                 │
│  Rules-first regex + entity resolution  │
│  → structured query dict                │
│  (sector, risk_band, project_id, etc.)  │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  Step 2: GROUNDED RETRIEVAL             │
│  Execute dict against results_store     │
│  (Pandas DataFrame / SQL query)         │
│  → real rows from pre-computed scores   │
│  RBAC scope enforced here               │
│  Exact query logged for audit           │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  Step 3: ANSWER COMPOSITION             │
│  For EXPLAIN: passthrough top_reasons   │
│    (same text dashboard shows — no LLM) │
│  For FILTER/COMPARE/AGGREGATE:          │
│    format retrieved rows verbatim       │
│  All numeric claims = verbatim retrieval│
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  Step 4: AUDIT LOG                      │
│  question + parsed_query + query_run    │
│  + retrieved_count + answer             │
│  → append-only JSONL                    │
└─────────────────────────────────────────┘
```

### Explanation Passthrough

When an officer asks *"Why is P-ROADS-0457 flagged?"*, we:
1. Fetch the stored `top_reasons` from `results_store.get_project_record()`
2. Format them directly as the answer — **no LLM call, no regeneration**

This guarantees the chatbot answer is **provably identical** to what the dashboard already shows for that project.

---

## Files

```
chatbot/
├── intent_parser.py   — question → structured query dict
├── retriever.py       — structured query → real data rows (RBAC-enforced)
├── answer_composer.py — grounded answer formatting (explanation passthrough)
├── api.py             — FastAPI: POST /chatbot/ask
├── results_store.py   — mock results store (pre-computed risk scores/SHAP)
├── tests/
│   └── test_chatbot.py   — 15 test cases
└── README.md
```

---

## Running the API

```bash
# From repo root:
uvicorn chatbot.api:app --reload --port 8000
```

### Test a question

```bash
curl -X POST http://localhost:8000/chatbot/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question":   "Which projects in the Roads sector are high risk?",
    "officer_id": "OFF-001",
    "scope":      "ALL"
  }'
```

**Response:**
```json
{
  "answer_text": "Found **12** project(s) matching your criteria...",
  "referenced_projects": ["PRJ-123456", "PRJ-654321"],
  "clarifying_question": null,
  "as_of_date": "2026-10-01",
  "disclaimer": "Answers are generated from stored risk data...",
  "query_run": "query_store(sector='Roads', risk_band='High', limit=15)"
}
```

---

## RBAC Scope

The `scope` field in every request is a ministry name (e.g. `"MoRTH"`) or `"ALL"`.

- The retriever enforces this scope as the **first filter** before any other query logic.
- An officer scoped to `MoRTH` cannot see `MoH` projects through the chatbot even if they know the project ID.
- The scope comes from the officer's login session — the chatbot API trusts the scope passed by the frontend.

---

## Running Tests

```bash
pytest chatbot/tests/test_chatbot.py -v
```

Test coverage:
1. High-risk sector filter → returns list + referenced_projects
2. Explain specific project → top_reasons passthrough
3. Compare two projects → table format
4. Zero-results scenario → plain "No projects found" message
5. Out-of-scope: contractor names → "I don't have that information"
6. Out-of-scope: legal status → clarifying question
7. RBAC boundary: MoRTH officer asking for MoH project → "not found/outside scope"
8. Aggregate: which sector has most cost overruns
9. Milestone delay filter (> 3 months)
10. Anomaly-flagged project filter
11. Ambiguous question → single clarifying question
12. Unknown project ID → "not found" (not fabricated data)
13. Disclaimer present in every response
14. Numeric claims match stored values (not invented)
15. Health endpoint

---

## "Cannot Answer" Cases

| Question type | Response |
|---|---|
| Contractor / vendor names | "I don't have access to that information. I can only answer questions about project risk scores, milestone delays, cost growth, anomaly flags, and SHAP-based explanations." |
| Legal / court status | Same as above |
| GST / tax records | Same |
| Unknown project ID | "Project 'XYZ' was not found in your authorised scope." |
| Unknown sector name | Clarifying question: "Could you tell me which sector you're interested in?" |
| Zero matching results | "No projects match the specified criteria in your authorised scope." |

---

## Audit Log

Every interaction is appended to `backend/chatbot_audit.jsonl`:

```json
{
  "ts":                  "2026-10-04T11:00:00Z",
  "officer_id":          "OFF-001",
  "scope":               "MoRTH",
  "role":                "officer",
  "question":            "Which Roads projects are high risk?",
  "parsed_query":        { "intent": "FILTER_PROJECTS", "sector": "Roads", "risk_band": "High" },
  "query_run":           "query_store(sector='Roads', risk_band='High', limit=15)",
  "retrieved_type":      "filtered_list",
  "retrieved_count":     12,
  "referenced_projects": ["PRJ-123456", "PRJ-654321"],
  "answer_preview":      "Found **12** project(s) matching your criteria..."
}
```

The audit log is append-only. Officers and compliance teams can reconstruct exactly what data drove each answer.
