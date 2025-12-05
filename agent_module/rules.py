import re

class RuleEngine:
    """
    Deterministic rule-based engine for agricultural recommendations.
    """
    
    def analyze(self, anomaly_event):
        # Normalize inputs
        anomaly_type = anomaly_event.anomaly_type.lower()
        
        # 1. Safely extract value
        try:
            match = re.search(r"[-+]?\d*\.\d+|\d+", anomaly_event.description)
            sensor_val = float(match.group()) if match else 0
        except:
            sensor_val = 0

        # 2. Get Confidence
        current_conf = anomaly_event.model_confidence if anomaly_event.model_confidence else 0.8

        # Default response
        recommendation = {
            "action": "Investigate manually.",
            "explanation": f"Unknown anomaly type: {anomaly_type}",
            "confidence": 0.5
        }

        # --- SMART LOGIC ---
        
        # RULE 1: MOISTURE ISSUES
        # Handles "drought", "failure", or generic "abnormal moisture"
        if "moisture" in anomaly_type or "drought" in anomaly_type or "waterlogging" in anomaly_type:
            if sensor_val < 30:
                recommendation = {
                    "action": "Check irrigation pump and increase water flow.",
                    "explanation": f"Soil moisture is critically low ({sensor_val}%). Potential pump failure.",
                    "confidence": current_conf
                }
            elif sensor_val > 80:
                recommendation = {
                    "action": "Stop irrigation and check drainage.",
                    "explanation": f"Soil moisture is abnormally high ({sensor_val}%). Risk of root rot.",
                    "confidence": current_conf
                }

        # RULE 2: TEMPERATURE ISSUES
        # Handles "heat", "frost", or generic "abnormal temperature"
        elif "temp" in anomaly_type or "heat" in anomaly_type or "frost" in anomaly_type or "cold" in anomaly_type:
            if sensor_val > 30:
                recommendation = {
                    "action": "Activate misting system or install shade nets.",
                    "explanation": f"Temperature is high ({sensor_val}°C). Risk of heat stress.",
                    "confidence": current_conf
                }
            else:
                recommendation = {
                    "action": "Deploy frost covers or heaters.",
                    "explanation": f"Temperature is low ({sensor_val}°C). Frost damage risk.",
                    "confidence": current_conf
                }

        # RULE 3: HUMIDITY ISSUES
        # Handles "dry air" or generic "abnormal humidity"
        elif "humidity" in anomaly_type or "dry" in anomaly_type:
            if sensor_val < 40:
                recommendation = {
                    "action": "Increase greenhouse humidity.",
                    "explanation": f"Humidity dropped to {sensor_val}%. Excessive transpiration risk.",
                    "confidence": current_conf
                }
            else:
                recommendation = {
                    "action": "Increase ventilation and air circulation.",
                    "explanation": f"Humidity rose to {sensor_val}%. Fungal disease risk.",
                    "confidence": current_conf
                }

        return recommendation