from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

# Import your models and serializers
from .models import FarmProfile, FieldPlot, SensorReading, AnomalyEvent, AgentRecommendation
from .serializers import (
    FarmProfileSerializer, FieldPlotSerializer, SensorReadingSerializer, 
    AnomalyEventSerializer, AgentRecommendationSerializer
)
# Import the new ML logic
from ml_module.logic import AnomalyDetector

# Initialize the detector once when the server starts
detector = AnomalyDetector()

# 1. Farm View (Only owner sees their farms)
class FarmListCreateView(generics.ListCreateAPIView):
    serializer_class = FarmProfileSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # Automatically assign the logged-in user as the owner
        serializer.save(user=self.request.user)

    def get_queryset(self):
        # Admin sees all; Farmer sees only their own farms
        if self.request.user.is_superuser:
            return FarmProfile.objects.all()
        return FarmProfile.objects.filter(user=self.request.user)

# 2. Plot View (Only owner sees their plots)
class PlotListCreateView(generics.ListCreateAPIView):
    serializer_class = FieldPlotSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # 1. Admin sees everything
        if self.request.user.is_superuser:
            return FieldPlot.objects.all()
        
        # 2. Farmer sees only plots linked to their farms
        # Logic: Look for plots where the 'farm' owner is the current user
        return FieldPlot.objects.filter(farm__user=self.request.user)

# 3. Sensor Data Ingestion & Retrieval (Secure + ML Integration)
class SensorReadingListCreateView(generics.ListCreateAPIView):
    serializer_class = SensorReadingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # 1. Security Filter: Only show readings from the user's own plots
        if self.request.user.is_superuser:
            queryset = SensorReading.objects.all()
        else:
            # Logic: Reading -> Plot -> Farm -> User matches current user
            queryset = SensorReading.objects.filter(plot__farm__user=self.request.user)

        # 2. URL Filter: ?plot=1 (For dashboard)
        plot_id = self.request.query_params.get('plot')
        if plot_id is not None:
            queryset = queryset.filter(plot__id=plot_id)
            
        return queryset

    def perform_create(self, serializer):
        # 1. Save the sensor reading
        reading = serializer.save()
        
        try:
            # 2. Run ML Check (Unpack 3 values: anomaly bool, text reason, confidence float)
            is_anomaly, reason, conf_score = detector.check_anomaly(reading.sensor_type, reading.value)
            
            if is_anomaly:
                # --- DYNAMIC SEVERITY LOGIC ---
                severity = 'medium' # Default

                # Rule A: Confidence Impact
                if conf_score > 0.90:
                    severity = 'high'
                elif conf_score < 0.60:
                    severity = 'low'

                # Rule B: Critical Keywords (Updated to match ml_module/logic.py)
                critical_keywords = [
                    'failure',       # Matches "Pump Failure"
                    'drought',       # Matches "Drought"
                    'waterlogging',  # Matches "Waterlogging"
                    'heat stress',   # Matches "Heat Stress"
                    'frost',         # Matches "Frost Danger"
                    'dry air'        # Matches "Extremely Dry Air"
                ]
                
                if any(k in reason.lower() for k in critical_keywords) and conf_score > 0.8:
                    severity = 'critical'

                # Rule C: Downgrade vague "Abnormal Patterns"
                if 'abnormal' in reason.lower():
                    if severity == 'critical': severity = 'high'
                # -------------------------------

                print(f"🚨 ANOMALY: {reason} (Val: {reading.value}, Conf: {conf_score}, Sev: {severity})")
                
                # 3. Save the event using the CALCULATED variables
                AnomalyEvent.objects.create(
                    plot=reading.plot,
                    anomaly_type=reason,
                    description=f"Abnormal {reading.sensor_type} reading: {reading.value}",
                    severity=severity, 
                    model_confidence=conf_score,
                    # related_reading=reading (REMOVED to prevent crash)
                )
                print("✅ Anomaly saved.")

        except Exception as e:
            print(f"❌ CRASH IN ML: {e}")
                
# 4. Anomaly & Recommendation Views
class AnomalyListCreateView(generics.ListCreateAPIView):
    serializer_class = AnomalyEventSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Filter anomalies by ownership
        if self.request.user.is_superuser:
            return AnomalyEvent.objects.all().order_by('-timestamp')
        return AnomalyEvent.objects.filter(plot__farm__user=self.request.user).order_by('-timestamp')

class RecommendationListView(generics.ListAPIView):
    serializer_class = AgentRecommendationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # 1. Filter recommendations by ownership (via Anomaly -> Plot -> Farm -> User)
        if self.request.user.is_superuser:
            queryset = AgentRecommendation.objects.all().order_by('-created_at')
        else:
            queryset = AgentRecommendation.objects.filter(anomaly_event__plot__farm__user=self.request.user).order_by('-created_at')
        
        # 2. Filter by specific plot (?plot=1)
        plot_id = self.request.query_params.get('plot')
        if plot_id is not None:
            queryset = queryset.filter(anomaly_event__plot__id=plot_id)
            
        return queryset

# 5. Frontend Template Views
def login_view(request):
    return render(request, 'api/login.html')

def dashboard_view(request):
    return render(request, 'api/dashboard.html')