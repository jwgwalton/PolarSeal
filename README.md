# PolarSeal

A powerful data validation library built on Polars that goes beyond type checking. PolarSeal allows you to define comprehensive validation schemas for your DataFrames using JSON configuration files or programmatic constraints.

## Features

- **Field-Based Schema**: Define fields with explicit types and optional constraints
- **Type Validation**: Automatically validate DataFrame column types against schema
- **Nullability Constraints**: Control acceptable rates of null values by ratio or count
- **Value Constraints**: Define minimum and maximum acceptable values
- **Statistical Constraints**: Validate mean, median, standard deviation, and arbitrary percentiles with upper/lower bounds
- **Uniqueness Constraints**: Ensure columns have minimum ratios or counts of unique values
- **String Validation**: Validate string lengths and regex pattern matching
- **Categorical Validation**: Ensure values are within predefined sets
- **Row Count Validation**: Control minimum and maximum DataFrame row counts
- **Native Polars**: Uses native Polars expressions for high performance
- **JSON Schema Support**: Define validation schemas in JSON files for easy configuration
- **ValidationError Exception**: Automatic error raising on validation failure with detailed messages

## Installation

```bash
pip install polarseal
```

For development:

```bash
git clone https://github.com/jwgwalton/PolarSeal.git
cd PolarSeal
pip install -e ".[dev]"
```

## Quick Start

