# PolarSeal

A powerful data validation library built on Polars that goes beyond type checking. PolarSeal allows you to define comprehensive validation schemas for your DataFrames using JSON configuration files or programmatic constraints.

## Features

- **Nullability Constraints**: Control acceptable rates of null values by ratio or count
- **Value Constraints**: Define minimum and maximum acceptable values
- **Statistical Constraints**: Validate mean, median, and arbitrary percentiles with upper/lower bounds
- **Native Polars**: Uses native Polars expressions for high performance
- **JSON Schema Support**: Define validation schemas in JSON files for easy configuration
- **Comprehensive Validation Results**: Get detailed reports on constraint violations

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

### Using JSON Schemas

Create a schema file (`schema.json`):

```json
{
  "constraints": [
    {
      "type": "nullability",
      "column": "user_id",
      "max_null_ratio": 0.0
    },
    {
      "type": "minimum_value",
      "column": "age",
      "min_value": 0
    },
    {
      "type": "maximum_value",
      "column": "age",
      "max_value": 120
    },
    {
      "type": "mean",
      "column": "age",
      "lower_bound": 18,
      "upper_bound": 65
    }
  ]
}
```

Validate your DataFrame:

```python
import polars as pl
from polarseal import load_schema, SchemaValidator

# Create your DataFrame
df = pl.DataFrame({
    "user_id": [1, 2, 3, 4, 5],
    "age": [25, 32, 28, 45, 38],
})

# Load schema and validate
constraints = load_schema("schema.json")
validator = SchemaValidator(constraints)
result = validator.validate(df)

# Check results
if result.passed:
    print("✓ Validation passed!")
else:
    print("✗ Validation failed!")
    print(result.summary())
```

### Programmatic Constraints

```python
import polars as pl
from polarseal import (
    SchemaValidator,
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

# Validate
validator = SchemaValidator(constraints)
result = validator.validate(df)

print(result.summary())
```

## Constraint Types

### Nullability Constraint

Controls the acceptable rate of null values in a column.

**JSON Schema:**
```json
{
  "type": "nullability",
  "column": "column_name",
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

**JSON Schema:**
```json
{
  "type": "maximum_value",
  "column": "column_name",
  "max_value": 100
}
```

**Python:**
```python
MaximumValueConstraint(column="column_name", max_value=100)
```

### Minimum Value Constraint

Ensures all values in a column are above or equal to a minimum.

**JSON Schema:**
```json
{
  "type": "minimum_value",
  "column": "column_name",
  "min_value": 0
}
```

**Python:**
```python
MinimumValueConstraint(column="column_name", min_value=0)
```

### Median Constraint

Validates that the median of a column falls within specified bounds.

**JSON Schema:**
```json
{
  "type": "median",
  "column": "column_name",
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

**JSON Schema:**
```json
{
  "type": "mean",
  "column": "column_name",
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

**JSON Schema:**
```json
{
  "type": "percentile",
  "column": "column_name",
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

## Working with Validation Results

The `ValidationResult` object provides multiple ways to inspect validation outcomes:

```python
result = validator.validate(df)

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
