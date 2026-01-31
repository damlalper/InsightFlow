"""
API URL configuration.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views import (
    DataIngestionView,
    ROIAnalyticsView,
    TrendsAnalyticsView,
    AnomaliesAnalyticsView,
    InsightsSummaryView,
)
from api.auth_views import obtain_token, refresh_token

app_name = 'api'

urlpatterns = [
    # Authentication
    path('auth/login', obtain_token, name='auth-login'),
    path('auth/refresh', refresh_token, name='auth-refresh'),
    
    # Data Ingestion
    path('data/ingest', DataIngestionView.as_view(), name='data-ingest'),
    
    # Analytics
    path('analytics/roi', ROIAnalyticsView.as_view(), name='analytics-roi'),
    path('analytics/trends', TrendsAnalyticsView.as_view(), name='analytics-trends'),
    path('analytics/anomalies', AnomaliesAnalyticsView.as_view(), name='analytics-anomalies'),
    
    # Insights
    path('insights/summary', InsightsSummaryView.as_view(), name='insights-summary'),
]
