"""
Campaign repository interface and implementation.
"""
from abc import ABC, abstractmethod
from typing import Optional, List
from core.domain.entities import Campaign as CampaignEntity
from core.models import Campaign as CampaignModel


class CampaignRepositoryInterface(ABC):
    """Campaign repository interface."""

    @abstractmethod
    def get_by_id(self, campaign_id: str) -> Optional[CampaignEntity]:
        """Get campaign by ID."""
        pass

    @abstractmethod
    def create(self, campaign: CampaignEntity) -> CampaignEntity:
        """Create a new campaign."""
        pass

    @abstractmethod
    def update(self, campaign: CampaignEntity) -> CampaignEntity:
        """Update an existing campaign."""
        pass

    @abstractmethod
    def list_all(self, platform: Optional[str] = None) -> List[CampaignEntity]:
        """List all campaigns, optionally filtered by platform."""
        pass


class DjangoCampaignRepository(CampaignRepositoryInterface):
    """Django ORM implementation of CampaignRepository."""

    def _to_entity(self, model: CampaignModel) -> CampaignEntity:
        """Convert Django model to domain entity."""
        return CampaignEntity(
            id=model.id,
            name=model.name,
            platform=model.platform,
            start_date=model.start_date,
            end_date=model.end_date,
            budget=model.budget,
            status=model.status,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _to_model(self, entity: CampaignEntity) -> CampaignModel:
        """Convert domain entity to Django model."""
        return CampaignModel(
            id=entity.id,
            name=entity.name,
            platform=entity.platform,
            start_date=entity.start_date,
            end_date=entity.end_date,
            budget=entity.budget,
            status=entity.status,
        )

    def get_by_id(self, campaign_id: str) -> Optional[CampaignEntity]:
        """Get campaign by ID."""
        try:
            model = CampaignModel.objects.get(id=campaign_id)
            return self._to_entity(model)
        except CampaignModel.DoesNotExist:
            return None

    def create(self, campaign: CampaignEntity) -> CampaignEntity:
        """Create a new campaign."""
        model = self._to_model(campaign)
        model.save()
        return self._to_entity(model)

    def update(self, campaign: CampaignEntity) -> CampaignEntity:
        """Update an existing campaign."""
        model = CampaignModel.objects.get(id=campaign.id)
        model.name = campaign.name
        model.platform = campaign.platform
        model.start_date = campaign.start_date
        model.end_date = campaign.end_date
        model.budget = campaign.budget
        model.status = campaign.status
        model.save()
        return self._to_entity(model)

    def list_all(self, platform: Optional[str] = None) -> List[CampaignEntity]:
        """List all campaigns, optionally filtered by platform."""
        queryset = CampaignModel.objects.all()
        if platform:
            queryset = queryset.filter(platform=platform)
        return [self._to_entity(model) for model in queryset]
