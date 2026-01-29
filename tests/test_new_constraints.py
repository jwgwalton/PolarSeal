"""Tests for new constraint classes."""

import pytest
import polars as pl

from polarseal.constraints import (
    UniquenessConstraint,
    StandardDeviationConstraint,
    StringLengthConstraint,
    RegexPatternConstraint,
    ValueSetConstraint,
    RowCountConstraint,
)


class TestUniquenessConstraint:
    """Tests for UniquenessConstraint."""

    def test_uniqueness_ratio_pass(self):
        """Test that uniqueness constraint passes with acceptable ratio."""
        df = pl.DataFrame({
            "values": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]  # 100% unique
        })
        
        constraint = UniquenessConstraint(column="values", min_unique_ratio=0.8)
        result = constraint.validate(df)
        
        assert result["passed"] is True
        assert result["details"]["unique_ratio"] == 1.0
        assert result["details"]["unique_count"] == 10

    def test_uniqueness_ratio_fail(self):
        """Test that uniqueness constraint fails with too few unique values."""
        df = pl.DataFrame({
            "values": [1, 1, 1, 2, 2]  # 40% unique
        })
        
        constraint = UniquenessConstraint(column="values", min_unique_ratio=0.5)
        result = constraint.validate(df)
        
        assert result["passed"] is False
        assert result["details"]["unique_ratio"] == 0.4
        assert "below minimum" in result["message"]

    def test_uniqueness_count_pass(self):
        """Test that uniqueness constraint passes with acceptable count."""
        df = pl.DataFrame({
            "values": [1, 2, 3, 4, 5, 1, 2]  # 5 unique
        })
        
        constraint = UniquenessConstraint(column="values", min_unique_count=4)
        result = constraint.validate(df)
        
        assert result["passed"] is True
        assert result["details"]["unique_count"] == 5

    def test_uniqueness_count_fail(self):
        """Test that uniqueness constraint fails with too few unique values."""
        df = pl.DataFrame({
            "values": [1, 1, 1, 2, 2]  # 2 unique
        })
        
        constraint = UniquenessConstraint(column="values", min_unique_count=5)
        result = constraint.validate(df)
        
        assert result["passed"] is False
        assert result["details"]["unique_count"] == 2

    def test_uniqueness_with_nulls(self):
        """Test uniqueness constraint with null values."""
        df = pl.DataFrame({
            "values": [1, 2, 3, None, None]  # 4 unique (including null)
        })
        
        constraint = UniquenessConstraint(column="values", min_unique_count=3)
        result = constraint.validate(df)
        
        assert result["passed"] is True

    def test_uniqueness_requires_parameter(self):
        """Test that at least one parameter is required."""
        with pytest.raises(ValueError, match="Must specify either"):
            UniquenessConstraint(column="values")


class TestStandardDeviationConstraint:
    """Tests for StandardDeviationConstraint."""

    def test_std_both_bounds_pass(self):
        """Test standard deviation constraint with both bounds passing."""
        df = pl.DataFrame({"values": [1, 2, 3, 4, 5]})  # std ≈ 1.58
        
        constraint = StandardDeviationConstraint(column="values", lower_bound=1.0, upper_bound=2.0)
        result = constraint.validate(df)
        
        assert result["passed"] is True

    def test_std_upper_bound_fail(self):
        """Test standard deviation constraint failing upper bound."""
        df = pl.DataFrame({"values": [1, 100, 200, 300, 400]})  # high std
        
        constraint = StandardDeviationConstraint(column="values", upper_bound=50)
        result = constraint.validate(df)
        
        assert result["passed"] is False
        assert "exceeds upper bound" in result["message"]

    def test_std_lower_bound_fail(self):
        """Test standard deviation constraint failing lower bound."""
        df = pl.DataFrame({"values": [10, 10, 10, 10, 10]})  # std = 0
        
        constraint = StandardDeviationConstraint(column="values", lower_bound=1.0)
        result = constraint.validate(df)
        
        assert result["passed"] is False
        assert "below lower bound" in result["message"]

    def test_std_with_nulls(self):
        """Test standard deviation constraint with null values."""
        df = pl.DataFrame({"values": [1, 2, 3, None, 5]})
        
        constraint = StandardDeviationConstraint(column="values", lower_bound=0.5, upper_bound=5.0)
        result = constraint.validate(df)
        
        assert result["passed"] is True

    def test_std_all_nulls(self):
        """Test standard deviation constraint with all null values."""
        df = pl.DataFrame({"values": [None, None, None]})
        
        constraint = StandardDeviationConstraint(column="values", upper_bound=10)
        result = constraint.validate(df)
        
        assert result["passed"] is True
        assert result["details"]["actual_std"] is None

    def test_std_requires_parameter(self):
        """Test that at least one parameter is required."""
        with pytest.raises(ValueError, match="Must specify at least one bound"):
            StandardDeviationConstraint(column="values")


