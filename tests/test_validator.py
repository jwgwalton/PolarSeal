"""Tests for SchemaValidator and ValidationResult."""

import pytest
import polars as pl

from polarseal.validator import SchemaValidator, ValidationResult
from polarseal.constraints import (
    NullabilityConstraint,
    MaximumValueConstraint,
    MinimumValueConstraint,
    MeanConstraint,
)


class TestValidationResult:
    """Tests for ValidationResult class."""

    def test_validation_result_all_passed(self):
        """Test validation result when all constraints pass."""
        results = [
            {"passed": True, "message": "OK", "details": {}},
            {"passed": True, "message": "OK", "details": {}},
        ]
        
        vr = ValidationResult(results)
        assert vr.passed is True
        assert bool(vr) is True
        assert len(vr.get_failures()) == 0

    def test_validation_result_some_failed(self):
        """Test validation result when some constraints fail."""
        results = [
            {"passed": True, "message": "OK", "details": {}},
            {"passed": False, "message": "Failed", "details": {}},
        ]
        
        vr = ValidationResult(results)
        assert vr.passed is False
        assert bool(vr) is False
        assert len(vr.get_failures()) == 1

    def test_validation_result_to_dict(self):
        """Test converting validation result to dictionary."""
        results = [
            {"passed": True, "message": "OK", "details": {}},
            {"passed": False, "message": "Failed", "details": {}},
        ]
        
        vr = ValidationResult(results)
        result_dict = vr.to_dict()
        
        assert result_dict["passed"] is False
        assert result_dict["total_constraints"] == 2
        assert result_dict["passed_constraints"] == 1
        assert result_dict["failed_constraints"] == 1
        assert len(result_dict["results"]) == 2

    def test_validation_result_summary(self):
        """Test getting summary of validation results."""
        results = [
            {"passed": True, "message": "OK", "details": {}, "constraint": "Test1"},
            {"passed": False, "message": "Failed", "details": {}, "constraint": "Test2"},
        ]
        
        vr = ValidationResult(results)
        summary = vr.summary()
        
        assert "FAILED" in summary
        assert "Total constraints: 2" in summary
        assert "Passed: 1" in summary
        assert "Failed: 1" in summary
        assert "Test2" in summary

    def test_validation_result_repr(self):
        """Test string representation of validation result."""
        results = [{"passed": True, "message": "OK", "details": {}}]
        
        vr = ValidationResult(results)
        repr_str = repr(vr)
        
        assert "PASSED" in repr_str
        assert "total=1" in repr_str


class TestSchemaValidator:
    """Tests for SchemaValidator class."""

    def test_validator_single_constraint_pass(self):
        """Test validator with single passing constraint."""
        df = pl.DataFrame({"age": [25, 30, 35, 40, 45]})
        
        constraints = [
            MaximumValueConstraint(column="age", max_value=50)
        ]
        
        validator = SchemaValidator(constraints)
        result = validator.validate(df)
        
        assert result.passed is True
        assert len(result.results) == 1

    def test_validator_single_constraint_fail(self):
        """Test validator with single failing constraint."""
        df = pl.DataFrame({"age": [25, 30, 35, 40, 55]})
        
        constraints = [
            MaximumValueConstraint(column="age", max_value=50)
        ]
        
        validator = SchemaValidator(constraints)
        result = validator.validate(df, raise_on_error=False)
        
        assert result.passed is False
        assert len(result.results) == 1
        assert len(result.get_failures()) == 1

    def test_validator_multiple_constraints_all_pass(self):
        """Test validator with multiple passing constraints."""
        df = pl.DataFrame({"age": [25, 30, 35, 40, 45]})
        
        constraints = [
            MaximumValueConstraint(column="age", max_value=50),
            MinimumValueConstraint(column="age", min_value=20),
            MeanConstraint(column="age", lower_bound=30, upper_bound=40),
        ]
        
        validator = SchemaValidator(constraints)
        result = validator.validate(df)
        
        assert result.passed is True
        assert len(result.results) == 3

    def test_validator_multiple_constraints_some_fail(self):
        """Test validator with some failing constraints."""
        df = pl.DataFrame({"age": [25, 30, 35, 40, 55]})
        
        constraints = [
            MaximumValueConstraint(column="age", max_value=50),  # Fails
            MinimumValueConstraint(column="age", min_value=20),  # Passes
            MeanConstraint(column="age", lower_bound=30, upper_bound=40),  # Passes
        ]
        
        validator = SchemaValidator(constraints)
        result = validator.validate(df, raise_on_error=False)
        
        assert result.passed is False
        assert len(result.results) == 3
        assert len(result.get_failures()) == 1

    def test_validator_with_nulls(self):
        """Test validator with dataframe containing nulls."""
        df = pl.DataFrame({"age": [25, None, 35, None, 45]})
        
        constraints = [
            NullabilityConstraint(column="age", max_null_ratio=0.5),
            MaximumValueConstraint(column="age", max_value=50),
        ]
        
        validator = SchemaValidator(constraints)
        result = validator.validate(df)
        
        assert result.passed is True

    def test_validator_constraint_info_added(self):
        """Test that constraint information is added to results."""
        df = pl.DataFrame({"age": [25, 30, 35]})
        
        constraints = [
            MaximumValueConstraint(column="age", max_value=50)
        ]
        
        validator = SchemaValidator(constraints)
        result = validator.validate(df)
        
        assert "constraint" in result.results[0]
        assert "MaximumValueConstraint" in result.results[0]["constraint"]
        assert "age" in result.results[0]["constraint"]
