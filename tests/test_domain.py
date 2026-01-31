"""
Tests for domain entities.
"""
import pytest
from datetime import datetime
from decimal import Decimal
from core.domain.entities import (
    Campaign,
    Metric,
    MetricType,
    AnalyticsResult,
)


class TestCampaign:
    """Tests for Campaign entity."""

    def test_campaign_is_active(self):
        """Test campaign active status."""
        campaign = Campaign(
            id="camp_1",
            name="Test Campaign",
            platform="google_ads",
            status="active",
            start_date=None,
            end_date=None,
        )
        assert campaign.is_active() is True

    def test_campaign_is_inactive_when_status_inactive(self):
        """Test campaign inactive when status is inactive."""
        campaign = Campaign(
            id="camp_1",
            name="Test Campaign",
            platform="google_ads",
            status="paused",
        )
        assert campaign.is_active() is False


class TestMetric:
    """Tests for Metric entity."""

    def test_metric_validation_negative_value(self):
        """Test metric validation rejects negative values."""
        with pytest.raises(ValueError, match="cannot be negative"):
            Metric(
                campaign_id="camp_1",
                date=datetime.utcnow(),
                metric_type=MetricType.IMPRESSIONS,
                value=Decimal('-10'),
                platform="google_ads",
            )


class TestAnalyticsResult:
    """Tests for AnalyticsResult entity."""

    def test_calculate_roi(self):
        """Test ROI calculation."""
        result = AnalyticsResult(
            total_cost=Decimal('100'),
            total_revenue=Decimal('150'),
        )
        roi = result.calculate_roi()
        assert roi == Decimal('50')  # (150-100)/100 * 100 = 50%

    def test_calculate_roi_zero_cost(self):
        """Test ROI calculation with zero cost."""
        result = AnalyticsResult(
            total_cost=Decimal('0'),
            total_revenue=Decimal('150'),
        )
        roi = result.calculate_roi()
        assert roi == Decimal('0')

    def test_calculate_cpc(self):
        """Test CPC calculation."""
        result = AnalyticsResult(
            total_cost=Decimal('100'),
            total_clicks=50,
        )
        cpc = result.calculate_cpc()
        assert cpc == Decimal('2')  # 100/50 = 2

    def test_calculate_ctr(self):
        """Test CTR calculation."""
        result = AnalyticsResult(
            total_clicks=50,
            total_impressions=1000,
        )
        ctr = result.calculate_ctr()
        assert ctr == Decimal('5')  # (50/1000) * 100 = 5%
