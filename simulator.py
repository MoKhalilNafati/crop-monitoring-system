import requests
import time
import datetime
import numpy as np
from faker import Faker

# Configuration
BASE_URL = "http://127.0.0.1:8000/api"
USERNAME = "admin"
PASSWORD = "admin"

# Initialize Faker
fake = Faker()

def get_token():
    try:
        response = requests.post(f"{BASE_URL}/token/", data={
            "username": USERNAME, "password": PASSWORD
        })
        if response.status_code == 200:
            return response.json()['access']
        else:
            print("❌ Login Failed:", response.text[:100])
            return None
    except Exception as e:
        print(f"Connection Error during login: {e}")
        return None

def get_plots(token):
    """Fetches available Plot IDs."""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/plots/", headers=headers)
        if response.status_code == 200:
            plots = response.json()
            ids = [p['id'] for p in plots]
            if not ids: print("⚠️ No plots found in DB! Create some in Admin Panel.")
            return ids
        return []
    except:
        return []

def generate_reading(hour, plot_variation=0):
    """
    Generates data using NumPy for realistic distributions.
    """
    # --- CHAOS MATH (Unique patterns per plot) ---
    time_shift = plot_variation * 2 
    amp_shift = 1 + (plot_variation % 3) 

    # 1. Calculate Baseline using NumPy
    temp_base = 25
    cycle = np.sin((hour - 8 + time_shift) * np.pi / 12)
    temp_variation = (10 + amp_shift) * cycle
    
    # Gaussian Noise
    noise_temp = np.random.normal(loc=0, scale=0.5) 
    temperature = temp_base + temp_variation + noise_temp

    noise_hum = np.random.normal(loc=0, scale=1.5)
    humidity = 80 - (temp_variation * 1.5) + noise_hum

    dry_rate = 0.5 + (plot_variation * 0.1)
    noise_moist = np.random.normal(loc=0, scale=0.2)
    moisture = 60 - (dry_rate * hour) + noise_moist
    
    if moisture < (20 + plot_variation): 
        moisture = 60 + np.random.uniform(-2, 5)

    # 2. INJECT ANOMALIES (20% chance)
    if np.random.random() < 0.2: 
        anomaly_type = np.random.choice(['heat_wave', 'pump_failure', 'frost', 'dry_air', 'flood'])
        
        if anomaly_type == 'heat_wave':
            print(f"⚠️  Simulating Heat Wave on Plot {plot_variation}")
            temperature = np.random.uniform(40, 50) 
            
        elif anomaly_type == 'pump_failure':
            print(f"⚠️  Simulating Pump Failure on Plot {plot_variation}")
            moisture = np.random.uniform(5, 15)

        elif anomaly_type == 'frost':
            print(f"⚠️  Simulating Cold Stress on Plot {plot_variation}")
            temperature = np.random.uniform(0, 4) 
            
        elif anomaly_type == 'dry_air':
            print(f"⚠️  Simulating Dry Air on Plot {plot_variation}")
            humidity = np.random.uniform(5, 15)

        elif anomaly_type == 'flood':
            print(f"⚠️  Simulating Flood on Plot {plot_variation}")
            moisture = np.random.uniform(92, 99)
            
    return round(temperature, 2), round(humidity, 2), round(moisture, 2)

def run_simulator():
    token = get_token()
    if not token: return

    headers = {"Authorization": f"Bearer {token}"}
    plot_ids = get_plots(token)
    if not plot_ids: plot_ids = [1]

    print(f"🌱 Simulator started for Plots: {plot_ids}")
    
    # --- Generate UNIQUE Hardware IDs for EACH plot ---
    plot_hardware_map = {}
    for pid in plot_ids:
        # Generates 'Sensor-X1Y2', 'Sensor-A9B8', etc.
        plot_hardware_map[pid] = fake.bothify(text='Sensor-##??')
        print(f"   📍 Plot {pid} connected to hardware: {plot_hardware_map[pid]}")

    virtual_hour = 8 
    
    while True:
        print(f"\n--- 🕒 Simulating Hour {virtual_hour}:00 ---")
        
        for plot_id in plot_ids:
            temp, hum, moist = generate_reading(virtual_hour, plot_variation=plot_id)
            
            # Get the specific sensor ID for this plot
            current_source = plot_hardware_map.get(plot_id, "Sensor-Unknown")

            sensors = [
                {"type": "temperature", "value": temp},
                {"type": "humidity", "value": hum},
                {"type": "moisture", "value": moist}
            ]

            for sensor in sensors:
                payload = {
                    "plot": plot_id,
                    "sensor_type": sensor['type'],
                    "value": sensor['value'],
                    "timestamp": datetime.datetime.now().isoformat(),
                    "source": current_source  # <--- Unique ID per plot
                }
                try:
                    r = requests.post(f"{BASE_URL}/sensor-readings/", json=payload, headers=headers)
                    if r.status_code == 401:
                        print("🔄 Token expired! Re-logging in...")
                        token = get_token()
                        if token:
                            headers = {"Authorization": f"Bearer {token}"}
                            requests.post(f"{BASE_URL}/sensor-readings/", json=payload, headers=headers)
                except Exception as e:
                    print(f"Error sending: {e}")
            
            print(f"✅ Sent data for Plot {plot_id} (Source: {current_source})")

        virtual_hour += 1
        if virtual_hour > 23: virtual_hour = 0
        time.sleep(2)

if __name__ == "__main__":
    run_simulator()