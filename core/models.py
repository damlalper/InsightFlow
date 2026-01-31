"""
Django ORM models - Infrastructure layer.
"""
from django.db import models
from django.utils import timezone
from decimal import Decimal


class Campaign(models.Model):
    """Campaign model."""
    id = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255)
    platform = models.CharField(max_length=100)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    budget = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=50, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'campaigns'
        indexes = [
            models.Index(fields=['platform', 'status']),
            models.Index(fields=['start_date', 'end_date']),
        ]

    def __str__(self):
        return f"{self.name} ({self.platform})"


class AdGroup(models.Model):
    """AdGroup model."""
    id = models.CharField(max_length=255, primary_key=True)
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='ad_groups')
    name = models.CharField(max_length=255)
    status = models.CharField(max_length=50, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'ad_groups'
        indexes = [
            models.Index(fields=['campaign', 'status']),
        ]

    def __str__(self):
        return f"{self.name} (Campaign: {self.campaign.name})"


class Ad(models.Model):
    """Ad model."""
    id = models.CharField(max_length=255, primary_key=True)
    ad_group = models.ForeignKey(AdGroup, on_delete=models.CASCADE, related_name='ads')
    name = models.CharField(max_length=255)
    creative_url = models.URLField(null=True, blank=True)
    status = models.CharField(max_length=50, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'ads'
        indexes = [
            models.Index(fields=['ad_group', 'status']),
        ]

    def __str__(self):
        return f"{self.name} (AdGroup: {self.ad_group.name})"


class Metric(models.Model):
    """Metric model for PostgreSQL (transactional data)."""
    METRIC_TYPES = [
        ('impressions', 'Impressions'),
        ('clicks', 'Clicks'),
        ('cost', 'Cost'),
        ('conversions', 'Conversions'),
        ('revenue', 'Revenue'),
    ]

    id = models.AutoField(primary_key=True)
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='metrics')
    ad_group = models.ForeignKey(AdGroup, on_delete=models.CASCADE, null=True, blank=True, related_name='metrics')
    ad = models.ForeignKey(Ad, on_delete=models.CASCADE, null=True, blank=True, related_name='metrics')
    date = models.DateField()
    metric_type = models.CharField(max_length=50, choices=METRIC_TYPES)
    value = models.DecimalField(max_digits=15, decimal_places=2)
    platform = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'metrics'
        indexes = [
            models.Index(fields=['campaign', 'date', 'metric_type']),
            models.Index(fields=['date', 'platform']),
            models.Index(fields=['ad_group', 'date']),
            models.Index(fields=['ad', 'date']),
        ]
        unique_together = [['campaign', 'ad_group', 'ad', 'date', 'metric_type', 'platform']]

    def __str__(self):
        return f"{self.metric_type}: {self.value} ({self.date})"


class Insight(models.Model):
    """Insight model."""
    INSIGHT_TYPES = [
        ('best_campaign', 'Best Performing Campaign'),
        ('underperforming_ad', 'Underperforming Ad'),
        ('budget_inefficiency', 'Budget Inefficiency'),
        ('anomaly_detected', 'Anomaly Detected'),
    ]

    SEVERITY_LEVELS = [
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('critical', 'Critical'),
    ]

    id = models.AutoField(primary_key=True)
    type = models.CharField(max_length=100, choices=INSIGHT_TYPES)
    title = models.CharField(max_length=255)
    description = models.TextField()
    entity_id = models.CharField(max_length=255)
    entity_type = models.CharField(max_length=50)  # campaign, ad, adgroup
    severity = models.CharField(max_length=20, choices=SEVERITY_LEVELS, default='info')
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'insights'
        indexes = [
            models.Index(fields=['type', 'severity']),
            models.Index(fields=['entity_type', 'entity_id']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.type})"
