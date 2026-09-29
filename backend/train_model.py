import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.metrics import classification_report, roc_auc_score
import shap
import pickle

# Load dataset
df = pd.read_csv('project_data.csv')

# Feature Engineering
# Using Ministry, State, Original Cost, Expenditure, Progress, Delay Months, Cost Overrun Pct
le_min = LabelEncoder()
df['Ministry_Encoded'] = le_min.fit_transform(df['Ministry'])

le_state = LabelEncoder()
df['State_Encoded'] = le_state.fit_transform(df['State'])

features = ['Ministry_Encoded', 'State_Encoded', 'Original_Cost_Cr', 'Expenditure_Cr', 'Physical_Progress_Pct', 'Delay_Months', 'Cost_Overrun_Pct']
X = df[features]
y = df['Is_High_Risk']

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train XGBoost Model
print("Training XGBoost Model...")
model = XGBClassifier(eval_metric='logloss', random_state=42)
model.fit(X_train, y_train)

# Evaluate
y_pred = model.predict(X_test)
print("Classification Report:")
print(classification_report(y_test, y_pred))

# Save models and encoders
with open('pragya_model.pkl', 'wb') as f:
    pickle.dump(model, f)
with open('le_min.pkl', 'wb') as f:
    pickle.dump(le_min, f)
with open('le_state.pkl', 'wb') as f:
    pickle.dump(le_state, f)

# Generate SHAP explainer
print("Generating SHAP Explainer...")
explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(X_test)

with open('shap_explainer.pkl', 'wb') as f:
    pickle.dump(explainer, f)

print("Model training complete and saved.")
