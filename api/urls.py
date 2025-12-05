from django.urls import path
from .views import login_view, dashboard_view
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import (
    FarmListCreateView, PlotListCreateView, 
    SensorReadingListCreateView, AnomalyListCreateView, RecommendationListView
)

urlpatterns = [
    # The Simulator hits this URL to get a token
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Your data URLs
    path('farms/', FarmListCreateView.as_view(), name='farm-list'),
    path('plots/', PlotListCreateView.as_view(), name='plot-list'),
    path('sensor-readings/', SensorReadingListCreateView.as_view(), name='sensor-readings'),
    path('anomalies/', AnomalyListCreateView.as_view(), name='anomaly-list'),
    path('recommendations/', RecommendationListView.as_view(), name='recommendation-list'),
    
    #Frontend Pages
    path('login/', login_view, name='login'),
    path('dashboard/', dashboard_view, name='dashboard'),
]