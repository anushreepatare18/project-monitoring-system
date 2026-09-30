from datetime import datetime
from typing import Dict, List, Any

def validate_project_update(update_data: Dict[str, Any], previous_state: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Validates a project update according to PRAGYA AI SRS Section 5.2.
    Returns a dictionary with 'is_valid', 'hard_errors', and 'soft_warnings'.
    """
    hard_errors = []
    soft_warnings = []
    
    # 1. Hard Errors
    mandatory_fields = ['Original_Cost_Cr', 'Physical_Progress_Pct']
    for field in mandatory_fields:
        if field not in update_data or update_data[field] is None:
            hard_errors.append({"field": field, "message": f"Mandatory field {field} is missing."})
            
    # Numeric checks
    try:
        cost = float(update_data.get('Original_Cost_Cr', 0))
        if cost < 0:
            hard_errors.append({"field": "Original_Cost_Cr", "message": "Cost cannot be negative."})
    except (ValueError, TypeError):
        hard_errors.append({"field": "Original_Cost_Cr", "message": "Cost must be numeric."})
        
    try:
        expenditure = float(update_data.get('Expenditure_Cr', 0))
        if expenditure < 0:
            hard_errors.append({"field": "Expenditure_Cr", "message": "Expenditure cannot be negative."})
    except (ValueError, TypeError):
        hard_errors.append({"field": "Expenditure_Cr", "message": "Expenditure must be numeric."})
        
    try:
        progress = float(update_data.get('Physical_Progress_Pct', 0))
        if progress < 0 or progress > 100:
            hard_errors.append({"field": "Physical_Progress_Pct", "message": "Progress must be between 0 and 100."})
    except (ValueError, TypeError):
        hard_errors.append({"field": "Physical_Progress_Pct", "message": "Progress must be numeric."})
        
    # Date logic checks (if actual_start and actual_end are provided)
    # Mocking date parsing for prototype, assuming ISO format
    start = update_data.get('actual_start')
    end = update_data.get('actual_end')
    if start and end:
        try:
            start_dt = datetime.fromisoformat(start)
            end_dt = datetime.fromisoformat(end)
            if end_dt < start_dt:
                hard_errors.append({"field": "actual_end", "message": "Actual end cannot be before actual start."})
        except Exception:
            pass # Unparsable handled gracefully or in another check
            
    # 2. Soft Warnings (if previous state exists)
    if previous_state:
        prev_prog = float(previous_state.get('physical_progress_pct', 0))
        curr_prog = float(update_data.get('Physical_Progress_Pct', 0))
        if curr_prog < prev_prog:
            soft_warnings.append({"field": "Physical_Progress_Pct", "message": "Progress is decreasing versus last update."})
            
        revised_cost = float(previous_state.get('revised_cost') or previous_state.get('original_cost_cr', 0))
        if expenditure > revised_cost and revised_cost > 0:
            soft_warnings.append({"field": "Expenditure_Cr", "message": "Expenditure is higher than revised cost."})
            
    return {
        "is_valid": len(hard_errors) == 0,
        "hard_errors": hard_errors,
        "soft_warnings": soft_warnings
    }
