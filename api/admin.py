from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import FarmProfile, FieldPlot, SensorReading, AnomalyEvent, AgentRecommendation

@admin.register(FarmProfile)
class FarmProfileAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner_name', 'location', 'size_hectares')

@admin.register(FieldPlot)
class FieldPlotAdmin(admin.ModelAdmin):
    list_display = ('plot_name', 'crop_variety', 'farm', 'area_sqm')
    list_filter = ('farm',) # Adds a sidebar filter

@admin.register(SensorReading)
class SensorReadingAdmin(admin.ModelAdmin):
    list_display = ('sensor_type', 'value', 'plot', 'timestamp')
    list_filter = ('sensor_type', 'plot') # Essential for filtering specific sensors
    ordering = ('-timestamp',)

@admin.register(AnomalyEvent)
class AnomalyEventAdmin(admin.ModelAdmin):
    list_display = ('anomaly_type', 'severity', 'plot', 'timestamp', 'model_confidence')
    list_filter = ('severity', 'anomaly_type')

@admin.register(AgentRecommendation)
class AgentRecommendationAdmin(admin.ModelAdmin):
    list_display = ('recommended_action', 'confidence', 'created_at')