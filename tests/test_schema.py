"""Tests for schema loading and validation."""

import json
import tempfile
from pathlib import Path

import pytest
import polars as pl

from polarseal.schema import load_schema, _parse_schema, _create_constraint
from polarseal.constraints import (
    NullabilityConstraint,
    MaximumValueConstraint,
    MinimumValueConstraint,
    MedianConstraint,
    MeanConstraint,
    PercentileConstraint,
)


class TestSchemaLoading:
    """Tests for schema loading from JSON files."""

    def test_load_schema_from_file(self):
        """Test loading schema from a JSON file."""
        schema_data = {
            "fields": {
                "age": {
                    "type": "Int64",
                    "constraints": [
                        {
                            "type": "nullability",
                            "max_null_ratio": 0.1
                        },
                        {
                            "type": "maximum_value",
                            "max_value": 120
                        }
                    ]
                }
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(schema_data, f)
            temp_path = f.name
        
        try:
            validator = load_schema(temp_path)
            assert len(validator.constraints) == 2
            assert isinstance(validator.constraints[0], NullabilityConstraint)
            assert isinstance(validator.constraints[1], MaximumValueConstraint)
        finally:
            Path(temp_path).unlink()

    def test_load_schema_file_not_found(self):
        """Test loading schema from non-existent file."""
        with pytest.raises(FileNotFoundError):
            load_schema("/nonexistent/schema.json")

    def test_parse_schema_missing_fields_key(self):
        """Test parsing schema without fields key."""
        with pytest.raises(ValueError, match="must contain a 'fields' key"):
            _parse_schema({"other_key": []})

    def test_create_nullability_constraint(self):
        """Test creating nullability constraint from definition."""
        constraint_def = {
            "type": "nullability",
            "column": "age",
            "max_null_ratio": 0.1
        }
        
        constraint = _create_constraint(constraint_def)
        assert isinstance(constraint, NullabilityConstraint)
        assert constraint.column == "age"
        assert constraint.max_null_ratio == 0.1

    def test_create_maximum_value_constraint(self):
        """Test creating maximum value constraint from definition."""
        constraint_def = {
            "type": "maximum_value",
            "column": "age",
            "max_value": 120
        }
        
        constraint = _create_constraint(constraint_def)
        assert isinstance(constraint, MaximumValueConstraint)
        assert constraint.column == "age"
        assert constraint.max_value == 120

    def test_create_minimum_value_constraint(self):
        """Test creating minimum value constraint from definition."""
        constraint_def = {
            "type": "minimum_value",
            "column": "age",
            "min_value": 0
        }
        
        constraint = _create_constraint(constraint_def)
        assert isinstance(constraint, MinimumValueConstraint)
        assert constraint.column == "age"
        assert constraint.min_value == 0

    def test_create_median_constraint(self):
        """Test creating median constraint from definition."""
        constraint_def = {
            "type": "median",
            "column": "age",
            "lower_bound": 20,
            "upper_bound": 50
        }
        
        constraint = _create_constraint(constraint_def)
        assert isinstance(constraint, MedianConstraint)
        assert constraint.column == "age"
        assert constraint.lower_bound == 20
        assert constraint.upper_bound == 50

    def test_create_mean_constraint(self):
        """Test creating mean constraint from definition."""
        constraint_def = {
            "type": "mean",
            "column": "age",
            "lower_bound": 25,
            "upper_bound": 45
        }
        
        constraint = _create_constraint(constraint_def)
        assert isinstance(constraint, MeanConstraint)
        assert constraint.column == "age"
        assert constraint.lower_bound == 25
        assert constraint.upper_bound == 45

    def test_create_percentile_constraint(self):
        """Test creating percentile constraint from definition."""
        constraint_def = {
            "type": "percentile",
            "column": "age",
            "percentile": 0.95,
            "lower_bound": 70,
            "upper_bound": 100
        }
        
        constraint = _create_constraint(constraint_def)
        assert isinstance(constraint, PercentileConstraint)
        assert constraint.column == "age"
        assert constraint.percentile == 0.95
        assert constraint.lower_bound == 70
        assert constraint.upper_bound == 100

    def test_create_constraint_missing_type(self):
        """Test creating constraint without type."""
        with pytest.raises(ValueError, match="must contain a 'type' key"):
            _create_constraint({"column": "age"})

    def test_create_constraint_missing_column(self):
        """Test creating constraint without column."""
        with pytest.raises(ValueError, match="must contain a 'column' key"):
            _create_constraint({"type": "nullability"})

    def test_create_constraint_unknown_type(self):
        """Test creating constraint with unknown type."""
        with pytest.raises(ValueError, match="Unknown constraint type"):
            _create_constraint({
                "type": "unknown_type",
                "column": "age"
            })

    def test_create_maximum_value_missing_max_value(self):
        """Test creating maximum_value constraint without max_value."""
        with pytest.raises(ValueError, match="requires 'max_value' key"):
            _create_constraint({
                "type": "maximum_value",
                "column": "age"
            })

    def test_create_minimum_value_missing_min_value(self):
        """Test creating minimum_value constraint without min_value."""
        with pytest.raises(ValueError, match="requires 'min_value' key"):
            _create_constraint({
                "type": "minimum_value",
                "column": "age"
            })

    def test_create_percentile_missing_percentile(self):
        """Test creating percentile constraint without percentile."""
        with pytest.raises(ValueError, match="requires 'percentile' key"):
            _create_constraint({
                "type": "percentile",
                "column": "age",
                "upper_bound": 100
            })