class TestStringLengthConstraint:
    """Tests for StringLengthConstraint."""

    def test_string_length_both_bounds_pass(self):
        """Test string length constraint with both bounds passing."""
        df = pl.DataFrame({
            "values": ["abc", "defg", "hi"]  # lengths: 3, 4, 2
        })
        
        constraint = StringLengthConstraint(column="values", min_length=2, max_length=5)
        result = constraint.validate(df)
        
        assert result["passed"] is True
        assert result["details"]["min_length_found"] == 2
        assert result["details"]["max_length_found"] == 4

    def test_string_length_min_fail(self):
        """Test string length constraint failing minimum."""
        df = pl.DataFrame({
            "values": ["a", "abc", "defgh"]  # min length: 1
        })
        
        constraint = StringLengthConstraint(column="values", min_length=2)
        result = constraint.validate(df)
        
        assert result["passed"] is False
        assert "below required minimum" in result["message"]

    def test_string_length_max_fail(self):
        """Test string length constraint failing maximum."""
        df = pl.DataFrame({
            "values": ["ab", "abc", "verylongstring"]
        })
        
        constraint = StringLengthConstraint(column="values", max_length=5)
        result = constraint.validate(df)
        
        assert result["passed"] is False
        assert "exceeds allowed maximum" in result["message"]

    def test_string_length_with_nulls(self):
        """Test string length constraint with null values."""
        df = pl.DataFrame({
            "values": ["abc", None, "defg"]
        })
        
        constraint = StringLengthConstraint(column="values", min_length=2, max_length=5)
        result = constraint.validate(df)
        
        assert result["passed"] is True

    def test_string_length_all_nulls(self):
        """Test string length constraint with all null values."""
        df = pl.DataFrame({"values": [None, None, None]})
        
        constraint = StringLengthConstraint(column="values", max_length=10)
        result = constraint.validate(df)
        
        assert result["passed"] is True
        assert result["details"]["min_length_found"] is None

    def test_string_length_requires_parameter(self):
        """Test that at least one parameter is required."""
        with pytest.raises(ValueError, match="Must specify at least one"):
            StringLengthConstraint(column="values")


class TestRegexPatternConstraint:
    """Tests for RegexPatternConstraint."""

    def test_regex_pattern_pass(self):
        """Test regex pattern constraint passing."""
        df = pl.DataFrame({
            "emails": ["user@example.com", "test@test.org", "admin@site.net"]
        })
        
        # Simple email pattern
        constraint = RegexPatternConstraint(column="emails", pattern=r"@")
        result = constraint.validate(df)
        
        assert result["passed"] is True
        assert result["details"]["mismatch_count"] == 0

    def test_regex_pattern_fail(self):
        """Test regex pattern constraint failing."""
        df = pl.DataFrame({
            "emails": ["user@example.com", "invalid", "test@test.org"]
        })
        
        constraint = RegexPatternConstraint(column="emails", pattern=r"@")
        result = constraint.validate(df)
        
        assert result["passed"] is False
        assert result["details"]["mismatch_count"] == 1
        assert "do not match pattern" in result["message"]

    def test_regex_pattern_with_nulls(self):
        """Test regex pattern constraint with null values."""
        df = pl.DataFrame({
            "emails": ["user@example.com", None, "test@test.org"]
        })
        
        constraint = RegexPatternConstraint(column="emails", pattern=r"@")
        result = constraint.validate(df)
        
        # Nulls are treated as matching (fill_null(True))
        assert result["passed"] is True

    def test_regex_pattern_digits(self):
        """Test regex pattern for digits."""
        df = pl.DataFrame({
            "codes": ["ABC123", "DEF456", "GHI789"]
        })
        
        constraint = RegexPatternConstraint(column="codes", pattern=r"\d")
        result = constraint.validate(df)
        
        assert result["passed"] is True


