"""Integration tests using example schemas."""

import json
import tempfile
from pathlib import Path

import pytest
import polars as pl

from polarseal import load_schema, SchemaValidator


class TestIntegrationWithSchemas:
    """Integration tests using JSON schemas."""

    def test_user_data_validation_pass(self):
        """Test validation of user data with passing constraints."""
        # Create sample user data
        df = pl.DataFrame({
            "user_id": [1, 2, 3, 4, 5],
            "age": [25, 30, 35, 40, 45],
            "score": [85.5, 90.2, 88.7, 92.1, 87.3],
        })
        
        # Define schema
        schema_data = {
            "constraints": [
                {
                    "type": "nullability",
                    "column": "user_id",
                    "max_null_ratio": 0.0
                },
                {
                    "type": "minimum_value",
                    "column": "age",
                    "min_value": 18
                },
                {
                    "type": "maximum_value",
                    "column": "age",
                    "max_value": 100
                },
                {
                    "type": "mean",
                    "column": "score",
                    "lower_bound": 80,
                    "upper_bound": 95
                },
                {
                    "type": "median",
                    "column": "score",
                    "lower_bound": 85,
                    "upper_bound": 93
                }
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(schema_data, f)
            temp_path = f.name
        
        try:
            constraints = load_schema(temp_path)
            validator = SchemaValidator(constraints)
            result = validator.validate(df)
            
            assert result.passed is True
            assert len(result.results) == 5
        finally:
            Path(temp_path).unlink()

    def test_sales_data_validation_fail(self):
        """Test validation of sales data with failing constraints."""
        # Create sample sales data with some issues
        df = pl.DataFrame({
            "sale_id": [1, 2, 3, None, 5],  # One null
            "amount": [100.5, 250.0, -50.0, 180.5, 320.0],  # One negative
            "discount": [0.1, 0.15, 0.2, 0.25, 0.9],  # One too high
        })
        
        # Define schema
        schema_data = {
            "constraints": [
                {
                    "type": "nullability",
                    "column": "sale_id",
                    "max_null_count": 0
                },
                {
                    "type": "minimum_value",
                    "column": "amount",
                    "min_value": 0
                },
                {
                    "type": "percentile",
                    "column": "discount",
                    "percentile": 0.95,
                    "upper_bound": 0.5
                }
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(schema_data, f)
            temp_path = f.name
        
        try:
            constraints = load_schema(temp_path)
            validator = SchemaValidator(constraints)
            result = validator.validate(df)
            
            assert result.passed is False
            failures = result.get_failures()
            assert len(failures) >= 2  # At least nullability and minimum value should fail
        finally:
            Path(temp_path).unlink()

    def test_sensor_data_validation(self):
        """Test validation of sensor data with percentile constraints."""
        # Create sample sensor data
        import random
        random.seed(42)
        
        temperatures = [random.gauss(25, 5) for _ in range(100)]
        
        df = pl.DataFrame({
            "timestamp": list(range(100)),
            "temperature": temperatures,
        })
        
        # Define schema with percentile constraints
        schema_data = {
            "constraints": [
                {
                    "type": "percentile",
                    "column": "temperature",
                    "percentile": 0.05,
                    "lower_bound": 10,
                    "upper_bound": 25
                },
                {
                    "type": "percentile",
                    "column": "temperature",
                    "percentile": 0.95,
                    "lower_bound": 25,
                    "upper_bound": 40
                },
                {
                    "type": "mean",
                    "column": "temperature",
                    "lower_bound": 20,
                    "upper_bound": 30
                }
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(schema_data, f)
            temp_path = f.name
        
        try:
            constraints = load_schema(temp_path)
            validator = SchemaValidator(constraints)
            result = validator.validate(df)
            
            # The result should pass with reasonable bounds
            assert result.passed is True
            assert len(result.results) == 3
        finally:
            Path(temp_path).unlink()

    def test_complex_validation_with_multiple_columns(self):
        """Test complex validation with multiple columns and constraints."""
        df = pl.DataFrame({
            "id": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            "value_a": [10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
            "value_b": [5.5, 6.2, 7.1, 8.0, 9.3, 10.1, 11.5, 12.2, 13.8, 14.5],
            "category": ["A", "B", "A", None, "B", "A", "B", "A", "B", "A"],
        })
        
        schema_data = {
            "constraints": [
                # ID constraints
                {
                    "type": "nullability",
                    "column": "id",
                    "max_null_ratio": 0.0
                },
                # Value A constraints
                {
                    "type": "minimum_value",
                    "column": "value_a",
                    "min_value": 0
                },
                {
                    "type": "maximum_value",
                    "column": "value_a",
                    "max_value": 100
                },
                {
                    "type": "median",
                    "column": "value_a",
                    "lower_bound": 40,
                    "upper_bound": 60
                },
                # Value B constraints
                {
                    "type": "mean",
                    "column": "value_b",
                    "lower_bound": 8,
                    "upper_bound": 12
                },
                {
                    "type": "percentile",
                    "column": "value_b",
                    "percentile": 0.25,
                    "lower_bound": 5,
                    "upper_bound": 8
                },
                # Category constraints
                {
                    "type": "nullability",
                    "column": "category",
                    "max_null_ratio": 0.2
                }
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(schema_data, f)
            temp_path = f.name
        
        try:
            constraints = load_schema(temp_path)
            validator = SchemaValidator(constraints)
            result = validator.validate(df)
            
            assert result.passed is True
            assert len(result.results) == 7
        finally:
            Path(temp_path).unlink()
