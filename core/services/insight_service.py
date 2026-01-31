"""
Insight generation service - Application layer.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from decimal import Decimal
from core.domain.entities import Insight
from core.services.analytics_service import AnalyticsService
from analytics.anomalies import AnomalyDetector
from core.models import Insight as InsightModel


class InsightService:
    """Service for generating marketing insights."""

    def __init__(self):
        self.analytics_service = AnalyticsService()
        self.anomaly_detector = AnomalyDetector()

    def generate_summary(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 10,
    ) -> List[Insight]:
        """
        Generate summary insights including:
        - Best performing campaigns
        - Underperforming ads
        - Budget inefficiency signals
        """
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = end_date - timedelta(days=30)

        insights = []

        # Get best performing campaigns
        best_campaigns = self._get_best_campaigns(start_date, end_date, limit)
        for campaign in best_campaigns:
            insight = Insight(
                type='best_campaign',
                title=f"Top Performer: {campaign.get('name', 'Campaign')}",
                description=(
                    f"Campaign achieved ROI of {campaign.get('roi', 0):.2f}% with "
                    f"${campaign.get('revenue', 0):.2f} revenue from ${campaign.get('cost', 0):.2f} spend."
                ),
                entity_id=campaign.get('campaign_id', ''),
                entity_type='campaign',
                severity='info',
                metadata={
                    'roi': float(campaign.get('roi', 0)),
                    'revenue': float(campaign.get('revenue', 0)),
                    'cost': float(campaign.get('cost', 0)),
                },
            )
            insights.append(insight)

        # Get underperforming ads
        underperforming_ads = self._get_underperforming_ads(start_date, end_date, limit)
        for ad in underperforming_ads:
            insight = Insight(
                type='underperforming_ad',
                title=f"Underperforming Ad: {ad.get('ad_name', 'Ad')}",
                description=(
                    f"Ad has negative ROI ({ad.get('roi', 0):.2f}%) or high CPA "
                    f"(${ad.get('cpa', 0):.2f}). Consider pausing or optimizing."
                ),
                entity_id=ad.get('ad_id', ''),
                entity_type='ad',
                severity='warning' if ad.get('roi', 0) < -20 else 'info',
                metadata={
                    'roi': ad.get('roi', 0),
                    'cpa': ad.get('cpa', 0),
                    'cost': ad.get('cost', 0),
                    'revenue': ad.get('revenue', 0),
                },
            )
            insights.append(insight)

        # Detect anomalies
        anomalies = self._detect_recent_anomalies(start_date, end_date)
        for anomaly in anomalies:
            insight = Insight(
                type='anomaly_detected',
                title=f"Anomaly Detected: {anomaly.metric_type.value}",
                description=anomaly.description,
                entity_id=anomaly.entity_id,
                entity_type=anomaly.entity_type,
                severity=anomaly.severity,
                metadata={
                    'z_score': float(anomaly.z_score),
                    'value': float(anomaly.value),
                    'expected_value': float(anomaly.expected_value),
                },
            )
            insights.append(insight)

        # Store insights
        for insight in insights:
            self._store_insight(insight)

        return insights

    def _get_best_campaigns(
        self,
        start_date: datetime,
        end_date: datetime,
        limit: int,
    ) -> List[Dict[str, Any]]:
        """Get best performing campaigns by ROI."""
        return self.analytics_service.get_campaign_performance(
            start_date=start_date,
            end_date=end_date,
            limit=limit,
        )

    def _get_underperforming_ads(
        self,
        start_date: datetime,
        end_date: datetime,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """Get underperforming ads (low ROI or high CPA)."""
        from core.models import Ad, Metric as MetricModel
        from django.db.models import Sum, F, Q
        from decimal import Decimal

        # Get ads with metrics in date range
        ads_with_metrics = MetricModel.objects.filter(
            date__gte=start_date.date(),
            date__lte=end_date.date(),
            ad__isnull=False,
        ).values('ad_id', 'ad__name').annotate(
            total_cost=Sum('value', filter=Q(metric_type='cost')),
            total_revenue=Sum('value', filter=Q(metric_type='revenue')),
            total_clicks=Sum('value', filter=Q(metric_type='clicks')),
            total_conversions=Sum('value', filter=Q(metric_type='conversions')),
        ).filter(total_cost__gt=0).order_by('total_cost')

        underperforming = []
        for ad_data in ads_with_metrics[:limit * 2]:  # Get more to filter
            cost = Decimal(str(ad_data['total_cost'] or 0))
            revenue = Decimal(str(ad_data['total_revenue'] or 0))
            conversions = int(ad_data['total_conversions'] or 0)
            
            if cost == 0:
                continue
                
            roi = ((revenue - cost) / cost * 100) if cost > 0 else Decimal('0')
            cpa = (cost / conversions) if conversions > 0 else Decimal('999999')
            
            # Flag as underperforming if ROI < 0 or CPA > 50
            if roi < 0 or cpa > 50:
                underperforming.append({
                    'ad_id': ad_data['ad_id'],
                    'ad_name': ad_data['ad__name'],
                    'roi': float(roi),
                    'cpa': float(cpa),
                    'cost': float(cost),
                    'revenue': float(revenue),
                })
                if len(underperforming) >= limit:
                    break

        return underperforming

    def _detect_recent_anomalies(
        self,
        start_date: datetime,
        end_date: datetime,
    ) -> List:
        """Detect recent anomalies across all campaigns."""
        from core.models import Campaign
        from core.domain.entities import MetricType
        
        anomalies = []
        campaigns = Campaign.objects.all()[:20]  # Limit to avoid too many queries
        
        for campaign in campaigns:
            # Check for anomalies in key metrics
            for metric_type in [MetricType.COST, MetricType.REVENUE, MetricType.CLICKS]:
                try:
                    detected = self.anomaly_detector.detect_anomalies(
                        metric_type=metric_type,
                        entity_id=campaign.id,
                        entity_type='campaign',
                        lookback_days=30,
                    )
                    # Only include recent anomalies
                    for anomaly in detected:
                        if start_date <= anomaly.date <= end_date:
                            anomalies.append(anomaly)
                except Exception:
                    # Skip if error (e.g., not enough data)
                    continue
        
        return anomalies

    def _store_insight(self, insight: Insight):
        """Store insight in database."""
        InsightModel.objects.create(
            type=insight.type,
            title=insight.title,
            description=insight.description,
            entity_id=insight.entity_id,
            entity_type=insight.entity_type,
            severity=insight.severity,
            metadata=insight.metadata or {},
        )
