# PRAGYA AI - Natural Language Query Assistant

This module provides a Retrieval-Grounded Chatbot designed specifically for government monitoring officers. It strictly avoids free-form LLM hallucination by architecting the chat as a structured Retrieval-Augmented Generation (RAG) loop against the *existing* predictive ML outputs.

## Why Grounded Retrieval instead of Free-Form Generation?
Government dashboards require extreme auditability. If an LLM independently guesses why a project is delayed or hallucinates a risk score, it breaks trust. 
Instead, our architecture:
1. **Parses Intents**: The LLM (or rules engine) maps the user's natural language to strict SQL/Dataframe filters (e.g., `sector="roads", risk_band="High"`).
2. **Retrieves Hard Data**: We query the existing `ml_core` outputs and `dataset.csv`.
3. **Explanation Passthrough**: When explaining a specific project, we completely bypass generation and directly format the top 5 SHAP values outputted by `explain_risk()`.
4. **Composes Answer**: The LLM is provided *only* the retrieved rows and given a strict prompt to summarize them without adding outside facts.

## Components
- `intent_parser.py`: Maps questions to a structured query dictionary. Resolves ambiguity.
- `retriever.py`: Executes the dictionary against the data, enforcing RBAC scope boundaries.
- `answer_composer.py`: Formats the retrieved rows into the final officer-facing string.
- `api.py`: FastAPI endpoint exposing `POST /chatbot/ask`.
- `tests/test_chatbot.py`: Validation suite for edge cases, permission bounds, and unsupported domains.

## Running the API
```bash
uvicorn chatbot.api:app --reload
```
