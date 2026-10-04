import json

def compose_answer(retrieved_data: dict, original_question: str) -> dict:
    """
    Composes a natural language answer grounded entirely in retrieved_data.
    Normally calls an LLM with strict constraints. Here, we mock the composition.
    """
    if "error" in retrieved_data:
        return {
            "answer_text": retrieved_data["error"],
            "referenced_projects": []
        }
        
    data_type = retrieved_data.get("type")
    
    if data_type == "explanation":
        data = retrieved_data["data"]
        pid = retrieved_data["project_id"]
        
        # EXPLANATION PASSTHROUGH
        reasons_text = "\n- ".join(data["top_reasons"])
        answer = f"Project {pid} is classified as {data['risk_band']} Risk (Probability: {data['risk_probability']:.2f}).\n\nThe top reasons flagged by the model are:\n- {reasons_text}"
        
        if data.get("anomaly_reasons"):
            answer += f"\n\nAdditionally, an anomaly was detected: {data['anomaly_reasons']}"
            
        return {
            "answer_text": answer,
            "referenced_projects": [pid],
            "shap_chart": data.get("shap_chart")
        }
        
    elif data_type == "comparison":
        data = retrieved_data["data"]
        pids = [p['project_id'] for p in data]
        
        if len(data) == 2:
            p1, p2 = data[0], data[1]
            answer = f"Comparing {p1['project_id']} and {p2['project_id']}:\n"
            answer += f"- Sector: {p1['sector']} vs {p2['sector']}\n"
            answer += f"- Physical Progress: {p1['physical_progress_pct']}% vs {p2['physical_progress_pct']}%\n"
            answer += f"- Sanctioned Cost: ₹{p1['sanctioned_cost']} Cr vs ₹{p2['sanctioned_cost']} Cr"
        else:
            answer = f"Comparison data retrieved for {len(data)} projects."
            
        return {
            "answer_text": answer,
            "referenced_projects": pids
        }
        
    elif data_type == "filtered_list":
        data = retrieved_data.get("data", [])
        if not data:
            return {
                "answer_text": retrieved_data.get("message", "No projects found."),
                "referenced_projects": []
            }
            
        pids = [p['project_id'] for p in data]
        count = retrieved_data.get("count", len(data))
        
        answer = f"I found {count} projects matching your criteria. Here are the top {len(data)}:\n"
        answer += ", ".join(pids)
        
        return {
            "answer_text": answer,
            "referenced_projects": pids
        }
        
    elif data_type == "aggregation":
        data = retrieved_data["data"]
        if not data:
            return {"answer_text": "No data found.", "referenced_projects": []}
            
        top_sector = data[0]
        answer = f"The {top_sector['sector']} sector currently has the most cost overruns, with a total of {top_sector['overruns']} flagged projects."
        
        return {
            "answer_text": answer,
            "referenced_projects": []
        }
        
    return {
        "answer_text": "I could not formulate an answer based on the retrieved data.",
        "referenced_projects": []
    }
