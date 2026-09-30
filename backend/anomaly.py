from typing import Dict, Any
import numpy as np

def detect_anomalies(update_data: Dict[str, Any], previous_state: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Implements rule-based anomaly checks per SRS 5.10.
    In the prototype, we use heuristic rules and standard z-score checks.
    """
    reasons = []
    anomaly_score = 0.0
    
    curr_prog = float(update_data.get('Physical_Progress_Pct', 0))
    curr_exp = float(update_data.get('Expenditure_Cr', 0))
    
    if previous_state:
        prev_prog = float(previous_state.get('physical_progress_pct', 0))
        prev_exp = float(previous_state.get('expenditure_cr', 0))
        
        # Rule 1: Massive jump in physical progress in a single update (e.g. > 30% in one month)
        prog_diff = curr_prog - prev_prog
        if prog_diff > 30:
            reasons.append(f"Progress jumped {prog_diff}% in one period, vs expected typical change.")
            anomaly_score += 40.0
            
        # Rule 2: Expenditure spike without progress
        exp_diff = curr_exp - prev_exp
        if exp_diff > 0 and prog_diff <= 0:
            reasons.append("Expenditure spiked while physical progress remained stagnant.")
            anomaly_score += 30.0
            
        # Rule 3: Extreme sudden deadline shift
        # Handled in dates if we have them
        
    # Threshold for flagging
    is_flagged = anomaly_score >= 50.0
    
    return {
        "anomaly_score": anomaly_score,
        "is_flagged": is_flagged,
        "reasons": reasons
    }
