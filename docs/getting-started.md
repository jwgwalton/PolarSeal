# Getting Started with PolarSeal

This guide will help you get started with PolarSeal, a powerful data validation library built on Polars.

## Installation

### From PyPI

```bash
pip install polarseal
```

### For Development

```bash
git clone https://github.com/jwgwalton/PolarSeal.git
cd PolarSeal
pip install -e ".[dev]"
```

## Quick Start

### 1. Using JSON Schemas (Recommended)

Create a schema file (`schema.json`):

```json
{
  "fields": {
    "user_id": {
      "type": "Int64",
      "constraints": [
        {
          "type": "nullability",
          "max_null_ratio": 0.0
        }
      ]
    },
    "age": {
      "type": "Int64",
      "constraints": [
        {
          "type": "minimum_value",
          "min_value": 0
        },
        {
          "type": "maximum_value",
          "max_value": 120
        }
      ]
    }
  }
}
```

Validate your DataFrame:

```python
import polars as pl
from polarseal import load_schema, ValidationError

# Create your DataFrame
df = pl.DataFrame({
    "user_id": [1, 2, 3, 4, 5],
    "age": [25, 32, 28, 45, 38],
})

# Load schema and validate
try:
    validator = load_schema("schema.json")
    result = validator.validate(df)
    print("✓ Validation passed!")
except ValidationError as e:
    print(f"✗ Validation failed: {e}")
    for failure in e.failures:
        print(f"  - {failure['constraint']}: {failure['message']}")
```

### 2. Programmatic Constraints

You can also create constraints programmatically:

```python
import polars as pl
from polarseal import (
    SchemaValidator,
    ValidationError,
    NullabilityConstraint,
    MaximumValueConstraint,
    MinimumValueConstraint,
    MeanConstraint,
)

df = pl.DataFrame({
    "temperature": [20.5, 21.3, 19.8, 22.1, 20.9],
})

# Define constraints programmatically
constraints = [
    NullabilityConstraint(column="temperature", max_null_ratio=0.05),
    MinimumValueConstraint(column="temperature", min_value=15.0),
    MaximumValueConstraint(column="temperature", max_value=30.0),
    MeanConstraint(column="temperature", lower_bound=19.0, upper_bound=23.0),
]

# Optionally specify field types
field_definitions = {
    "temperature": "Float64"
}

# Validate
validator = SchemaValidator(constraints, field_definitions)
try:
    result = validator.validate(df)
    print("✓ All validations passed!")
except ValidationError as e:
    print(f"✗ Validation failed: {e}")
```

## Supported Data Types

PolarSeal supports the following Polars data types:

- **Integers**: `Int8`, `Int16`, `Int32`, `Int64`, `UInt8`, `UInt16`, `UInt32`, `UInt64`
- **Floats**: `Float32`, `Float64`
- **Strings**: `String`, `Utf8`
- **Boolean**: `Boolean`, `Bool`

Type matching includes exact matches and alias support (e.g., `String` matches `Utf8`).

## Schema Format

### Field-Based Schema

The field-based schema format allows you to define each field with its type and an optional list of constraints:

```json
{
  "fields": {
    "field_name": {
      "type": "DataType",
      "constraints": [
        // List of constraints (can be empty)
      ]
    }
  }
}
```

### Type-Only Validation

You can validate types without additional constraints by using an empty constraints list:

```json
{
  "fields": {
    "id": {
      "type": "Int64",
      "constraints": []
    },
    "name": {
      "type": "String",
      "constraints": []
    }
  }
}
```

This validates that the DataFrame has the correct columns with the correct types, without any additional constraints.

## Available Constraints

PolarSeal provides 12 constraint types:

| Constraint | Description | Documentation |
|-----------|-------------|---------------|
| Nullability | Control null value rates | [→](constraints/nullability.md) |
| Uniqueness | Ensure unique values | [→](constraints/uniqueness.md) |
| Minimum Value | Lower bound validation | [→](constraints/minimum-value.md) |
| Maximum Value | Upper bound validation | [→](constraints/maximum-value.md) |
| Mean | Average value bounds | [→](constraints/mean.md) |
| Median | Median value bounds | [→](constraints/median.md) |
| Percentile | Percentile bounds | [→](constraints/percentile.md) |
| Standard Deviation | Variance bounds | [→](constraints/standard-deviation.md) |
| String Length | String length bounds | [→](constraints/string-length.md) |
| Regex Pattern | Pattern matching | [→](constraints/regex-pattern.md) |
| Value Set | Categorical validation | [→](constraints/value-set.md) |
| Row Count | DataFrame size | [→](constraints/row-count.md) |

## Validation Error Handling

### Default Behavior (Raises Exception)

By default, PolarSeal raises a `ValidationError` exception when validation fails:

```python
from polarseal import load_schema, ValidationError

try:
    validator = load_schema("schema.json")
    result = validator.validate(df)
    print("✓ All validations passed!")
except ValidationError as e:
    print(f"✗ Validation failed: {e}")
    
    # Access failure details
    for failure in e.failures:
        print(f"  Field: {failure['constraint']}")
        print(f"  Issue: {failure['message']}")
```

### Legacy Behavior (Returns Result)

You can also get validation results without exceptions:

```python
validator = load_schema("schema.json")
result = validator.validate(df, raise_on_error=False)

if result.passed:
    print("✓ Validation passed!")
else:
    print("✗ Validation failed!")
    print(result.summary())
    
    # Get only failures
    for failure in result.get_failures():
        print(f"Failed: {failure['constraint']}")
        print(f"  Message: {failure['message']}")
```

## Examples

See the `examples/` directory for:

- `user_schema.json` - User data validation schema
- `sales_schema.json` - Sales transaction validation schema
- `sensor_schema.json` - IoT sensor data validation schema
- `advanced_schema.json` - Demonstrates all new constraints
- `usage_example.py` - Comprehensive usage examples
- `new_constraints_examples.py` - Examples of all new constraints

## Next Steps

- **Learn about constraints**: [Constraints Reference](constraints/index.md)
- **API documentation**: [API Reference](api-reference.md)
- **See examples**: [Examples directory](../examples/)

## Running Tests

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run all tests
pytest

# Run with coverage
pytest --cov=polarseal --cov-report=html
```

## Getting Help

- Check the [Constraints Reference](constraints/index.md) for detailed documentation
- Browse the [examples](../examples/) for working code
- Review the [API Reference](api-reference.md) for programmatic usage
