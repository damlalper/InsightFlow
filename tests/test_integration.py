"""
Integration tests for API endpoints.
"""
import pytest
from django.test import Client
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from core.models import Campaign, Metric
from decimal import Decimal


@pytest.mark.django_db
class TestDataIngestionAPI:
    """Integration tests for data ingestion API."""

    def test_ingest_json_data(self):
        """Test JSON data ingestion."""
        client = APIClient()
        
        data = [
            {
                "campaign_id": "camp_test_1",
                "campaign_name": "Test Campaign",
                "platform": "google_ads",
                "date": "2024-01-15",
                "impressions": 1000,
                "clicks": 50,
                "cost": 25.50,
                "conversions": 5,
                "revenue": 150.00
            }
        ]
        
        response = client.post('/api/v1/data/ingest', data, format='json')
        assert response.status_code == 202
        assert 'task_id' in response.data
        assert response.data['records_count'] == 1

    def test_ingest_csv_data(self):
        """Test CSV data ingestion."""
        client = APIClient()
        
        csv_content = """campaign_id,platform,date,impressions,clicks,cost,conversions,revenue
camp_test_2,google_ads,2024-01-15,1000,50,25.50,5,150.00"""
        
        response = client.post(
            '/api/v1/data/ingest',
            csv_content,
            content_type='text/csv'
        )
        assert response.status_code == 202

    def test_ingest_invalid_data(self):
        """Test ingestion with invalid data."""
        client = APIClient()
        
        data = [{"invalid": "data"}]
        response = client.post('/api/v1/data/ingest', data, format='json')
        assert response.status_code == 400


@pytest.mark.django_db
class TestAnalyticsAPI:
    """Integration tests for analytics API."""

    def setup_method(self):
        """Set up test data."""
        # Create test campaign
        campaign = Campaign.objects.create(
            id="camp_analytics_1",
            name="Analytics Test Campaign",
            platform="google_ads",
            status="active"
        )
        
        # Create test metrics
        Metric.objects.create(
            campaign=campaign,
            date="2024-01-15",
            metric_type="impressions",
            value=1000,
            platform="google_ads"
        )
        Metric.objects.create(
            campaign=campaign,
            date="2024-01-15",
            metric_type="clicks",
            value=50,
            platform="google_ads"
        )
        Metric.objects.create(
            campaign=campaign,
            date="2024-01-15",
            metric_type="cost",
            value=Decimal('25.50'),
            platform="google_ads"
        )
        Metric.objects.create(
            campaign=campaign,
            date="2024-01-15",
            metric_type="revenue",
            value=Decimal('150.00'),
            platform="google_ads"
        )

    def test_roi_endpoint(self):
        """Test ROI analytics endpoint."""
        client = APIClient()
        response = client.get('/api/v1/analytics/roi?campaign_id=camp_analytics_1')
        assert response.status_code == 200
        assert 'roi' in response.data
        assert 'cpc' in response.data
        assert 'ctr' in response.data

    def test_trends_endpoint(self):
        """Test trends analytics endpoint."""
        client = APIClient()
        response = client.get('/api/v1/analytics/trends?days=30')
        assert response.status_code == 200
        assert isinstance(response.data, list)

    def test_anomalies_endpoint(self):
        """Test anomalies endpoint."""
        client = APIClient()
        response = client.get(
            '/api/v1/analytics/anomalies?'
            'metric_type=cost&entity_id=camp_analytics_1&entity_type=campaign'
        )
        assert response.status_code == 200
        assert isinstance(response.data, list)

    def test_insights_endpoint(self):
        """Test insights summary endpoint."""
        client = APIClient()
        response = client.get('/api/v1/insights/summary')
        assert response.status_code == 200
        assert isinstance(response.data, list)
