"""
Anomaly detection using Z-score method.
"""
from typing import List, Dict, Any
from datetime import datetime, timedelta
from decimal import Decimal
import statistics
from core.domain.entities import Anomaly, MetricType
from core.infrastructure.clickhouse_client import ClickHouseClient


class AnomalyDetector:
    """Detect anomalies in metrics using Z-score."""

    def __init__(self, z_threshold: float = 2.5):
        """
        Initialize anomaly detector.
        
        Args:
            z_threshold: Z-score threshold for anomaly detection (default: 2.5)
        """
        self.z_threshold = z_threshold
        self.clickhouse = ClickHouseClient()

    def detect_anomalies(
        self,
        metric_type: MetricType,
        entity_id: str,
        entity_type: str = "campaign",
        lookback_days: int = 30,
    ) -> List[Anomaly]:
        """
        Detect anomalies for a specific metric.
        
        Args:
            metric_type: Type of metric to analyze
            entity_id: ID of the entity (campaign, ad, etc.)
            entity_type: Type of entity
            lookback_days: Number of days to look back for baseline
            
        Returns:
            List of detected anomalies
        """
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=lookback_days)

        # Get historical data
        time_series = self.clickhouse.get_time_series_metrics(
            campaign_id=entity_id if entity_type == "campaign" else None,
            start_date=start_date,
            end_date=end_date,
        )

        if len(time_series) < 7:  # Need at least 7 data points
            return []

        # Extract values for the metric type
        metric_key = metric_type.value
        values = [self._get_metric_value(point, metric_key) for point in time_series]
        dates = [point['date'] for point in time_series]

        # Calculate statistics
        if not values or all(v == 0 for v in values):
            return []

        mean = statistics.mean(values)
        stdev = statistics.stdev(values) if len(values) > 1 else 0

        if stdev == 0:
            return []

        # Detect anomalies
        anomalies = []
        for i, (value, date) in enumerate(zip(values, dates)):
            z_score = (value - mean) / stdev if stdev > 0 else 0

            if abs(z_score) >= self.z_threshold:
                severity = self._determine_severity(abs(z_score))
                description = self._generate_description(
                    metric_type, value, mean, z_score, entity_type
                )

                anomaly = Anomaly(
                    metric_type=metric_type,
                    entity_id=entity_id,
                    entity_type=entity_type,
                    date=date if isinstance(date, datetime) else datetime.combine(date, datetime.min.time()),
                    value=Decimal(str(value)),
                    expected_value=Decimal(str(mean)),
                    z_score=Decimal(str(round(z_score, 4))),
                    severity=severity,
                    description=description,
                )
                anomalies.append(anomaly)

        return anomalies

    def _get_metric_value(self, data_point: Dict[str, Any], metric_key: str) -> float:
        """Extract metric value from data point."""
        return float(data_point.get(metric_key, 0))

    def _determine_severity(self, abs_z_score: float) -> str:
        """Determine anomaly severity based on Z-score."""
        if abs_z_score >= 3.5:
            return "high"
        elif abs_z_score >= 2.5:
            return "medium"
        else:
            return "low"

    def _generate_description(
        self,
        metric_type: MetricType,
        value: float,
        mean: float,
        z_score: float,
        entity_type: str,
    ) -> str:
        """Generate human-readable description of anomaly."""
        direction = "spike" if z_score > 0 else "drop"
        percentage = abs((value - mean) / mean * 100) if mean > 0 else 0

        return (
            f"Anomalous {direction} detected in {metric_type.value} for {entity_type}. "
            f"Value: {value:.2f} (expected: {mean:.2f}, {percentage:.1f}% deviation, "
            f"Z-score: {z_score:.2f})"
        )
