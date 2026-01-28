"""Tests for new field-based schema format and ValidationError."""

import json
import tempfile
from pathlib import Path

import pytest
import polars as pl

from polarseal import load_schema, ValidationError
from polarseal.validator import SchemaValidator


class TestFieldBasedSchema:
    """Tests for field-based schema format."""

    def test_load_field_based_schema(self):
        """Test loading a field-based schema."""
        schema_data = {
            "fields": {
                "user_id": {
                    "type": "Int64",
                    "constraints": []
                },
                "age": {
                    "type": "Int64",
                    "constraints": [
                        {"type": "minimum_value", "min_value": 0},
                        {"type": "maximum_value", "max_value": 120}
                    ]
                }
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(schema_data, f)
            temp_path = f.name
        
        try:
            validator = load_schema(temp_path)
            assert isinstance(validator, SchemaValidator)
            assert len(validator.constraints) == 2
            assert len(validator.field_definitions) == 2
            assert validator.field_definitions["user_id"] == "Int64"
            assert validator.field_definitions["age"] == "Int64"
        finally:
            Path(temp_path).unlink()

    def test_field_without_type_raises_error(self):
        """Test that field without type raises error."""
        schema_data = {
            "fields": {
                "user_id": {
                    "constraints": []
                }
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(schema_data, f)
            temp_path = f.name
        
        try:
            with pytest.raises(ValueError, match="must specify a 'type'"):
                load_schema(temp_path)
        finally:
            Path(temp_path).unlink()

    def test_field_with_empty_constraints(self):
        """Test field with empty constraints list."""
        schema_data = {
            "fields": {
                "user_id": {
                    "type": "Int64",
                    "constraints": []
                }
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(schema_data, f)
            temp_path = f.name
        
        try:
            validator = load_schema(temp_path)
            assert len(validator.constraints) == 0
            assert len(validator.field_definitions) == 1
        finally:
            Path(temp_path).unlink()

    def test_field_constraints_must_be_list(self):
        """Test that constraints must be a list."""
        schema_data = {
            "fields": {
                "user_id": {
                    "type": "Int64",
                    "constraints": "not a list"
                }
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(schema_data, f)
            temp_path = f.name
        
        try:
            with pytest.raises(ValueError, match="constraints must be a list"):
                load_schema(temp_path)
        finally:
            Path(temp_path).unlink()

    def test_schema_without_fields_or_constraints_raises_error(self):
        """Test that schema without fields or constraints raises error."""
        schema_data = {"other_key": "value"}
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(schema_data, f)
            temp_path = f.name
        
        try:
            with pytest.raises(ValueError, match="must contain either 'fields' or 'constraints'"):
                load_schema(temp_path)
        finally:
            Path(temp_path).unlink()


class TestValidationError:
    """Tests for ValidationError exception."""

    def test_validation_error_raised_on_type_mismatch(self):
        """Test that ValidationError is raised when field type doesn't match."""
        df = pl.DataFrame({
            "user_id": ["a", "b", "c"],  # String instead of Int64
        })
        
        schema_data = {
            "fields": {
                "user_id": {
                    "type": "Int64",
                    "constraints": []
                }
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(schema_data, f)
            temp_path = f.name
        
        try:
            validator = load_schema(temp_path)
            with pytest.raises(ValidationError) as exc_info:
                validator.validate(df)
            
            assert "type error" in str(exc_info.value).lower()
            assert len(exc_info.value.failures) > 0
        finally:
            Path(temp_path).unlink()

    def test_validation_error_raised_on_missing_field(self):
        """Test that ValidationError is raised when required field is missing."""
        df = pl.DataFrame({
            "other_field": [1, 2, 3]
        })
        
        schema_data = {
            "fields": {
                "user_id": {
                    "type": "Int64",
                    "constraints": []
                }
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(schema_data, f)
            temp_path = f.name
        
        try:
            validator = load_schema(temp_path)
            with pytest.raises(ValidationError) as exc_info:
                validator.validate(df)
            
            assert "not found" in str(exc_info.value).lower()
        finally:
            Path(temp_path).unlink()

    def test_validation_error_raised_on_constraint_failure(self):
        """Test that ValidationError is raised when constraint fails."""
        df = pl.DataFrame({
            "age": [150, 200, 250]  # Values exceed maximum
        })
        
        schema_data = {
            "fields": {
                "age": {
                    "type": "Int64",
                    "constraints": [
                        {"type": "maximum_value", "max_value": 120}
                    ]
                }
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(schema_data, f)
            temp_path = f.name
        
        try:
            validator = load_schema(temp_path)
            with pytest.raises(ValidationError) as exc_info:
                validator.validate(df)
            
            assert "constraint" in str(exc_info.value).lower()
            assert len(exc_info.value.failures) > 0
        finally:
            Path(temp_path).unlink()

    def test_validation_passes_with_correct_data(self):
        """Test that validation passes with correct data."""
        df = pl.DataFrame({
            "user_id": [1, 2, 3],
            "age": [25, 30, 35]
        })
        
        schema_data = {
            "fields": {
                "user_id": {
                    "type": "Int64",
                    "constraints": []
                },
                "age": {
                    "type": "Int64",
                    "constraints": [
                        {"type": "minimum_value", "min_value": 0},
                        {"type": "maximum_value", "max_value": 120}
                    ]
                }
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(schema_data, f)
            temp_path = f.name
        
        try:
            validator = load_schema(temp_path)
            # Should not raise any exception
            result = validator.validate(df)
            assert result.passed
        finally:
            Path(temp_path).unlink()

    def test_validation_error_includes_failure_details(self):
        """Test that ValidationError includes detailed failure information."""
        df = pl.DataFrame({
            "age": [150]
        })
        
        schema_data = {
            "fields": {
                "age": {
                    "type": "Int64",
                    "constraints": [
                        {"type": "maximum_value", "max_value": 120}
                    ]
                }
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(schema_data, f)
            temp_path = f.name
        
        try:
            validator = load_schema(temp_path)
            with pytest.raises(ValidationError) as exc_info:
                validator.validate(df)
            
            error_str = str(exc_info.value)
            assert "Failed constraints:" in error_str
            assert "MaximumValueConstraint" in error_str
        finally:
            Path(temp_path).unlink()

    def test_legacy_behavior_with_raise_on_error_false(self):
        """Test that raise_on_error=False provides legacy behavior."""
        df = pl.DataFrame({
            "age": [150]
        })
        
        schema_data = {
            "fields": {
                "age": {
                    "type": "Int64",
                    "constraints": [
                        {"type": "maximum_value", "max_value": 120}
                    ]
                }
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(schema_data, f)
            temp_path = f.name
        
        try:
            validator = load_schema(temp_path)
            # Should not raise, but return a failed ValidationResult
            result = validator.validate(df, raise_on_error=False)
            assert not result.passed
            assert len(result.get_failures()) > 0
        finally:
            Path(temp_path).unlink()


class TestTypeMatching:
    """Tests for type matching functionality."""

    def test_exact_type_match(self):
        """Test exact type matching."""
        df = pl.DataFrame({
            "value": pl.Series([1, 2, 3], dtype=pl.Int64)
        })
        
        schema_data = {
            "fields": {
                "value": {
                    "type": "Int64",
                    "constraints": []
                }
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(schema_data, f)
            temp_path = f.name
        
        try:
            validator = load_schema(temp_path)
            result = validator.validate(df)
            assert result.passed
        finally:
            Path(temp_path).unlink()

    def test_string_type_alias(self):
        """Test string type alias matching."""
        df = pl.DataFrame({
            "name": ["Alice", "Bob", "Charlie"]
        })
        
        # Polars uses "String" or "Utf8" internally
        schema_data = {
            "fields": {
                "name": {
                    "type": "String",
                    "constraints": []
                }
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(schema_data, f)
            temp_path = f.name
        
        try:
            validator = load_schema(temp_path)
            result = validator.validate(df)
            assert result.passed
        finally:
            Path(temp_path).unlink()

    def test_float_type_match(self):
        """Test float type matching."""
        df = pl.DataFrame({
            "score": pl.Series([1.5, 2.7, 3.2], dtype=pl.Float64)
        })
        
        schema_data = {
            "fields": {
                "score": {
                    "type": "Float64",
                    "constraints": []
                }
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(schema_data, f)
            temp_path = f.name
        
        try:
            validator = load_schema(temp_path)
            result = validator.validate(df)
            assert result.passed
        finally:
            Path(temp_path).unlink()


class TestBackwardCompatibility:
    """Tests for backward compatibility with old schema format."""

    def test_old_format_still_works(self):
        """Test that old constraint-based format still works."""
        schema_data = {
            "constraints": [
                {
                    "type": "maximum_value",
                    "column": "age",
                    "max_value": 120
                }
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(schema_data, f)
            temp_path = f.name
        
        try:
            validator = load_schema(temp_path)
            assert isinstance(validator, SchemaValidator)
            assert len(validator.constraints) == 1
            # Old format doesn't have field definitions
            assert len(validator.field_definitions) == 0
        finally:
            Path(temp_path).unlink()

    def test_old_format_with_valid_data(self):
        """Test old format validation with valid data."""
        df = pl.DataFrame({
            "age": [25, 30, 35]
        })
        
        schema_data = {
            "constraints": [
                {
                    "type": "maximum_value",
                    "column": "age",
                    "max_value": 120
                }
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(schema_data, f)
            temp_path = f.name
        
        try:
            validator = load_schema(temp_path)
            # With old format, should still raise on error by default
            result = validator.validate(df)
            assert result.passed
        finally:
            Path(temp_path).unlink()
