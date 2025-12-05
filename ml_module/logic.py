import numpy as np
from sklearn.ensemble import IsolationForest

class AnomalyDetector:
    """
    Advanced Isolation Forest Model with Tuned Confidence.
    """
    def __init__(self):
        # contamination=0.1 means we expect ~10% anomalies
        self.models = {
            'temperature': IsolationForest(contamination=0.1, random_state=42),
            'humidity': IsolationForest(contamination=0.1, random_state=42),
            'moisture': IsolationForest(contamination=0.1, random_state=42)
        }
        self._train_models()

    def _train_models(self):
        """
        Pre-trains with TIGHTER 'Normal' data ranges.
        This makes the model more confident that deviations are anomalies.
        """
        print("🧠 Training Stricter Isolation Forest Models...")
        
        # 1. Normal Temperature (Stricter: mostly 20-30°C)
        # scale=2 means standard deviation is 2. 
        X_temp = np.random.normal(loc=25, scale=2, size=(1000, 1)) 
        self.models['temperature'].fit(X_temp)

        # 2. Normal Humidity (Stricter: mostly 50-70%)
        X_hum = np.random.normal(loc=60, scale=5, size=(1000, 1))
        self.models['humidity'].fit(X_hum)

        # 3. Normal Moisture (Stricter: mostly 45-65%)
        X_moist = np.random.normal(loc=55, scale=5, size=(1000, 1))
        self.models['moisture'].fit(X_moist)
        
        print("✅ Models Trained.")

    def check_anomaly(self, sensor_type, value):
        """
        Returns: (is_anomaly, reason, confidence_score)
        """
        model = self.models.get(sensor_type)
        if not model: return False, "Unknown", 0.0

        # --- LAYER 1: ISOLATION FOREST ---
        data_point = np.array([[value]])
        prediction = model.predict(data_point)[0] # -1 is Anomaly
        score = model.decision_function(data_point)[0]
        
        # TUNED CONFIDENCE FORMULA
        # We multiply the raw score by 3 to boost the confidence.
        # If score is -0.1 (weak anomaly) -> 0.5 + 0.3 = 0.80
        # If score is -0.2 (strong anomaly) -> 0.5 + 0.6 = 1.0 -> capped at 0.99
        ai_confidence = min(0.99, 0.5 + (abs(score) * 3))
        
        # --- LAYER 2: SAFETY THRESHOLDS ---
        force_anomaly = False
        reason = "Normal"

        if sensor_type == 'temperature':
            if value > 35: 
                force_anomaly = True
                reason = "Heat Stress"
            elif value < 5:
                force_anomaly = True
                reason = "Frost Danger"
        
        elif sensor_type == 'moisture':
            if value < 30:
                force_anomaly = True
                reason = "Drought / Pump Failure"
            elif value > 90:
                force_anomaly = True
                reason = "Waterlogging"

        elif sensor_type == 'humidity':
            if value < 20:
                force_anomaly = True
                reason = "Extremely Dry Air"
            elif value > 90:
                force_anomaly = True
                reason = "High Humidity"

        # --- FINAL DECISION ---
        if prediction == -1 or force_anomaly:
            
            # If the threshold forced it, ensure high confidence
            if force_anomaly and ai_confidence < 0.8:
                ai_confidence = 0.95
            
            # If AI caught it but threshold didn't (rare but possible)
            if prediction == -1 and not force_anomaly:
                reason = f"Abnormal {sensor_type} pattern"

            return True, reason, float(f"{ai_confidence:.2f}")

        return False, "Normal", 0.0