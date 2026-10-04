from ml_core.data.generator import generate_synthetic_data
from ml_core.training.train import train_and_evaluate
from ml_core.anomaly.detector import train_anomaly_detector
import os

def run_all():
    print("1. Generating Data...")
    generate_synthetic_data()
    
    print("2. Training Anomaly Detector...")
    train_anomaly_detector()
    
    print("3. Training & Evaluating Models...")
    train_and_evaluate("overrun_flag")
    train_and_evaluate("delayed_flag")
    
    print("\nPipeline Complete. Models saved in ml_core/registry/")
    
if __name__ == "__main__":
    run_all()
