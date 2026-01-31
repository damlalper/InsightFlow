"""
Domain entities - Pure business logic with no framework dependencies.
"""
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from enum import Enum


class MetricType(str, Enum):
    """Metric types."""
    IMPRESSIONS = "impressions"
    CLICKS = "clicks"
    COST = "cost"
    CONVERSIONS = "conversions"
    REVENUE = "revenue"


@dataclass
class Campaign:
    """Campaign domain entity."""
    id: Optional[str] = None
    name: str = ""
    platform: str = ""
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    budget: Optional[Decimal] = None
    status: str = "active"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def is_active(self) -> bool:
        """Check if campaign is currently active."""
        if self.status != "active":
            return False
        now = datetime.utcnow()
        if self.start_date and now < self.start_date:
            return False
        if self.end_date and now > self.end_date:
            return False
        return True


@dataclass
class AdGroup:
    """AdGroup domain entity."""
    id: Optional[str] = None
    campaign_id: str = ""
    name: str = ""
    status: str = "active"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class Ad:
    """Ad domain entity."""
    id: Optional[str] = None
    ad_group_id: str = ""
    name: str = ""
    creative_url: Optional[str] = None
    status: str = "active"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class Metric:
    """Metric domain entity."""
    id: Optional[str] = None
    campaign_id: str = ""
    ad_group_id: Optional[str] = None
    ad_id: Optional[str] = None
    date: datetime = None
    metric_type: MetricType = MetricType.IMPRESSIONS
    value: Decimal = Decimal('0')
    platform: str = ""
    created_at: Optional[datetime] = None

    def __post_init__(self):
        """Validate metric after initialization."""
        if self.value < 0:
            raise ValueError("Metric value cannot be negative")


@dataclass
class Insight:
    """Insight domain entity."""
    id: Optional[str] = None
    type: str = ""  # e.g., "best_campaign", "underperforming_ad", "budget_inefficiency"
    title: str = ""
    description: str = ""
    entity_id: str = ""  # ID of the related entity (campaign, ad, etc.)
    entity_type: str = ""  # "campaign", "ad", "adgroup"
    severity: str = "info"  # "info", "warning", "critical"
    metadata: dict = None
    created_at: Optional[datetime] = None

    def __post_init__(self):
        """Initialize metadata if not provided."""
        if self.metadata is None:
            self.metadata = {}


@dataclass
class AnalyticsResult:
    """Analytics computation result."""
    roi: Optional[Decimal] = None
    cpc: Optional[Decimal] = None  # Cost Per Click
    cpa: Optional[Decimal] = None  # Cost Per Acquisition
    ctr: Optional[Decimal] = None  # Click-Through Rate
    total_cost: Decimal = Decimal('0')
    total_revenue: Decimal = Decimal('0')
    total_clicks: int = 0
    total_impressions: int = 0
    total_conversions: int = 0
    date_range_start: Optional[datetime] = None
    date_range_end: Optional[datetime] = None
    campaign_id: Optional[str] = None
    platform: Optional[str] = None

    def calculate_roi(self) -> Decimal:
        """Calculate ROI: (Revenue - Cost) / Cost * 100."""
        if self.total_cost == 0:
            return Decimal('0')
        return ((self.total_revenue - self.total_cost) / self.total_cost) * 100

    def calculate_cpc(self) -> Decimal:
        """Calculate CPC: Cost / Clicks."""
        if self.total_clicks == 0:
            return Decimal('0')
        return self.total_cost / self.total_clicks

    def calculate_cpa(self) -> Decimal:
        """Calculate CPA: Cost / Conversions."""
        if self.total_conversions == 0:
            return Decimal('0')
        return self.total_cost / self.total_conversions

    def calculate_ctr(self) -> Decimal:
        """Calculate CTR: (Clicks / Impressions) * 100."""
        if self.total_impressions == 0:
            return Decimal('0')
        return (Decimal(self.total_clicks) / Decimal(self.total_impressions)) * 100


@dataclass
class Anomaly:
    """Anomaly detection result."""
    id: Optional[str] = None
    metric_type: MetricType = MetricType.IMPRESSIONS
    entity_id: str = ""
    entity_type: str = ""  # "campaign", "ad", "adgroup"
    date: datetime = None
    value: Decimal = Decimal('0')
    expected_value: Decimal = Decimal('0')
    z_score: Decimal = Decimal('0')
    severity: str = "medium"  # "low", "medium", "high"
    description: str = ""
    created_at: Optional[datetime] = None
