"""Tests for constraint classes."""

import pytest
import polars as pl

from polarseal.constraints import (
    NullabilityConstraint,
    MaximumValueConstraint,
    MinimumValueConstraint,
    MedianConstraint,
    MeanConstraint,
    PercentileConstraint,
)


class TestNullabilityConstraint:
    """Tests for NullabilityConstraint."""

    def test_nullability_ratio_pass(self):
        """Test that nullability constraint passes with acceptable ratio."""
        df = pl.DataFrame({
            "values": [1, 2, 3, None, 5, 6, 7, 8, 9, 10]  # 10% nulls
        })
        
        constraint = NullabilityConstraint(column="values", max_null_ratio=0.2)
        result = constraint.validate(df)
        
        assert result["passed"] is True
        assert result["details"]["null_ratio"] == 0.1
        assert result["details"]["null_count"] == 1

    def test_nullability_ratio_fail(self):
        """Test that nullability constraint fails with too many nulls."""
        df = pl.DataFrame({
            "values": [1, None, None, None, 5]  # 60% nulls
        })
        
        constraint = NullabilityConstraint(column="values", max_null_ratio=0.5)
        result = constraint.validate(df)
        
        assert result["passed"] is False
        assert result["details"]["null_ratio"] == 0.6
        assert "exceeds maximum" in result["message"]

    def test_nullability_count_pass(self):
        """Test that nullability constraint passes with acceptable count."""
        df = pl.DataFrame({
            "values": [1, 2, None, 4, 5]  # 1 null
        })
        
        constraint = NullabilityConstraint(column="values", max_null_count=2)
        result = constraint.validate(df)
        
        assert result["passed"] is True
        assert result["details"]["null_count"] == 1

    def test_nullability_count_fail(self):
        """Test that nullability constraint fails with too many nulls."""
        df = pl.DataFrame({
            "values": [1, None, None, None, 5]  # 3 nulls
        })
        
        constraint = NullabilityConstraint(column="values", max_null_count=2)
        result = constraint.validate(df)
        
        assert result["passed"] is False
        assert result["details"]["null_count"] == 3

    def test_nullability_both_constraints(self):
        """Test nullability with both ratio and count constraints."""
        df = pl.DataFrame({
            "values": [1, 2, None, 4, 5, 6, 7, 8, 9, 10]  # 1 null, 10% ratio
        })
        
        constraint = NullabilityConstraint(
            column="values",
            max_null_ratio=0.15,
            max_null_count=2
        )
        result = constraint.validate(df)
        
        assert result["passed"] is True

    def test_nullability_missing_column(self):
        """Test nullability constraint with missing column."""
        df = pl.DataFrame({"other": [1, 2, 3]})
        
        constraint = NullabilityConstraint(column="values", max_null_ratio=0.5)
        result = constraint.validate(df)
        
        assert result["passed"] is False
        assert "not found" in result["message"]

    def test_nullability_no_nulls(self):
        """Test nullability constraint with no null values."""
        df = pl.DataFrame({"values": [1, 2, 3, 4, 5]})
        
        constraint = NullabilityConstraint(column="values", max_null_ratio=0.0)
        result = constraint.validate(df)
        
        assert result["passed"] is True
        assert result["details"]["null_count"] == 0

    def test_nullability_requires_parameter(self):
        """Test that at least one parameter is required."""
        with pytest.raises(ValueError, match="Must specify either"):
            NullabilityConstraint(column="values")


class TestMaximumValueConstraint:
    """Tests for MaximumValueConstraint."""

    def test_maximum_value_pass(self):
        """Test that maximum value constraint passes."""
        df = pl.DataFrame({"values": [1, 2, 3, 4, 5]})
        
        constraint = MaximumValueConstraint(column="values", max_value=10)
        result = constraint.validate(df)
        
        assert result["passed"] is True
        assert result["details"]["actual_max"] == 5

    def test_maximum_value_fail(self):
        """Test that maximum value constraint fails."""
        df = pl.DataFrame({"values": [1, 2, 3, 4, 15]})
        
        constraint = MaximumValueConstraint(column="values", max_value=10)
        result = constraint.validate(df)
        
        assert result["passed"] is False
        assert result["details"]["actual_max"] == 15
        assert "exceeds limit" in result["message"]

    def test_maximum_value_exact_match(self):
        """Test maximum value constraint with exact match."""
        df = pl.DataFrame({"values": [1, 2, 3, 4, 10]})
        
        constraint = MaximumValueConstraint(column="values", max_value=10)
        result = constraint.validate(df)
        
        assert result["passed"] is True

    def test_maximum_value_with_nulls(self):
        """Test maximum value constraint with null values."""
        df = pl.DataFrame({"values": [1, 2, None, 4, 5]})
        
        constraint = MaximumValueConstraint(column="values", max_value=10)
        result = constraint.validate(df)
        
        assert result["passed"] is True
        assert result["details"]["actual_max"] == 5

    def test_maximum_value_all_nulls(self):
        """Test maximum value constraint with all null values."""
        df = pl.DataFrame({"values": [None, None, None]})
        
        constraint = MaximumValueConstraint(column="values", max_value=10)
        result = constraint.validate(df)
        
        assert result["passed"] is True
        assert result["details"]["actual_max"] is None