### Using Field-Based JSON Schemas (Recommended)

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
        },
        {
          "type": "mean",
          "lower_bound": 18,
          "upper_bound": 65
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
    result = validator.validate(df)  # Raises ValidationError on failure
    print("✓ Validation passed!")
except ValidationError as e:
    print(f"✗ Validation failed: {e}")
```

### Legacy Behavior

If you prefer to get validation results without exceptions:

```python
validator = load_schema("schema.json")
result = validator.validate(df, raise_on_error=False)

if result.passed:
    print("✓ Validation passed!")
else:
    print("✗ Validation failed!")
    print(result.summary())
```

### Programmatic Constraints

You can also create constraints programmatically with optional type definitions:

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
    print("✓ Validation passed!")
except ValidationError as e:
    print(f"✗ Validation failed: {e}")
```

## Schema Format

### Field-Based Schema (Recommended)

The new field-based schema format allows you to define each field with its type and an optional list of constraints:

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

**Supported Data Types:**
- Integer types: `Int8`, `Int16`, `Int32`, `Int64`, `UInt8`, `UInt16`, `UInt32`, `UInt64`
- Float types: `Float32`, `Float64`
- String types: `String`, `Utf8`
- Boolean: `Boolean`, `Bool`

**Example with Empty Constraints:**
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

This will validate that the DataFrame has the correct columns with the correct types, without any additional constraints.

## Constraint Types

### Nullability Constraint

Controls the acceptable rate of null values in a column.

**Field-Based JSON Schema:**
```json
{
  "type": "nullability",
  "max_null_ratio": 0.1,      // Optional: Max ratio (0.0-1.0)
  "max_null_count": 10        // Optional: Max count
}
```

**Python:**
```python
NullabilityConstraint(
    column="column_name",
    max_null_ratio=0.1,    # At least one of these
    max_null_count=10      # must be specified
)
```

### Maximum Value Constraint

Ensures all values in a column are below or equal to a maximum.

**Field-Based JSON Schema:**
```json
{
  "type": "maximum_value",
  "max_value": 100
}
```

**Python:**
```python
MaximumValueConstraint(column="column_name", max_value=100)
```

### Minimum Value Constraint

Ensures all values in a column are above or equal to a minimum.

**Field-Based JSON Schema:**
```json
{
  "type": "minimum_value",
  "min_value": 0
}
```

**Python:**
```python
MinimumValueConstraint(column="column_name", min_value=0)
```

### Median Constraint

Validates that the median of a column falls within specified bounds.

**Field-Based JSON Schema:**
```json
{
  "type": "median",
  "lower_bound": 10,      // Optional
  "upper_bound": 50       // Optional (at least one required)
}
```

**Python:**
```python
MedianConstraint(
    column="column_name",
    lower_bound=10,
    upper_bound=50
)
```

### Mean Constraint

Validates that the mean of a column falls within specified bounds.

**Field-Based JSON Schema:**
```json
{
  "type": "mean",
  "lower_bound": 20,      // Optional
  "upper_bound": 40       // Optional (at least one required)
}
```

**Python:**
```python
MeanConstraint(
    column="column_name",
    lower_bound=20,
    upper_bound=40
)
```

### Percentile Constraint

Validates that a specific percentile of a column falls within specified bounds.

**Field-Based JSON Schema:**
```json
{
  "type": "percentile",
  "percentile": 0.95,     // 0.0 to 1.0
  "lower_bound": 80,      // Optional
  "upper_bound": 100      // Optional (at least one required)
}
```

**Python:**
```python
PercentileConstraint(
    column="column_name",
    percentile=0.95,      # 0.0 to 1.0
    lower_bound=80,
    upper_bound=100
)
```

### Uniqueness Constraint

Validates that a column has a minimum ratio or count of unique values.

**Field-Based JSON Schema:**
```json
{
  "type": "uniqueness",
  "min_unique_ratio": 0.95,   // Optional: Min ratio (0.0-1.0)
  "min_unique_count": 100     // Optional: Min count
}
```

**Python:**
```python
UniquenessConstraint(
    column="column_name",
    min_unique_ratio=0.95,    # At least one of these
    min_unique_count=100      # must be specified
)
```

### Standard Deviation Constraint

Validates that the standard deviation of a column falls within specified bounds.

**Field-Based JSON Schema:**
```json
{
  "type": "standard_deviation",
  "lower_bound": 1.0,     // Optional
  "upper_bound": 5.0      // Optional (at least one required)
}
```

**Python:**
```python
StandardDeviationConstraint(
    column="column_name",
    lower_bound=1.0,
    upper_bound=5.0
)
```

### String Length Constraint

Validates that string values in a column have lengths within specified bounds.

**Field-Based JSON Schema:**
```json
{
  "type": "string_length",
  "min_length": 5,        // Optional: Min string length
  "max_length": 100       // Optional: Max string length
}
```

**Python:**
```python
StringLengthConstraint(
    column="column_name",
    min_length=5,
    max_length=100
)
```

### Regex Pattern Constraint

Validates that string values match a regular expression pattern.

**Field-Based JSON Schema:**
```json
{
  "type": "regex_pattern",
  "pattern": "^[A-Z]{3}-\\d{4}$"   // Regex pattern
}
```

**Python:**
```python
RegexPatternConstraint(
    column="column_name",
    pattern=r"^[A-Z]{3}-\d{4}$"
)
```

### Value Set Constraint

Validates that values are within a predefined set (categorical validation).

**Field-Based JSON Schema:**
```json
{
  "type": "value_set",
  "allowed_values": ["active", "inactive", "pending"]
}
```

**Python:**
```python
ValueSetConstraint(
    column="column_name",
    allowed_values=["active", "inactive", "pending"]
)
```

### Row Count Constraint

Validates that the DataFrame has a minimum or maximum number of rows.

**Field-Based JSON Schema:**
```json
{
  "type": "row_count",
  "min_rows": 10,         // Optional: Min row count
  "max_rows": 1000        // Optional: Max row count
}
```

**Python:**
```python
RowCountConstraint(
    column="",              # Not used for this constraint
    min_rows=10,
    max_rows=1000
)
```

## Working with ValidationError

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

## Working with Validation Results (Legacy)

When using `raise_on_error=False`, the `ValidationResult` object provides multiple ways to inspect validation outcomes:

```python
result = validator.validate(df, raise_on_error=False)

# Check if validation passed
if result.passed:
    print("All constraints satisfied!")

# Get a summary
print(result.summary())

# Get detailed dictionary
result_dict = result.to_dict()
print(f"Passed: {result_dict['passed_constraints']}/{result_dict['total_constraints']}")

# Get only failures
for failure in result.get_failures():
    print(f"Failed: {failure['constraint']}")
    print(f"  Message: {failure['message']}")
    print(f"  Details: {failure['details']}")
```

## Examples

See the `examples/` directory for:
- `user_schema.json` - User data validation schema
- `sales_schema.json` - Sales transaction validation schema
- `sensor_schema.json` - IoT sensor data validation schema
- `usage_example.py` - Comprehensive usage examples

## Running Tests

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run all tests
pytest

# Run with coverage
pytest --cov=polarseal --cov-report=html
```

## How It Works

PolarSeal uses native Polars expressions to calculate statistics and validate constraints. This means:

- **Fast**: Takes advantage of Polars' optimized query engine
- **Memory Efficient**: Doesn't create intermediate copies of data
- **Lazy Evaluation Support**: Works with both eager and lazy DataFrames

Example of native Polars expression usage:
```python
# Internally, constraints use expressions like:
null_count = df.select(pl.col(column).is_null().sum()).item()
median_value = df.select(pl.col(column).median()).item()
percentile_value = df.select(pl.col(column).quantile(0.95)).item()
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see LICENSE file for details.

## Acknowledgments

Built with [Polars](https://www.pola.rs/) - A blazingly fast DataFrames library
