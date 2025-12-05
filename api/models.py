from django.db import models
from django.contrib.auth.models import User

class FarmProfile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='farms')
    name = models.CharField(max_length=100)
    owner_name = models.CharField(max_length=100)
    location = models.CharField(max_length=200)
    size_hectares = models.FloatField()

    def __str__(self):
        return f"{self.name} ({self.user.username})"

class FieldPlot(models.Model):
    farm = models.ForeignKey(FarmProfile, on_delete=models.CASCADE, related_name='plots')
    plot_name = models.CharField(max_length=50)
    crop_variety = models.CharField(max_length=100)
    area_sqm = models.FloatField()

    def __str__(self):
        return f"{self.plot_name} ({self.crop_variety})"

class SensorReading(models.Model):
    SENSOR_TYPES = [
        ('moisture', 'Soil Moisture'),
        ('temperature', 'Air Temperature'),
        ('humidity', 'Humidity'),
    ]
    plot = models.ForeignKey(FieldPlot, on_delete=models.CASCADE, related_name='readings')
    sensor_type = models.CharField(max_length=20, choices=SENSOR_TYPES)
    value = models.FloatField()
    timestamp = models.DateTimeField()
    source = models.CharField(max_length=50, default='simulator')

class AnomalyEvent(models.Model):
    SEVERITY = [('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('critical', 'Critical')]
    
    plot = models.ForeignKey(FieldPlot, on_delete=models.CASCADE, related_name='anomalies')
    anomaly_type = models.CharField(max_length=100)
    description = models.TextField()
    severity = models.CharField(max_length=10, choices=SEVERITY)
    model_confidence = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

class AgentRecommendation(models.Model):
    anomaly_event = models.OneToOneField(AnomalyEvent, on_delete=models.CASCADE, related_name='recommendation')
    recommended_action = models.CharField(max_length=255)
    explanation_text = models.TextField()
    confidence = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)