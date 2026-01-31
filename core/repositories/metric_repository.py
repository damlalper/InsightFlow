"""
Metric repository interface and implementation.
"""
from abc import ABC, abstractmethod
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from core.domain.entities import Metric as MetricEntity, MetricType
from core.models import Metric as MetricModel


class MetricRepositoryInterface(ABC):
    """Metric repository interface."""

    @abstractmethod
    def create(self, metric: MetricEntity) -> MetricEntity:
        """Create a new metric."""
        pass

    @abstractmethod
    def create_batch(self, metrics: List[MetricEntity]) -> List[MetricEntity]:
        """Create multiple metrics in batch."""
        pass

    @abstractmethod
    def get_by_campaign(
        self,
        campaign_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[MetricEntity]:
        """Get metrics for a campaign."""
        pass


class DjangoMetricRepository(MetricRepositoryInterface):
    """Django ORM implementation of MetricRepository."""

    def _to_entity(self, model: MetricModel) -> MetricEntity:
        """Convert Django model to domain entity."""
        return MetricEntity(
            id=str(model.id),
            campaign_id=model.campaign.id,
            ad_group_id=model.ad_group.id if model.ad_group else None,
            ad_id=model.ad.id if model.ad else None,
            date=datetime.combine(model.date, datetime.min.time()),
            metric_type=MetricType(model.metric_type),
            value=model.value,
            platform=model.platform,
            created_at=model.created_at,
        )

    def _to_model(self, entity: MetricEntity) -> MetricModel:
        """Convert domain entity to Django model."""
        from core.models import Campaign, AdGroup, Ad

        campaign = Campaign.objects.get(id=entity.campaign_id)
        ad_group = None
        ad = None
        
        if entity.ad_group_id:
            try:
                ad_group = AdGroup.objects.get(id=entity.ad_group_id)
            except AdGroup.DoesNotExist:
                pass
        
        if entity.ad_id:
            try:
                ad = Ad.objects.get(id=entity.ad_id)
            except Ad.DoesNotExist:
                pass

        return MetricModel(
            campaign=campaign,
            ad_group=ad_group,
            ad=ad,
            date=entity.date.date(),
            metric_type=entity.metric_type.value,
            value=entity.value,
            platform=entity.platform,
        )

    def create(self, metric: MetricEntity) -> MetricEntity:
        """Create a new metric."""
        model = self._to_model(metric)
        model.save()
        return self._to_entity(model)

    def create_batch(self, metrics: List[MetricEntity]) -> List[MetricEntity]:
        """Create multiple metrics in batch."""
        models = [self._to_model(metric) for metric in metrics]
        created_models = MetricModel.objects.bulk_create(models, ignore_conflicts=True)
        return [self._to_entity(model) for model in created_models]

    def get_by_campaign(
        self,
        campaign_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[MetricEntity]:
        """Get metrics for a campaign."""
        queryset = MetricModel.objects.filter(campaign_id=campaign_id)
        if start_date:
            queryset = queryset.filter(date__gte=start_date.date())
        if end_date:
            queryset = queryset.filter(date__lte=end_date.date())
        return [self._to_entity(model) for model in queryset]
