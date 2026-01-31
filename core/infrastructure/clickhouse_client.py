"""
ClickHouse client for analytics data storage.
"""
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
from decimal import Decimal
import clickhouse_connect
from django.conf import settings


class ClickHouseClient:
    """ClickHouse client for analytics operations."""

    def __init__(self):
        """Initialize ClickHouse client."""
        # ClickHouse default user doesn't require password if empty
        password = settings.CLICKHOUSE_PASSWORD if settings.CLICKHOUSE_PASSWORD else None
        self.client = clickhouse_connect.get_client(
            host=settings.CLICKHOUSE_HOST,
            port=settings.CLICKHOUSE_PORT,
            database=settings.CLICKHOUSE_DB,
            username=settings.CLICKHOUSE_USER,
            password=password,
        )
        self._ensure_tables()

    def _ensure_tables(self):
        """Ensure analytics tables exist."""
        # Metrics table for analytics
        self.client.command("""
            CREATE TABLE IF NOT EXISTS metrics_analytics (
                campaign_id String,
                ad_group_id Nullable(String),
                ad_id Nullable(String),
                date Date,
                platform String,
                impressions UInt64,
                clicks UInt64,
                cost Decimal(15, 2),
                conversions UInt32,
                revenue Decimal(15, 2),
                created_at DateTime DEFAULT now()
            ) ENGINE = MergeTree()
            ORDER BY (date, campaign_id, platform)
            PARTITION BY toYYYYMM(date)
        """)

        # Anomalies table
        self.client.command("""
            CREATE TABLE IF NOT EXISTS anomalies (
                id String,
                metric_type String,
                entity_id String,
                entity_type String,
                date Date,
                value Decimal(15, 2),
                expected_value Decimal(15, 2),
                z_score Decimal(10, 4),
                severity String,
                description String,
                created_at DateTime DEFAULT now()
            ) ENGINE = MergeTree()
            ORDER BY (date, entity_id, metric_type)
            PARTITION BY toYYYYMM(date)
        """)

    def insert_metrics(self, metrics: List[Dict[str, Any]]):
        """Insert metrics into ClickHouse."""
        if not metrics:
            return

        self.client.insert(
            'metrics_analytics',
            metrics,
            column_names=[
                'campaign_id', 'ad_group_id', 'ad_id', 'date', 'platform',
                'impressions', 'clicks', 'cost', 'conversions', 'revenue'
            ]
        )

    def get_aggregated_metrics(
        self,
        campaign_id: Optional[str] = None,
        platform: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """Get aggregated metrics from ClickHouse."""
        conditions = []
        params = {}

        if campaign_id:
            conditions.append("campaign_id = {campaign_id:String}")
            params['campaign_id'] = campaign_id

        if platform:
            conditions.append("platform = {platform:String}")
            params['platform'] = platform

        if start_date:
            conditions.append("date >= {start_date:Date}")
            params['start_date'] = start_date.date()

        if end_date:
            conditions.append("date <= {end_date:Date}")
            params['end_date'] = end_date.date()

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        query = f"""
            SELECT
                sum(impressions) as total_impressions,
                sum(clicks) as total_clicks,
                sum(cost) as total_cost,
                sum(conversions) as total_conversions,
                sum(revenue) as total_revenue
            FROM metrics_analytics
            WHERE {where_clause}
        """

        result = self.client.query(query, parameters=params)
        if result.result_rows:
            row = result.result_rows[0]
            return {
                'total_impressions': int(row[0]) if row[0] else 0,
                'total_clicks': int(row[1]) if row[1] else 0,
                'total_cost': Decimal(str(row[2])) if row[2] else Decimal('0'),
                'total_conversions': int(row[3]) if row[3] else 0,
                'total_revenue': Decimal(str(row[4])) if row[4] else Decimal('0'),
            }
        return {
            'total_impressions': 0,
            'total_clicks': 0,
            'total_cost': Decimal('0'),
            'total_conversions': 0,
            'total_revenue': Decimal('0'),
        }

    def get_time_series_metrics(
        self,
        campaign_id: Optional[str] = None,
        platform: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:
        """Get time series metrics grouped by date."""
        conditions = []
        params = {}

        if campaign_id:
            conditions.append("campaign_id = {campaign_id:String}")
            params['campaign_id'] = campaign_id

        if platform:
            conditions.append("platform = {platform:String}")
            params['platform'] = platform

        if start_date:
            conditions.append("date >= {start_date:Date}")
            params['start_date'] = start_date.date()

        if end_date:
            conditions.append("date <= {end_date:Date}")
            params['end_date'] = end_date.date()

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        query = f"""
            SELECT
                date,
                sum(impressions) as impressions,
                sum(clicks) as clicks,
                sum(cost) as cost,
                sum(conversions) as conversions,
                sum(revenue) as revenue
            FROM metrics_analytics
            WHERE {where_clause}
            GROUP BY date
            ORDER BY date
        """

        result = self.client.query(query, parameters=params)
        return [
            {
                'date': row[0],
                'impressions': int(row[1]) if row[1] else 0,
                'clicks': int(row[2]) if row[2] else 0,
                'cost': Decimal(str(row[3])) if row[3] else Decimal('0'),
                'conversions': int(row[4]) if row[4] else 0,
                'revenue': Decimal(str(row[5])) if row[5] else Decimal('0'),
            }
            for row in result.result_rows
        ]

    def get_campaign_performance(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """Get top performing campaigns by ROI."""
        conditions = []
        params = {}

        if start_date:
            conditions.append("date >= {start_date:Date}")
            params['start_date'] = start_date.date()

        if end_date:
            conditions.append("date <= {end_date:Date}")
            params['end_date'] = end_date.date()

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        query = f"""
            SELECT
                campaign_id,
                sum(impressions) as impressions,
                sum(clicks) as clicks,
                sum(cost) as cost,
                sum(conversions) as conversions,
                sum(revenue) as revenue
            FROM metrics_analytics
            WHERE {where_clause}
            GROUP BY campaign_id
            HAVING sum(cost) > 0
            ORDER BY (sum(revenue) - sum(cost)) / sum(cost) DESC
            LIMIT {{limit:UInt32}}
        """
        params['limit'] = limit

        result = self.client.query(query, parameters=params)
        campaigns = []
        for row in result.result_rows:
            cost = Decimal(str(row[2])) if row[2] else Decimal('0')
            revenue = Decimal(str(row[4])) if row[4] else Decimal('0')
            roi = ((revenue - cost) / cost * 100) if cost > 0 else Decimal('0')
            
            campaigns.append({
                'campaign_id': row[0],
                'impressions': int(row[1]) if row[1] else 0,
                'clicks': int(row[2]) if row[2] else 0,
                'cost': float(cost),
                'conversions': int(row[3]) if row[3] else 0,
                'revenue': float(revenue),
                'roi': float(roi),
            })
        
        return campaigns
