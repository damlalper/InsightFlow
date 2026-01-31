"""
ROI and related metric calculations.
"""
from decimal import Decimal
from core.domain.entities import AnalyticsResult


def calculate_roi(cost: Decimal, revenue: Decimal) -> Decimal:
    """
    Calculate ROI: (Revenue - Cost) / Cost * 100.
    
    Args:
        cost: Total cost
        revenue: Total revenue
        
    Returns:
        ROI percentage
    """
    if cost == 0:
        return Decimal('0')
    return ((revenue - cost) / cost) * 100


def calculate_cpc(cost: Decimal, clicks: int) -> Decimal:
    """
    Calculate Cost Per Click: Cost / Clicks.
    
    Args:
        cost: Total cost
        clicks: Total clicks
        
    Returns:
        Cost per click
    """
    if clicks == 0:
        return Decimal('0')
    return cost / Decimal(clicks)


def calculate_cpa(cost: Decimal, conversions: int) -> Decimal:
    """
    Calculate Cost Per Acquisition: Cost / Conversions.
    
    Args:
        cost: Total cost
        conversions: Total conversions
        
    Returns:
        Cost per acquisition
    """
    if conversions == 0:
        return Decimal('0')
    return cost / Decimal(conversions)


def calculate_ctr(clicks: int, impressions: int) -> Decimal:
    """
    Calculate Click-Through Rate: (Clicks / Impressions) * 100.
    
    Args:
        clicks: Total clicks
        impressions: Total impressions
        
    Returns:
        CTR percentage
    """
    if impressions == 0:
        return Decimal('0')
    return (Decimal(clicks) / Decimal(impressions)) * 100


def calculate_all_metrics(result: AnalyticsResult) -> AnalyticsResult:
    """
    Calculate all analytics metrics for a result.
    
    Args:
        result: AnalyticsResult with raw data
        
    Returns:
        AnalyticsResult with calculated metrics
    """
    result.roi = calculate_roi(result.total_cost, result.total_revenue)
    result.cpc = calculate_cpc(result.total_cost, result.total_clicks)
    result.cpa = calculate_cpa(result.total_cost, result.total_conversions)
    result.ctr = calculate_ctr(result.total_clicks, result.total_impressions)
    return result
