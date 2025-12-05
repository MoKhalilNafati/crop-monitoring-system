import os
import django

# 1. Setup Django Environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from api.models import AnomalyEvent, FieldPlot

def force_save_anomaly():
    print("🛠️ ATTEMPTING TO FORCE-SAVE AN ANOMALY...")

    # 2. Get a Plot (We need one to link the anomaly to)
    plot = FieldPlot.objects.first()
    if not plot:
        print("❌ ERROR: You have no Plots in the database. Create a Plot in Admin first.")
        return

    print(f"📍 Found Plot: {plot.plot_name} (ID: {plot.id})")

    # 3. Try to Create the Anomaly
    try:
        anomaly = AnomalyEvent.objects.create(
            plot=plot,
            anomaly_type="DEBUG_TEST_FAILURE",
            description="This is a forced test to prove DB works.",
            severity="critical",
            model_confidence=1.0
            # Note: NO related_reading field here
        )
        print(f"✅ SUCCESS! Anomaly saved with ID: {anomaly.id}")
        print("👉 Go check your Admin Panel now.")
        
    except Exception as e:
        print(f"❌ DATABASE ERROR: {e}")

if __name__ == "__main__":
    force_save_anomaly()