"""
Ingestion service - Application layer.
"""
from typing import List, Dict, Any
from datetime import datetime
from decimal import Decimal
from core.domain.entities import (
    Campaign,
    AdGroup,
    Ad,
    Metric,
    MetricType,
)
from core.repositories.campaign_repository import DjangoCampaignRepository
from core.repositories.metric_repository import DjangoMetricRepository
from core.models import AdGroup as AdGroupModel, Ad as AdModel


class IngestionService:
    """Service for ingesting marketing data."""

    def __init__(self):
        self.campaign_repo = DjangoCampaignRepository()
        self.metric_repo = DjangoMetricRepository()

    def normalize_and_store(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Normalize and store ingested data.
        
        Expected data format:
        [
            {
                "campaign_id": "camp_1",
                "campaign_name": "Summer Sale",
                "platform": "google_ads",
                "ad_group_id": "ag_1",
                "ad_group_name": "Banner Ads",
                "ad_id": "ad_1",
                "ad_name": "Banner 1",
                "date": "2024-01-15",
                "impressions": 1000,
                "clicks": 50,
                "cost": 25.50,
                "conversions": 5,
                "revenue": 150.00
            },
            ...
        ]
        """
        campaigns_created = 0
        ad_groups_created = 0
        ads_created = 0
        metrics_created = 0

        metrics_to_store = []

        for record in data:
            # Normalize and create Campaign
            campaign = self._normalize_campaign(record)
            existing_campaign = self.campaign_repo.get_by_id(campaign.id)
            if not existing_campaign:
                self.campaign_repo.create(campaign)
                campaigns_created += 1

            # Normalize and create AdGroup
            if record.get('ad_group_id'):
                ad_group = self._normalize_ad_group(record, campaign.id)
                if not AdGroupModel.objects.filter(id=ad_group.id).exists():
                    AdGroupModel.objects.create(
                        id=ad_group.id,
                        campaign_id=campaign.id,
                        name=ad_group.name,
                        status=ad_group.status,
                    )
                    ad_groups_created += 1

            # Normalize and create Ad
            if record.get('ad_id'):
                ad = self._normalize_ad(record, record.get('ad_group_id'))
                if ad and not AdModel.objects.filter(id=ad.id).exists():
                    AdModel.objects.create(
                        id=ad.id,
                        ad_group_id=record.get('ad_group_id'),
                        name=ad.name,
                        creative_url=ad.creative_url,
                        status=ad.status,
                    )
                    ads_created += 1

            # Normalize metrics
            metrics = self._normalize_metrics(record)
            metrics_to_store.extend(metrics)

        # Batch insert metrics
        if metrics_to_store:
            self.metric_repo.create_batch(metrics_to_store)
            metrics_created = len(metrics_to_store)

        return {
            'campaigns_created': campaigns_created,
            'ad_groups_created': ad_groups_created,
            'ads_created': ads_created,
            'metrics_created': metrics_created,
        }

    def _normalize_campaign(self, record: Dict[str, Any]) -> Campaign:
        """Normalize campaign data."""
        from datetime import datetime as dt

        return Campaign(
            id=record['campaign_id'],
            name=record.get('campaign_name', record['campaign_id']),
            platform=record['platform'],
            start_date=None,  # Can be extracted from record if available
            end_date=None,
            budget=None,  # Can be extracted from record if available
            status='active',
        )

    def _normalize_ad_group(self, record: Dict[str, Any], campaign_id: str) -> AdGroup:
        """Normalize ad group data."""
        return AdGroup(
            id=record['ad_group_id'],
            campaign_id=campaign_id,
            name=record.get('ad_group_name', record['ad_group_id']),
            status='active',
        )

    def _normalize_ad(self, record: Dict[str, Any], ad_group_id: str) -> Ad:
        """Normalize ad data."""
        if not record.get('ad_id'):
            return None

        return Ad(
            id=record['ad_id'],
            ad_group_id=ad_group_id,
            name=record.get('ad_name', record['ad_id']),
            creative_url=record.get('creative_url'),
            status='active',
        )

    def _normalize_metrics(self, record: Dict[str, Any]) -> List[Metric]:
        """Normalize metrics from a record."""
        from datetime import datetime as dt

        date_str = record.get('date')
        if isinstance(date_str, str):
            date = dt.strptime(date_str, '%Y-%m-%d')
        else:
            date = dt.now()

        metrics = []
        platform = record.get('platform', 'unknown')

        # Create metric for each metric type
        metric_mapping = {
            'impressions': MetricType.IMPRESSIONS,
            'clicks': MetricType.CLICKS,
            'cost': MetricType.COST,
            'conversions': MetricType.CONVERSIONS,
            'revenue': MetricType.REVENUE,
        }

        for key, metric_type in metric_mapping.items():
            if key in record and record[key] is not None:
                metric = Metric(
                    campaign_id=record['campaign_id'],
                    ad_group_id=record.get('ad_group_id'),
                    ad_id=record.get('ad_id'),
                    date=date,
                    metric_type=metric_type,
                    value=Decimal(str(record[key])),
                    platform=platform,
                )
                metrics.append(metric)

        return metrics
