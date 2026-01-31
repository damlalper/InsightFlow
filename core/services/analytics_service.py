"""
Analytics service - Application layer.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from decimal import Decimal
from core.domain.entities import AnalyticsResult
from core.infrastructure.clickhouse_client import ClickHouseClient
from core.utils.cache import cached_result
from core.utils.logging import analytics_logger


class AnalyticsService:
    """Service for computing marketing analytics."""

    def __init__(self):
        self.clickhouse = ClickHouseClient()

    @cached_result(key_prefix='analytics:roi', timeout=300)
    def calculate_roi(
        self,
        campaign_id: Optional[str] = None,
        platform: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> AnalyticsResult:
        """Calculate ROI and related metrics."""
        analytics_logger.info(
            f"Calculating ROI for campaign_id={campaign_id}, "
            f"platform={platform}, start_date={start_date}, end_date={end_date}"
        )
        
        try:
            aggregated = self.clickhouse.get_aggregated_metrics(
                campaign_id=campaign_id,
                platform=platform,
                start_date=start_date,
                end_date=end_date,
            )
        except Exception as e:
            analytics_logger.error(f"Error calculating ROI: {str(e)}")
            raise

        result = AnalyticsResult(
            total_cost=aggregated['total_cost'],
            total_revenue=aggregated['total_revenue'],
            total_clicks=aggregated['total_clicks'],
            total_impressions=aggregated['total_impressions'],
            total_conversions=aggregated['total_conversions'],
            date_range_start=start_date,
            date_range_end=end_date,
            campaign_id=campaign_id,
            platform=platform,
        )

        # Calculate derived metrics
        result.roi = result.calculate_roi()
        result.cpc = result.calculate_cpc()
        result.cpa = result.calculate_cpa()
        result.ctr = result.calculate_ctr()

        return result

    def get_trends(
        self,
        campaign_id: Optional[str] = None,
        platform: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        days: int = 30,
    ) -> List[Dict[str, Any]]:
        """Get time series trends."""
        if not start_date:
            end_date = end_date or datetime.utcnow()
            start_date = end_date - timedelta(days=days)

        return self.clickhouse.get_time_series_metrics(
            campaign_id=campaign_id,
            platform=platform,
            start_date=start_date,
            end_date=end_date,
        )

    def get_campaign_performance(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """Get top performing campaigns by ROI."""
        return self.clickhouse.get_campaign_performance(
            start_date=start_date,
            end_date=end_date,
            limit=limit,
        )