class TestMinimumValueConstraint:
    """Tests for MinimumValueConstraint."""

    def test_minimum_value_pass(self):
        """Test that minimum value constraint passes."""
        df = pl.DataFrame({"values": [5, 6, 7, 8, 9]})
        
        constraint = MinimumValueConstraint(column="values", min_value=1)
        result = constraint.validate(df)
        
        assert result["passed"] is True
        assert result["details"]["actual_min"] == 5

    def test_minimum_value_fail(self):
        """Test that minimum value constraint fails."""
        df = pl.DataFrame({"values": [-5, 1, 2, 3, 4]})
        
        constraint = MinimumValueConstraint(column="values", min_value=0)
        result = constraint.validate(df)
        
        assert result["passed"] is False
        assert result["details"]["actual_min"] == -5
        assert "below limit" in result["message"]

    def test_minimum_value_exact_match(self):
        """Test minimum value constraint with exact match."""
        df = pl.DataFrame({"values": [1, 2, 3, 4, 5]})
        
        constraint = MinimumValueConstraint(column="values", min_value=1)
        result = constraint.validate(df)
        
        assert result["passed"] is True

    def test_minimum_value_with_nulls(self):
        """Test minimum value constraint with null values."""
        df = pl.DataFrame({"values": [5, None, 6, 7, 8]})
        
        constraint = MinimumValueConstraint(column="values", min_value=1)
        result = constraint.validate(df)
        
        assert result["passed"] is True
        assert result["details"]["actual_min"] == 5


class TestMedianConstraint:
    """Tests for MedianConstraint."""

    def test_median_both_bounds_pass(self):
        """Test median constraint with both bounds passing."""
        df = pl.DataFrame({"values": [1, 2, 3, 4, 5]})  # median = 3
        
        constraint = MedianConstraint(column="values", lower_bound=2, upper_bound=4)
        result = constraint.validate(df)
        
        assert result["passed"] is True
        assert result["details"]["actual_median"] == 3

    def test_median_upper_bound_fail(self):
        """Test median constraint failing upper bound."""
        df = pl.DataFrame({"values": [10, 20, 30, 40, 50]})  # median = 30
        
        constraint = MedianConstraint(column="values", upper_bound=20)
        result = constraint.validate(df)
        
        assert result["passed"] is False
        assert "exceeds upper bound" in result["message"]

    def test_median_lower_bound_fail(self):
        """Test median constraint failing lower bound."""
        df = pl.DataFrame({"values": [1, 2, 3, 4, 5]})  # median = 3
        
        constraint = MedianConstraint(column="values", lower_bound=10)
        result = constraint.validate(df)
        
        assert result["passed"] is False
        assert "below lower bound" in result["message"]

    def test_median_only_upper_bound(self):
        """Test median constraint with only upper bound."""
        df = pl.DataFrame({"values": [1, 2, 3, 4, 5]})
        
        constraint = MedianConstraint(column="values", upper_bound=10)
        result = constraint.validate(df)
        
        assert result["passed"] is True

    def test_median_only_lower_bound(self):
        """Test median constraint with only lower bound."""
        df = pl.DataFrame({"values": [5, 6, 7, 8, 9]})
        
        constraint = MedianConstraint(column="values", lower_bound=1)
        result = constraint.validate(df)
        
        assert result["passed"] is True

    def test_median_requires_bound(self):
        """Test that at least one bound is required."""
        with pytest.raises(ValueError, match="Must specify at least one bound"):
            MedianConstraint(column="values")


