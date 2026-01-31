"""
Tests for ingestion service.
"""
import pytest
from datetime import datetime
from core.services.ingestion_service import IngestionService
from core.repositories.campaign_repository import DjangoCampaignRepository


@pytest.mark.django_db
class TestIngestionService:
    """Tests for IngestionService."""

    def test_normalize_campaign(self):
        """Test campaign normalization."""
        service = IngestionService()
        record = {
            'campaign_id': 'camp_1',
            'campaign_name': 'Test Campaign',
            'platform': 'google_ads',
        }
        campaign = service._normalize_campaign(record)
        assert campaign.id == 'camp_1'
        assert campaign.name == 'Test Campaign'
        assert campaign.platform == 'google_ads'

    def test_normalize_metrics(self):
        """Test metrics normalization."""
        service = IngestionService()
        record = {
            'campaign_id': 'camp_1',
            'platform': 'google_ads',
            'date': '2024-01-15',
            'impressions': 1000,
            'clicks': 50,
            'cost': 25.50,
            'conversions': 5,
            'revenue': 150.00,
        }
        metrics = service._normalize_metrics(record)
        assert len(metrics) == 5  # impressions, clicks, cost, conversions, revenue
        assert metrics[0].metric_type.value == 'impressions'
        assert metrics[0].value == 1000
