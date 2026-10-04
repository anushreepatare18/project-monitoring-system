import json
import re

# Mocking an LLM call for the purpose of the prototype.
# In a real environment, this would call a model like Gemini/GPT with a strict schema prompt.

def parse_intent(question: str) -> dict:
    """
    Parses a natural language question into a structured query dictionary.
    """
    question = question.lower()
    
    # 1. Check for "why flagged" or explain specific project
    if "why" in question and ("flagged" in question or "risk" in question):
        match = re.search(r'p-[a-z]+-\d+|prj-\d+', question)
        if match:
            return {
                "intent": "EXPLAIN_PROJECT",
                "project_id": match.group(0).upper()
            }
            
    # 2. Check for comparison
    if "compare" in question:
        matches = re.findall(r'p-[a-z]+-\d+|prj-\d+', question)
        if len(matches) >= 2:
            return {
                "intent": "COMPARE_PROJECTS",
                "project_ids": [m.upper() for m in matches]
            }
            
    # 3. Aggregation/Filtering
    query = {
        "intent": "FILTER_PROJECTS",
        "filters": {}
    }
    
    # Simple rule-based extraction for prototype (normally LLM handles this)
    if "high risk" in question:
        query["filters"]["risk_band"] = "High"
    if "critical risk" in question:
        query["filters"]["risk_band"] = "Critical"
    
    # Extract sector
    sectors = ["roads", "railways", "power", "health", "education", "sector_1", "sector_2"]
    for s in sectors:
        if s in question:
            # Capitalize properly based on known sectors if needed, or leave lower
            query["filters"]["sector"] = s.capitalize() if s.startswith("sector") else s
            break
            
    if "most cost overruns" in question:
        return {
            "intent": "AGGREGATE",
            "metric": "cost_overruns",
            "group_by": "sector",
            "sort": "desc"
        }
        
    if "milestone delays over" in question:
        match = re.search(r'(\d+)\s*months', question)
        if match:
            query["filters"]["min_milestone_delay_months"] = int(match.group(1))
            
    # Ambiguous or unknown
    if "contractor" in question or "legal" in question:
        return {
            "intent": "UNKNOWN_DOMAIN",
            "clarifying_question": "I don't have access to contractor names or legal status. I can only answer questions about project progress, risk scores, costs, and delays. How else can I help?"
        }
        
    if query["filters"] == {}:
        return {
            "intent": "AMBIGUOUS",
            "clarifying_question": "Could you please specify which sector, risk band, or project ID you are interested in?"
        }
        
    return query
