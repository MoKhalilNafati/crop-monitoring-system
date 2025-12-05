import random
import numpy as np
from sklearn.metrics import precision_score, recall_score, f1_score, confusion_matrix, accuracy_score
# Import your actual ML logic to test the real system
from ml_module.logic import AnomalyDetector

def generate_test_dataset(n_samples=1000):
    """
    Generates synthetic data with KNOWN labels (Ground Truth).
    0 = Normal
    1 = Anomaly
    """
    X_test = [] 
    y_true = [] 
    
    print(f"🧪 Generating {n_samples} test samples...")

    for _ in range(n_samples):
        # 85% Normal Data (Gaussian Distribution matched to your training)
        if random.random() > 0.15:
            # Normal temp is around 25, with small variance
            val = random.normalvariate(25, 2) 
            X_test.append({'type': 'temperature', 'value': val})
            y_true.append(0) # Label: Normal
        else:
            # 15% Anomalies (Extreme Values)
            # We force values outside the trained "Normal" range
            if random.random() > 0.5:
                val = random.uniform(40, 60) # Heat wave
            else:
                val = random.uniform(-10, 5) # Frost / Cold
            
            X_test.append({'type': 'temperature', 'value': val})
            y_true.append(1) # Label: Anomaly
        
    return X_test, y_true

def run_evaluation():
    print("--------------------------------------------------")
    print("🚀 STARTING MODEL EVALUATION")
    print("--------------------------------------------------")

    # 1. Initialize Model (This runs the training logic)
    detector = AnomalyDetector()
    
    # 2. Get Test Data
    X_test, y_true = generate_test_dataset()
    y_pred = [] 

    # 3. Run Predictions
    print("🔍 Running inference on test set...")
    for reading in X_test:
        # We call your actual logic function
        # It returns: (is_anomaly, reason, score)
        is_anomaly, reason, score = detector.check_anomaly(reading['type'], reading['value'])
        
        # Convert True -> 1, False -> 0
        y_pred.append(1 if is_anomaly else 0)

    # 4. Calculate Metrics
    precision = precision_score(y_true, y_pred)
    recall = recall_score(y_true, y_pred)
    f1 = f1_score(y_true, y_pred)
    acc = accuracy_score(y_true, y_pred)
    cm = confusion_matrix(y_true, y_pred)

    # 5. Print Final Report
    print("\n" + "="*40)
    print("📊  FINAL EVALUATION REPORT")
    print("="*40)
    print(f"Model: Hybrid (Isolation Forest + Threshold)")
    print("-" * 40)
    print(f"✅ Accuracy:   {acc*100:.2f}%")
    print(f"🎯 Precision:  {precision:.2f}  (Trustworthiness)")
    print(f"🔎 Recall:     {recall:.2f}     (Sensitivity)")
    print(f"⚖️  F1-Score:   {f1:.2f}      (Overall Score)")
    print("-" * 40)
    print("Confusion Matrix:")
    print(f" [ {cm[0][0]} (TN)   {cm[0][1]} (FP) ]")
    print(f" [ {cm[1][0]} (FN)   {cm[1][1]} (TP) ]")
    print("="*40 + "\n")

if __name__ == "__main__":
    run_evaluation()