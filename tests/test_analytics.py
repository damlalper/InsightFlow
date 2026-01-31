"""
Tests for analytics calculations.
"""
import pytest
from decimal import Decimal
from analytics.roi import (
    calculate_roi,
    calculate_cpc,
    calculate_cpa,
    calculate_ctr,
)


class TestROICalculations:
    """Tests for ROI calculations."""

    def test_calculate_roi(self):
        """Test ROI calculation."""
        roi = calculate_roi(Decimal('100'), Decimal('150'))
        assert roi == Decimal('50')  # (150-100)/100 * 100 = 50%

    def test_calculate_roi_zero_cost(self):
        """Test ROI with zero cost."""
        roi = calculate_roi(Decimal('0'), Decimal('150'))
        assert roi == Decimal('0')

    def test_calculate_cpc(self):
        """Test CPC calculation."""
        cpc = calculate_cpc(Decimal('100'), 50)
        assert cpc == Decimal('2')

    def test_calculate_cpa(self):
        """Test CPA calculation."""
        cpa = calculate_cpa(Decimal('100'), 10)
        assert cpa == Decimal('10')

    def test_calculate_ctr(self):
        """Test CTR calculation."""
        ctr = calculate_ctr(50, 1000)
        assert ctr == Decimal('5')
