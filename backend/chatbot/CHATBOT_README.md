# PRAGYA AI — Grounded Chatbot (Risk Intelligence Assistant)

## Why Free-Form Generation Was Avoided

Government officers acting on AI outputs need **auditability** and **verifiability**. A free-form LLM can:
- Confabulate project IDs, risk scores, or delay figures
- Blend data from different projects into plausible-sounding but wrong composites
- Give different answers to the same question on consecutive calls

The PRAGYA chatbot eliminates these risks through a **retrieval-grounded pipeline** where the LLM is used _only_ for two narrow tasks — never to supply facts.

---

## Architecture

```
Officer Question
      │
      ▼
┌─────────────────────────────────────────────────────────────────┐
│  1. INTENT PARSING (intent_parser.py)                           │
│     Rules precheck → LLM extracts structured fields ONLY        │
│     Output: { intent, sector, risk_band, project_ids, ... }     │
│     LLM cannot invent facts — it only fills in field names      │
└─────────────────────────┬───────────────────────────────────────┘
                          │  structured query dict
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│  2. GROUNDED RETRIEVAL (retriever.py)                           │
│     Deterministic query against the real results store          │
│     • SQL / dataframe filter on actual rows                     │
│     • RBAC scope enforced (ministry/agency officers can't       │
│       query outside their permission boundary)                  │
│     • explain_risk() called for "why flagged" queries           │
│       → returns verbatim SHAP reasons from the pipeline         │
│     • Every query is logged for audit (query_log field)         │
│     Output: { rows, query_log, as_of_date, total_matched }      │
└─────────────────────────┬───────────────────────────────────────┘
                          │  retrieved rows (real data)
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│  3. ANSWER COMPOSITION (answer_composer.py)                     │
│     • explain_project intent: NO LLM — SHAP reasons formatted   │
│       directly → answer is identical to what the dashboard shows│
│     • All other intents: LLM receives ONLY the retrieved rows   │
│       with a strict prompt:                                      │
│       "Do not add numbers, projects, or reasons not in this     │
│        data. If the data doesn't answer the question, say so."  │
│     • Zero rows → plain "no results" message, no guessing       │
│     Grounding methods: direct_shap | llm_grounded | no_llm |   │
│       zero_results | cannot_answer | clarification              │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│  4. AUDIT LOG (audit_logger.py)                                 │
│     Every interaction logged: question, parsed_query,           │
│     db_query_log, rows_retrieved, referenced_projects,          │
│     grounding_method, answer_text                               │
│     → JSONL file + SQLAlchemy AuditLog table                    │
└─────────────────────────────────────────────────────────────────┘
```

---

## File Map

| File | Role |
|------|------|
| `backend/chatbot/intent_parser.py` | Question → structured query (LLM for field extraction only) |
| `backend/chatbot/retriever.py` | Structured query → real data rows (RBAC-scoped, deterministic) |
| `backend/chatbot/answer_composer.py` | Retrieved rows → grounded natural-language answer |
| `backend/chatbot/audit_logger.py` | Logs every interaction for compliance |
| `backend/chatbot/api.py` | FastAPI router: `POST /chatbot/ask` |
| `backend/chatbot/tests/test_chatbot_pipeline.py` | 10 test cases covering all scenarios |
| `src/components/ui/AssistantChat.tsx` | React chat panel (floating + fullscreen) |
| `src/app/dashboard/officer/assistant/page.tsx` | Full-screen Risk Assistant page (officer) |
| `src/app/dashboard/ministry/assistant/page.tsx` | Full-screen Risk Assistant page (ministry) |
| `src/app/dashboard/agency/assistant/page.tsx` | Full-screen Risk Assistant page (agency) |

---

## API

### `POST /chatbot/ask`

**Request:**
```json
{
  "question": "Which projects in the roads sector are high risk?",
  "officer_id": "officer@pragya.gov.in",
  "role": "officer",
  "scope": {}
}
```

**Response:**
```json
{
  "answer_text": "There are 2 high-risk projects in the Roads sector...",
  "referenced_projects": ["P-ROADS-0457", "P-ROADS-0891"],
  "clarifying_question": null,
  "as_of_date": "2026-09-01",
  "grounding_method": "llm_grounded",
  "query_log": "intent=list_projects | role=officer | sector=Roads | risk_level=High | order_by=risk_score DESC | limit=10"
}
```

**`grounding_method` values:**

| Value | Meaning |
|-------|---------|
| `direct_shap` | SHAP reasons returned verbatim from the pipeline — no LLM |
| `llm_grounded` | LLM composed answer from retrieved rows only |
| `no_llm` | Raw tabular fallback (LLM unavailable) |
| `zero_results` | No rows matched — answer says so plainly |
| `cannot_answer` | Question is out of scope (contractor names, legal, etc.) |
| `clarification` | Question is ambiguous — one clarifying question returned |
| `permission_denied` | Role doesn't have chatbot access |

---

## Running the Tests

```bash
# From project root
cd c:\Users\RAMESH PATARE\OneDrive\Desktop\SIH\SIH26103
python -m pytest backend/chatbot/tests/test_chatbot_pipeline.py -v
```

All 10 test classes pass without a live LLM (SHAP pass-through and zero-results paths don't need the API key). LLM-backed paths fall back to formatted raw data if `GEMINI_API_KEY` is not set.

---

## RBAC Scope

| Role | Access |
|------|--------|
| `officer` | Full portfolio access |
| `ministry` | Only projects under `scope.ministry` |
| `agency` | Only projects assigned to `scope.agency` |
| `public` | No chatbot access — blocked at API layer |

Officers cannot bypass this by asking about other ministries through the chat — the retriever's `_apply_scope()` filters before any data is returned.

---

## "Cannot Answer" Cases

The system returns a `cannot_answer` response (never fabricates) for:
- Contractor names, vendor details
- Legal status, court cases
- Employee salaries, contact info
- RTI, tender documents
- Anything not in the risk/financial/milestone data schema

These are caught by `_rules_precheck()` in `intent_parser.py` before any LLM call.

---

## Audit Trail

Every interaction appended to `backend/chatbot_audit.jsonl`:
```json
{
  "timestamp": "2026-09-29T07:13:22Z",
  "officer_id": "officer@pragya.gov.in",
  "role": "officer",
  "question": "Why is P-ROADS-0457 flagged?",
  "parsed_query": { "intent": "explain_project", "project_ids": ["P-ROADS-0457"] },
  "db_query_log": "intent=explain_project | role=officer | project_id=P-ROADS-0457",
  "rows_retrieved": 1,
  "referenced_projects": ["P-ROADS-0457"],
  "grounding_method": "direct_shap",
  "as_of_date": "2026-09-01",
  "answer_text": "NH-48 Bangalore-Chennai Expressway Phase 2 (P-ROADS-0457) has a risk score of 82.4/100..."
}
```
