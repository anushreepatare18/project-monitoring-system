import sys, warnings
warnings.filterwarnings('ignore')
sys.path.insert(0, '.')

import pandas as pd
from datetime import datetime, timedelta

as_of = datetime.now().strftime('%Y-%m-%d')
update_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

# Test 1: normal project
df = pd.DataFrame([{
    'project_id': 'PRJ-001',
    'update_date': update_date,
    'ministry': 'Ministry of Road Transport',
    'sector': 'Roads',
    'agency': 'NHAI',
    'state': 'Maharashtra',
    'sanctioned_cost': 500.0,
    'planned_start': '2020-01-01',
    'planned_end': '2027-12-31',
    'project_type': 'Infrastructure',
    'physical_progress_pct': 60.0,
    'financial_progress_pct': 55.0,
    'cumulative_expenditure': 300.0,
    'revised_cost': 550.0,
    'expected_completion_date': '2027-12-31',
    'milestone_name': 'Milestone 1',
    'milestone_planned_date': '2022-06-01',
    'milestone_expected_date': '2023-01-01',
    'milestone_actual_date': None
}])

from backend.ml_core.inference.infer import run_inference
res = run_inference('PRJ-001', as_of, df)

raw_shap = res.get('shap_explanation', [])
valid_shap = [s for s in raw_shap if isinstance(s, dict) and 'feature' in s and 'impact' in s]

print('=== RESULTS ===')
print('Risk score:', round(res.get('composite_risk_score', 0) * 100, 2))
print('Risk band:', res.get('risk_band'))
print('SHAP features count:', len(valid_shap))
print()
for s in valid_shap:
    feat = s['feature']
    imp = s['impact']
    exp = s.get('explanation', '')[:70]
    print(f"  {feat:<35}  impact={imp:+.4f}  {exp}")
