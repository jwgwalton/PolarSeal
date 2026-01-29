# PolarSeal - Functional Overview

## Introduction

PolarSeal is a comprehensive data validation library built on Polars that enables validation beyond simple type checking. The library allows users to define constraints for DataFrames using JSON schemas or programmatic constraints.

> **Note**: This document provides a high-level overview. For detailed documentation, see:
> - [Getting Started Guide](getting-started.md)
> - [Complete Constraints Reference](constraints/index.md)
> - [API Reference](api-reference.md)

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

PolarSeal provides **12 constraint types** organized into categories:

#### Data Quality Constraints
- **[NullabilityConstraint](constraints/nullability.md)** - Controls null value rates (ratio/count)
- **[UniquenessConstraint](constraints/uniqueness.md)** - Ensures minimum unique values

#### Value Range Constraints
- **[MinimumValueConstraint](constraints/minimum-value.md)** - Ensures values ≥ minimum
- **[MaximumValueConstraint](constraints/maximum-value.md)** - Ensures values ≤ maximum

#### Statistical Constraints
- **[MeanConstraint](constraints/mean.md)** - Validates column mean falls within bounds
- **[MedianConstraint](constraints/median.md)** - Validates column median falls within bounds
- **[PercentileConstraint](constraints/percentile.md)** - Validates arbitrary percentiles (0.0-1.0)
- **[StandardDeviationConstraint](constraints/standard-deviation.md)** - Validates variance falls within bounds

#### String Constraints
- **[StringLengthConstraint](constraints/string-length.md)** - Validates string length bounds
- **[RegexPatternConstraint](constraints/regex-pattern.md)** - Validates pattern matching

#### Categorical Constraints
- **[ValueSetConstraint](constraints/value-set.md)** - Ensures values from predefined set

#### DataFrame Constraints
- **[RowCountConstraint](constraints/row-count.md)** - Validates DataFrame row count

All constraints use native Polars expressions for optimal performance.

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
│   ├── constraints.py        # All 12 constraint implementations
│   ├── schema.py            # JSON schema loading
│   └── validator.py         # SchemaValidator and ValidationResult
├── tests/
│   ├── test_constraints.py      # Constraint unit tests
│   ├── test_new_constraints.py  # New constraint tests
│   ├── test_schema.py           # Schema loading tests
│   ├── test_validator.py        # Validator tests
│   └── test_integration.py      # Integration tests
├── examples/
│   ├── user_schema.json             # User data validation
│   ├── sales_schema.json            # Sales transactions
│   ├── sensor_schema.json           # IoT sensor data
│   ├── advanced_schema.json         # All constraints
│   └── new_constraints_examples.py  # Usage examples
└── docs/
    ├── index.md                     # Documentation home
    ├── getting-started.md           # Quick start guide
    ├── api-reference.md             # API documentation
    ├── overview.md                  # This file
    └── constraints/                 # Individual constraint docs
        ├── index.md
        ├── nullability.md
        ├── uniqueness.md
        └── ... (all 12 constraints)
```

### Key Components

1. **Constraints** (`constraints.py`)
   - Base `Constraint` class
   - 12 constraint implementations
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

See the [Getting Started Guide](getting-started.md) for detailed usage examples.

### Quick Example: JSON Schema

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

### Quick Example: Programmatic

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

- **Test Coverage**: High coverage across all constraints
- **Total Tests**: 114 tests (all passing)
- **Test Categories**:
  - Constraint validation tests (original and new constraints)
  - Schema loading tests
  - Validator tests
  - Integration tests
- **Security**: CodeQL scan with 0 alerts

## Common Use Cases

### 1. User Data Validation

Validate user registration data:
- Age within reasonable bounds ([MinimumValueConstraint](constraints/minimum-value.md), [MaximumValueConstraint](constraints/maximum-value.md))
- Required fields present ([NullabilityConstraint](constraints/nullability.md))
- Email format ([RegexPatternConstraint](constraints/regex-pattern.md))
- Unique user IDs ([UniquenessConstraint](constraints/uniqueness.md))

### 2. Sales Transaction Validation

Validate sales data:
- Prices within expected ranges ([MinimumValueConstraint](constraints/minimum-value.md), [MaximumValueConstraint](constraints/maximum-value.md))
- Valid product categories ([ValueSetConstraint](constraints/value-set.md))
- Statistical checks on transaction amounts ([MeanConstraint](constraints/mean.md), [StandardDeviationConstraint](constraints/standard-deviation.md))

### 3. IoT Sensor Data Validation

Validate sensor readings:
- Temperature within operational limits ([MinimumValueConstraint](constraints/minimum-value.md), [MaximumValueConstraint](constraints/maximum-value.md))
- No excessive null readings ([NullabilityConstraint](constraints/nullability.md))
- Mean values within expected ranges ([MeanConstraint](constraints/mean.md))
- Consistent variance ([StandardDeviationConstraint](constraints/standard-deviation.md))

See [examples/](../examples/) directory for complete working examples.

## Best Practices

1. **Use Field-Based Schemas**: Define types explicitly for all fields
2. **Empty Constraints for Type Checking**: Use `"constraints": []` when you only need type validation
3. **Exception Handling**: Always catch `ValidationError` in production code
4. **Incremental Validation**: Test constraints incrementally during development
5. **Reusable Schemas**: Store schemas in JSON files for reusability across validation points
6. **Choose Appropriate Constraints**: Use the right constraint for your data type and validation needs
7. **Document Assumptions**: Include comments in schemas explaining validation thresholds

## Additional Resources

- **[Getting Started](getting-started.md)**: Installation and quick start guide
- **[Constraints Reference](constraints/index.md)**: Detailed documentation for all 12 constraints
- **[API Reference](api-reference.md)**: Complete programmatic API documentation
- **[Examples](../examples/)**: Working code examples

## Contributing

Contributions are welcome! The codebase follows these principles:

- Native Polars expressions for all operations
- Comprehensive test coverage
- Clear, informative error messages
- Well-documented public API

See the repository's contribution guidelines for more information.