class TestValueSetConstraint:
    """Tests for ValueSetConstraint."""

    def test_value_set_pass(self):
        """Test value set constraint passing."""
        df = pl.DataFrame({
            "status": ["active", "inactive", "active", "pending"]
        })
        
        constraint = ValueSetConstraint(
            column="status",
            allowed_values=["active", "inactive", "pending"]
        )
        result = constraint.validate(df)
        
        assert result["passed"] is True
        assert result["details"]["invalid_count"] == 0

    def test_value_set_fail(self):
        """Test value set constraint failing."""
        df = pl.DataFrame({
            "status": ["active", "invalid", "pending"]
        })
        
        constraint = ValueSetConstraint(
            column="status",
            allowed_values=["active", "inactive", "pending"]
        )
        result = constraint.validate(df)
        
        assert result["passed"] is False
        assert result["details"]["invalid_count"] == 1
        assert "not in allowed set" in result["message"]

    def test_value_set_numeric(self):
        """Test value set constraint with numeric values."""
        df = pl.DataFrame({
            "priority": [1, 2, 3, 1, 2]
        })
        
        constraint = ValueSetConstraint(
            column="priority",
            allowed_values=[1, 2, 3, 4, 5]
        )
        result = constraint.validate(df)
        
        assert result["passed"] is True

    def test_value_set_with_nulls(self):
        """Test value set constraint with null values."""
        df = pl.DataFrame({
            "status": ["active", None, "pending"]
        })
        
        constraint = ValueSetConstraint(
            column="status",
            allowed_values=["active", "inactive", "pending"]
        )
        result = constraint.validate(df)
        
        # Nulls are treated as valid (fill_null(True))
        assert result["passed"] is True

    def test_value_set_empty_list_error(self):
        """Test value set constraint with empty allowed values."""
        with pytest.raises(ValueError, match="must contain at least one value"):
            ValueSetConstraint(column="status", allowed_values=[])


class TestRowCountConstraint:
    """Tests for RowCountConstraint."""

    def test_row_count_both_bounds_pass(self):
        """Test row count constraint with both bounds passing."""
        df = pl.DataFrame({
            "values": [1, 2, 3, 4, 5]  # 5 rows
        })
        
        constraint = RowCountConstraint(column="", min_rows=3, max_rows=10)
        result = constraint.validate(df)
        
        assert result["passed"] is True
        assert result["details"]["row_count"] == 5

    def test_row_count_min_fail(self):
        """Test row count constraint failing minimum."""
        df = pl.DataFrame({
            "values": [1, 2]  # 2 rows
        })
        
        constraint = RowCountConstraint(column="", min_rows=5)
        result = constraint.validate(df)
        
        assert result["passed"] is False
        assert "below minimum" in result["message"]

    def test_row_count_max_fail(self):
        """Test row count constraint failing maximum."""
        df = pl.DataFrame({
            "values": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]  # 10 rows
        })
        
        constraint = RowCountConstraint(column="", max_rows=5)
        result = constraint.validate(df)
        
        assert result["passed"] is False
        assert "exceeds maximum" in result["message"]

    def test_row_count_exact(self):
        """Test row count constraint with exact bounds."""
        df = pl.DataFrame({
            "values": [1, 2, 3, 4, 5]
        })
        
        constraint = RowCountConstraint(column="", min_rows=5, max_rows=5)
        result = constraint.validate(df)
        
        assert result["passed"] is True

    def test_row_count_empty_dataframe(self):
        """Test row count constraint with empty dataframe."""
        df = pl.DataFrame({"values": []})
        
        constraint = RowCountConstraint(column="", min_rows=0, max_rows=10)
        result = constraint.validate(df)
        
        assert result["passed"] is True
        assert result["details"]["row_count"] == 0

    def test_row_count_requires_parameter(self):
        """Test that at least one parameter is required."""
        with pytest.raises(ValueError, match="Must specify at least one"):
            RowCountConstraint(column="")
