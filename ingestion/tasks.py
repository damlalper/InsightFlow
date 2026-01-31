"""
Celery tasks for async data ingestion.
"""
from celery import shared_task
from typing import List, Dict, Any
from core.services.ingestion_service import IngestionService
from core.infrastructure.clickhouse_client import ClickHouseClient


@shared_task
def ingest_marketing_data(data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Async task to ingest marketing data.
    
    Args:
        data: List of marketing data records
        
    Returns:
        Dictionary with ingestion results
    """
    service = IngestionService()
    result = service.normalize_and_store(data)

    # Also store in ClickHouse for analytics
    clickhouse = ClickHouseClient()
    clickhouse_metrics = _prepare_clickhouse_metrics(data)
    if clickhouse_metrics:
        clickhouse.insert_metrics(clickhouse_metrics)

    return result


def _prepare_clickhouse_metrics(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Prepare metrics for ClickHouse insertion."""
    metrics = []
    
    for record in data:
        # Group metrics by date, campaign, ad_group, ad
        metric_record = {
            'campaign_id': record.get('campaign_id', ''),
            'ad_group_id': record.get('ad_group_id') or None,
            'ad_id': record.get('ad_id') or None,
            'date': record.get('date'),
            'platform': record.get('platform', 'unknown'),
            'impressions': int(record.get('impressions', 0)),
            'clicks': int(record.get('clicks', 0)),
            'cost': float(record.get('cost', 0)),
            'conversions': int(record.get('conversions', 0)),
            'revenue': float(record.get('revenue', 0)),
        }
        metrics.append(metric_record)
    
    return metrics
