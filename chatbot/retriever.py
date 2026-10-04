import pandas as pd
import sys
import os

# Ensure we can import from ml_core
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from ml_core.inference.predict import explain_risk

def fetch_data():
    path = "ml_core/data/synthetic_projects.csv"
    if not os.path.exists(path):
        return pd.DataFrame()
    df = pd.read_csv(path)
    # Return only the latest snapshot for simplicity
    df['update_date'] = pd.to_datetime(df['update_date'])
    return df.sort_values(by=['project_id', 'update_date']).groupby('project_id').tail(1)

def retrieve_grounded_data(parsed_query: dict, scope: str = None) -> dict:
    """
    Executes the structured query against the data store.
    Enforces RBAC scope.
    """
    df = fetch_data()
    if df.empty:
        return {"error": "Data store unavailable."}
        
    # Enforce scope
    if scope and scope != "ALL":
        df = df[df['ministry'] == scope]
        
    intent = parsed_query.get("intent")
    
    if intent == "EXPLAIN_PROJECT":
        pid = parsed_query["project_id"]
        if pid not in df['project_id'].values:
            return {"error": f"Project {pid} not found or outside your authorized scope."}
        
        # We need the full history for explain_risk, so read it fresh
        full_df = pd.read_csv("ml_core/data/synthetic_projects.csv")
        try:
            explanation = explain_risk(pid, "2030-01-01", full_df)
            return {
                "type": "explanation",
                "project_id": pid,
                "data": explanation
            }
        except Exception as e:
            return {"error": str(e)}
            
    elif intent == "COMPARE_PROJECTS":
        pids = parsed_query["project_ids"]
        mask = df['project_id'].isin(pids)
        filtered = df[mask]
        
        if filtered.empty:
            return {"error": "None of the requested projects were found in your scope."}
            
        data = filtered[['project_id', 'sector', 'physical_progress_pct', 'sanctioned_cost', 'expected_completion_date']].to_dict(orient="records")
        return {
            "type": "comparison",
            "data": data
        }
        
    elif intent == "FILTER_PROJECTS":
        filters = parsed_query.get("filters", {})
        filtered = df.copy()
        
        # Apply mock risk band (for prototype without running inference on everything)
        # Normally, we'd query a materialized view of risk scores
        if "risk_band" in filters:
            # We mock filtering based on overrun/delay flags since we don't have precomputed scores for all rows
            if filters["risk_band"] == "High" or filters["risk_band"] == "Critical":
                filtered = filtered[(filtered['overrun_flag'] == 1) | (filtered['delayed_flag'] == 1)]
                
        if "sector" in filters:
            s = filters["sector"].lower()
            filtered = filtered[filtered['sector'].str.lower() == s]
            
        if "min_milestone_delay_months" in filters:
            # Mock calculation
            filtered['delay_months'] = (pd.to_datetime(filtered['expected_completion_date']) - pd.to_datetime(filtered['planned_end'])).dt.days / 30.0
            filtered = filtered[filtered['delay_months'] > filters["min_milestone_delay_months"]]
            
        if filtered.empty:
            return {"type": "filtered_list", "data": [], "message": "No projects match the criteria."}
            
        results = filtered[['project_id', 'sector', 'ministry']].head(10).to_dict(orient="records")
        return {
            "type": "filtered_list",
            "data": results,
            "count": len(filtered)
        }
        
    elif intent == "AGGREGATE":
        if parsed_query.get("metric") == "cost_overruns":
            grouped = df[df['overrun_flag'] == 1].groupby('sector').size().reset_index(name='overruns')
            grouped = grouped.sort_values(by='overruns', ascending=False)
            return {
                "type": "aggregation",
                "data": grouped.to_dict(orient="records")
            }
            
    return {"error": "Unhandled intent."}
