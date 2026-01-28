# PolarSeal - Functional Overview

## Introduction

PolarSeal is a comprehensive data validation library built on Polars that enables validation beyond simple type checking. The library allows users to define constraints for DataFrames using JSON schemas or programmatic constraints.

## Core Features

### 1. Field-Based Schema Validation

PolarSeal uses a field-based schema format where each field is defined with:
- Explicit data type
- Optional list of constraints (can be empty for type-only validation)

**Example Schema:**
```json
{
  "fields": {
    "user_id": {
      "type": "Int64",
      "constraints": [
        {"type": "nullability", "max_null_ratio": 0.0}
      ]
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
```

### 2. Supported Data Types

- **Integers:** `Int8`, `Int16`, `Int32`, `Int64`, `UInt8`, `UInt16`, `UInt32`, `UInt64`
- **Floats:** `Float32`, `Float64`
- **Strings:** `String`, `Utf8`
- **Boolean:** `Boolean`, `Bool`

Type matching includes exact matches and alias support (e.g., `String` matches `Utf8`).

### 3. Constraint Types

All constraints use native Polars expressions for optimal performance:

#### Nullability Constraint
Controls the acceptable rate of null values in a column.
- Supports ratio-based (`max_null_ratio`: 0.0-1.0)
- Supports count-based (`max_null_count`: integer)

#### Value Range Constraints
- **Minimum Value**: Ensures all values ≥ minimum
- **Maximum Value**: Ensures all values ≤ maximum

#### Statistical Constraints
- **Mean**: Validates column mean falls within bounds
- **Median**: Validates column median falls within bounds
- **Percentile**: Validates arbitrary percentiles (0.0-1.0) fall within bounds

All statistical constraints support:
- Upper bound only
- Lower bound only
- Both upper and lower bounds

### 4. Validation Error Handling

By default, PolarSeal raises a `ValidationError` exception when validation fails:

```python
from polarseal import load_schema, ValidationError

try:
    validator = load_schema("schema.json")
    result = validator.validate(df)
    print("✓ Validation passed!")
except ValidationError as e:
    print(f"✗ Validation failed: {e}")
    for failure in e.failures:
        print(f"  - {failure['message']}")
```

Legacy behavior (returning ValidationResult without raising) is available via `raise_on_error=False`.

## Architecture

### Project Structure

```
PolarSeal/
├── src/polarseal/
│   ├── __init__.py           # Package exports
│   ├── constraints.py        # All constraint implementations
│   ├── schema.py            # JSON schema loading
│   └── validator.py         # SchemaValidator and ValidationResult
├── tests/
│   ├── test_constraints.py  # Constraint unit tests
│   ├── test_schema.py       # Schema loading tests
│   ├── test_validator.py    # Validator tests
│   └── test_integration.py  # Integration tests
├── examples/
│   ├── user_schema.json     # User data validation example
│   ├── sales_schema.json    # Sales data validation example
│   ├── sensor_schema.json   # Sensor data validation example
│   └── usage_example.py     # Comprehensive usage examples
└── docs/
    └── overview.md          # This file
```

### Key Components

1. **Constraints** (`constraints.py`)
   - Base `Constraint` class
   - Individual constraint implementations
   - All use native Polars expressions

2. **Schema Loading** (`schema.py`)
   - JSON schema parsing
   - Field definition extraction
   - Constraint instantiation

3. **Validation** (`validator.py`)
   - `SchemaValidator` class
   - Type validation
   - Constraint validation
   - `ValidationResult` and `ValidationError` classes

## Usage Patterns

### Pattern 1: JSON Schema with Exceptions

```python
import polars as pl
from polarseal import load_schema, ValidationError

df = pl.DataFrame({
    "user_id": [1, 2, 3],
    "age": [25, 30, 35]
})

try:
    validator = load_schema("schema.json")
    result = validator.validate(df)
    print("✓ All validations passed!")
except ValidationError as e:
    print(f"✗ Validation failed: {e}")
```

### Pattern 2: Programmatic Constraints

```python
from polarseal import (
    SchemaValidator,
    NullabilityConstraint,
    MaximumValueConstraint,
    MeanConstraint,
)

constraints = [
    NullabilityConstraint(column="temperature", max_null_ratio=0.05),
    MaximumValueConstraint(column="temperature", max_value=30.0),
    MeanConstraint(column="temperature", lower_bound=19.0, upper_bound=23.0),
]

field_definitions = {"temperature": "Float64"}

validator = SchemaValidator(constraints, field_definitions)
result = validator.validate(df)
```

### Pattern 3: Type-Only Validation

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

This validates only that the DataFrame has the correct columns with the correct types, without additional constraints.

## Performance Characteristics

PolarSeal is designed for high performance:

- **Native Polars Expressions**: All validations use Polars' optimized query engine
- **Single-Pass Validation**: Each constraint requires only one pass over the data
- **Minimal Memory Overhead**: No intermediate data copies
- **Lazy Evaluation Support**: Works with both eager and lazy DataFrames

Example of internal Polars expression usage:
```python
# Nullability check
null_count = df.select(pl.col(column).is_null().sum()).item()

# Statistical validation
median_value = df.select(pl.col(column).median()).item()
percentile_value = df.select(pl.col(column).quantile(0.95)).item()
```

## Testing and Quality

- **Test Coverage**: 96%
- **Total Tests**: 81 (all passing)
- **Test Categories**:
  - Constraint validation tests
  - Schema loading tests
  - Validator tests
  - Integration tests
- **Security**: CodeQL scan with 0 alerts

## Common Use Cases

### 1. User Data Validation

Validate user registration data:
- Age within reasonable bounds
- Required fields present
- Email format (via regex constraints if implemented)

### 2. Sales Transaction Validation

Validate sales data:
- Prices within expected ranges
- Quantities non-negative
- Statistical checks on transaction amounts

### 3. IoT Sensor Data Validation

Validate sensor readings:
- Temperature within operational limits
- No excessive null readings
- Mean values within expected ranges

See `examples/` directory for complete examples.

## Best Practices

1. **Use Field-Based Schemas**: Define types explicitly for all fields
2. **Empty Constraints for Type Checking**: Use `"constraints": []` when you only need type validation
3. **Exception Handling**: Always catch `ValidationError` in production code
4. **Incremental Validation**: Test constraints incrementally during development
5. **Reusable Schemas**: Store schemas in JSON files for reusability across different validation points

## Migration Notes

PolarSeal previously supported a constraint-based schema format. This has been removed in favor of the field-based format:

**Old Format (No Longer Supported):**
```json
{
  "constraints": [
    {
      "type": "maximum_value",
      "column": "age",
      "max_value": 120
    }
  ]
}
```

**Current Format:**
```json
{
  "fields": {
    "age": {
      "type": "Int64",
      "constraints": [
        {"type": "maximum_value", "max_value": 120}
      ]
    }
  }
}
```

## Contributing

Contributions are welcome! The codebase follows these principles:

- Native Polars expressions for all operations
- Comprehensive test coverage
- Clear, informative error messages
- Well-documented public API

## Additional Resources

- **README.md**: Quick start guide and API reference
- **examples/**: Working examples with different data types
- **tests/**: Comprehensive test suite demonstrating all features
