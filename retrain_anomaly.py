import pandas as pd
from backend.ml_core.anomaly.detector import AnomalyDetector

def retrain():
    print("Retraining anomaly detector as a module...")
    df = pd.read_csv("dataset.csv")
    detector = AnomalyDetector()
    detector.fit(df)
    print("Done")

if __name__ == "__main__":
    retrain()
