"""
API views for InsightFlow.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiParameter
from typing import List, Dict, Any
from datetime import datetime
from decimal import Decimal

from core.services.ingestion_service import IngestionService
from core.services.analytics_service import AnalyticsService
from core.services.insight_service import InsightService
from analytics.anomalies import AnomalyDetector
from ingestion.tasks import ingest_marketing_data
from ingestion.adapters.csv_adapter import CSVAdapter
from core.domain.entities import MetricType


class DataIngestionView(APIView):
    """View for ingesting marketing data."""

    # Note: In production, use IsAuthenticated
    # For development, you can temporarily remove this or use AllowAny
    permission_classes = []  # Change to [IsAuthenticated] in production

    @extend_schema(
        summary="Ingest marketing data",
        description="Ingest marketing data asynchronously. Accepts JSON array or CSV file.",
        request={
            'application/json': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'campaign_id': {'type': 'string'},
                        'campaign_name': {'type': 'string'},
                        'platform': {'type': 'string'},
                        'ad_group_id': {'type': 'string'},
                        'ad_group_name': {'type': 'string'},
                        'ad_id': {'type': 'string'},
                        'ad_name': {'type': 'string'},
                        'date': {'type': 'string', 'format': 'date'},
                        'impressions': {'type': 'integer'},
                        'clicks': {'type': 'integer'},
                        'cost': {'type': 'number'},
                        'conversions': {'type': 'integer'},
                        'revenue': {'type': 'number'},
                    },
                },
            },
            'text/csv': {'type': 'string'},
        },
        responses={202: {'description': 'Data ingestion started'}},
    )
    def post(self, request):
        """Ingest marketing data (JSON or CSV)."""
        content_type = request.content_type or ''
        
        # Handle CSV upload
        if 'csv' in content_type or 'text/csv' in content_type:
            if hasattr(request, 'FILES') and 'file' in request.FILES:
                csv_file = request.FILES['file']
                csv_content = csv_file.read().decode('utf-8')
            elif hasattr(request, 'body'):
                csv_content = request.body.decode('utf-8')
            else:
                return Response(
                    {'error': 'CSV content required'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            
            try:
                adapter = CSVAdapter()
                data = adapter.parse(csv_content)
            except ValueError as e:
                return Response(
                    {'error': f'CSV parsing error: {str(e)}'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            # Handle JSON
            data = request.data
            if not isinstance(data, list):
                return Response(
                    {'error': 'Data must be a list of records'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # Validate required fields
        for record in data:
            if 'campaign_id' not in record or 'platform' not in record:
                return Response(
                    {'error': 'Each record must have campaign_id and platform'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # Queue async task
        task = ingest_marketing_data.delay(data)

        return Response(
            {
                'message': 'Data ingestion started',
                'task_id': task.id,
                'records_count': len(data),
            },
            status=status.HTTP_202_ACCEPTED,
        )


class ROIAnalyticsView(APIView):
    """View for ROI analytics."""

    permission_classes = []  # Change to [IsAuthenticated] in production

    @extend_schema(
        summary="Get ROI analytics",
        description="Calculate ROI and related metrics (CPC, CPA, CTR).",
        parameters=[
            OpenApiParameter('campaign_id', str, description='Filter by campaign ID'),
            OpenApiParameter('platform', str, description='Filter by platform'),
            OpenApiParameter('start_date', str, description='Start date (YYYY-MM-DD)'),
            OpenApiParameter('end_date', str, description='End date (YYYY-MM-DD)'),
        ],
        responses={200: {'description': 'Analytics results'}},
    )
    def get(self, request):
        """Get ROI analytics."""
        service = AnalyticsService()

        campaign_id = request.query_params.get('campaign_id')
        platform = request.query_params.get('platform')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        start = datetime.strptime(start_date, '%Y-%m-%d') if start_date else None
        end = datetime.strptime(end_date, '%Y-%m-%d') if end_date else None

        result = service.calculate_roi(
            campaign_id=campaign_id,
            platform=platform,
            start_date=start,
            end_date=end,
        )

        return Response({
            'roi': float(result.roi) if result.roi else None,
            'cpc': float(result.cpc) if result.cpc else None,
            'cpa': float(result.cpa) if result.cpa else None,
            'ctr': float(result.ctr) if result.ctr else None,
            'total_cost': float(result.total_cost),
            'total_revenue': float(result.total_revenue),
            'total_clicks': result.total_clicks,
            'total_impressions': result.total_impressions,
            'total_conversions': result.total_conversions,
            'campaign_id': result.campaign_id,
            'platform': result.platform,
        })


class TrendsAnalyticsView(APIView):
    """View for trends analytics."""

    permission_classes = []  # Change to [IsAuthenticated] in production

    @extend_schema(
        summary="Get trends analytics",
        description="Get time series trends data.",
        parameters=[
            OpenApiParameter('campaign_id', str, description='Filter by campaign ID'),
            OpenApiParameter('platform', str, description='Filter by platform'),
            OpenApiParameter('start_date', str, description='Start date (YYYY-MM-DD)'),
            OpenApiParameter('end_date', str, description='End date (YYYY-MM-DD)'),
            OpenApiParameter('days', int, description='Number of days (default: 30)'),
        ],
        responses={200: {'description': 'Trends data'}},
    )
    def get(self, request):
        """Get trends analytics."""
        service = AnalyticsService()

        campaign_id = request.query_params.get('campaign_id')
        platform = request.query_params.get('platform')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        days = int(request.query_params.get('days', 30))

        start = datetime.strptime(start_date, '%Y-%m-%d') if start_date else None
        end = datetime.strptime(end_date, '%Y-%m-%d') if end_date else None

        trends = service.get_trends(
            campaign_id=campaign_id,
            platform=platform,
            start_date=start,
            end_date=end,
            days=days,
        )

        # Convert dates to strings for JSON serialization
        for trend in trends:
            if isinstance(trend['date'], datetime):
                trend['date'] = trend['date'].strftime('%Y-%m-%d')
            elif hasattr(trend['date'], 'isoformat'):
                trend['date'] = trend['date'].isoformat()
            trend['cost'] = float(trend['cost'])
            trend['revenue'] = float(trend['revenue'])

        return Response(trends)


class AnomaliesAnalyticsView(APIView):
    """View for anomaly detection."""

    permission_classes = []  # Change to [IsAuthenticated] in production

    @extend_schema(
        summary="Get anomalies",
        description="Detect anomalies in metrics using Z-score.",
        parameters=[
            OpenApiParameter('metric_type', str, description='Metric type (impressions, clicks, cost, etc.)'),
            OpenApiParameter('entity_id', str, description='Entity ID (campaign, ad, etc.)'),
            OpenApiParameter('entity_type', str, description='Entity type (campaign, ad, adgroup)'),
            OpenApiParameter('lookback_days', int, description='Lookback days (default: 30)'),
        ],
        responses={200: {'description': 'Anomalies detected'}},
    )
    def get(self, request):
        """Get anomalies."""
        detector = AnomalyDetector()

        metric_type_str = request.query_params.get('metric_type', 'impressions')
        entity_id = request.query_params.get('entity_id')
        entity_type = request.query_params.get('entity_type', 'campaign')
        lookback_days = int(request.query_params.get('lookback_days', 30))

        if not entity_id:
            return Response(
                {'error': 'entity_id is required'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            metric_type = MetricType(metric_type_str)
        except ValueError:
            return Response(
                {'error': f'Invalid metric_type: {metric_type_str}'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        anomalies = detector.detect_anomalies(
            metric_type=metric_type,
            entity_id=entity_id,
            entity_type=entity_type,
            lookback_days=lookback_days,
        )

        return Response([
            {
                'metric_type': anomaly.metric_type.value,
                'entity_id': anomaly.entity_id,
                'entity_type': anomaly.entity_type,
                'date': anomaly.date.isoformat() if isinstance(anomaly.date, datetime) else str(anomaly.date),
                'value': float(anomaly.value),
                'expected_value': float(anomaly.expected_value),
                'z_score': float(anomaly.z_score),
                'severity': anomaly.severity,
                'description': anomaly.description,
            }
            for anomaly in anomalies
        ])


class InsightsSummaryView(APIView):
    """View for insights summary."""

    permission_classes = []  # Change to [IsAuthenticated] in production

    @extend_schema(
        summary="Get insights summary",
        description="Get generated marketing insights summary.",
        parameters=[
            OpenApiParameter('start_date', str, description='Start date (YYYY-MM-DD)'),
            OpenApiParameter('end_date', str, description='End date (YYYY-MM-DD)'),
            OpenApiParameter('limit', int, description='Limit results (default: 10)'),
        ],
        responses={200: {'description': 'Insights summary'}},
    )
    def get(self, request):
        """Get insights summary."""
        service = InsightService()

        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        limit = int(request.query_params.get('limit', 10))

        start = datetime.strptime(start_date, '%Y-%m-%d') if start_date else None
        end = datetime.strptime(end_date, '%Y-%m-%d') if end_date else None

        insights = service.generate_summary(
            start_date=start,
            end_date=end,
            limit=limit,
        )

        return Response([
            {
                'type': insight.type,
                'title': insight.title,
                'description': insight.description,
                'entity_id': insight.entity_id,
                'entity_type': insight.entity_type,
                'severity': insight.severity,
                'metadata': insight.metadata,
                'created_at': insight.created_at.isoformat() if insight.created_at else None,
            }
            for insight in insights
        ])