class TestMeanConstraint:
    """Tests for MeanConstraint."""

    def test_mean_both_bounds_pass(self):
        """Test mean constraint with both bounds passing."""
        df = pl.DataFrame({"values": [1, 2, 3, 4, 5]})  # mean = 3
        
        constraint = MeanConstraint(column="values", lower_bound=2, upper_bound=4)
        result = constraint.validate(df)
        
        assert result["passed"] is True
        assert result["details"]["actual_mean"] == 3.0

    def test_mean_upper_bound_fail(self):
        """Test mean constraint failing upper bound."""
        df = pl.DataFrame({"values": [10, 20, 30, 40, 50]})  # mean = 30
        
        constraint = MeanConstraint(column="values", upper_bound=20)
        result = constraint.validate(df)
        
        assert result["passed"] is False
        assert "exceeds upper bound" in result["message"]

    def test_mean_lower_bound_fail(self):
        """Test mean constraint failing lower bound."""
        df = pl.DataFrame({"values": [1, 2, 3, 4, 5]})  # mean = 3
        
        constraint = MeanConstraint(column="values", lower_bound=10)
        result = constraint.validate(df)
        
        assert result["passed"] is False
        assert "below lower bound" in result["message"]

    def test_mean_with_nulls(self):
        """Test mean constraint with null values."""
        df = pl.DataFrame({"values": [1, 2, None, 4, 5]})  # mean = 3
        
        constraint = MeanConstraint(column="values", lower_bound=2, upper_bound=4)
        result = constraint.validate(df)
        
        assert result["passed"] is True

    def test_mean_requires_bound(self):
        """Test that at least one bound is required."""
        with pytest.raises(ValueError, match="Must specify at least one bound"):
            MeanConstraint(column="values")


class TestPercentileConstraint:
    """Tests for PercentileConstraint."""

    def test_percentile_50th_pass(self):
        """Test 50th percentile (median) constraint passing."""
        df = pl.DataFrame({"values": [1, 2, 3, 4, 5]})
        
        constraint = PercentileConstraint(
            column="values",
            percentile=0.5,
            lower_bound=2,
            upper_bound=4
        )
        result = constraint.validate(df)
        
        assert result["passed"] is True

    def test_percentile_90th_pass(self):
        """Test 90th percentile constraint passing."""
        df = pl.DataFrame({"values": list(range(1, 101))})  # 1-100
        
        # 90th percentile should be around 90
        constraint = PercentileConstraint(
            column="values",
            percentile=0.9,
            lower_bound=85,
            upper_bound=95
        )
        result = constraint.validate(df)
        
        assert result["passed"] is True

    def test_percentile_upper_bound_fail(self):
        """Test percentile constraint failing upper bound."""
        df = pl.DataFrame({"values": [1, 2, 3, 4, 5]})
        
        constraint = PercentileConstraint(
            column="values",
            percentile=0.75,
            upper_bound=3
        )
        result = constraint.validate(df)
        
        assert result["passed"] is False
        assert "exceeds upper bound" in result["message"]

    def test_percentile_lower_bound_fail(self):
        """Test percentile constraint failing lower bound."""
        df = pl.DataFrame({"values": [1, 2, 3, 4, 5]})
        
        constraint = PercentileConstraint(
            column="values",
            percentile=0.25,
            lower_bound=3
        )
        result = constraint.validate(df)
        
        assert result["passed"] is False
        assert "below lower bound" in result["message"]

    def test_percentile_25th(self):
        """Test 25th percentile constraint."""
        df = pl.DataFrame({"values": [1, 2, 3, 4, 5, 6, 7, 8]})
        
        constraint = PercentileConstraint(
            column="values",
            percentile=0.25,
            lower_bound=1,
            upper_bound=3
        )
        result = constraint.validate(df)
        
        assert result["passed"] is True

    def test_percentile_invalid_value(self):
        """Test that percentile must be between 0 and 1."""
        with pytest.raises(ValueError, match="must be between 0.0 and 1.0"):
            PercentileConstraint(
                column="values",
                percentile=1.5,
                upper_bound=10
            )

    def test_percentile_requires_bound(self):
        """Test that at least one bound is required."""
        with pytest.raises(ValueError, match="Must specify at least one bound"):
            PercentileConstraint(column="values", percentile=0.5)

    def test_percentile_0th(self):
        """Test 0th percentile (minimum) constraint."""
        df = pl.DataFrame({"values": [5, 10, 15, 20, 25]})
        
        constraint = PercentileConstraint(
            column="values",
            percentile=0.0,
            lower_bound=1,
            upper_bound=10
        )
        result = constraint.validate(df)
        
        assert result["passed"] is True

    def test_percentile_100th(self):
        """Test 100th percentile (maximum) constraint."""
        df = pl.DataFrame({"values": [5, 10, 15, 20, 25]})
        
        constraint = PercentileConstraint(
            column="values",
            percentile=1.0,
            lower_bound=20,
            upper_bound=30
        )
        result = constraint.validate(df)
        
        assert result["passed"] is True
