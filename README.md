# PolarSeal

A powerful data validation library built on Polars that goes beyond type checking. PolarSeal allows you to define comprehensive validation schemas for your DataFrames using JSON configuration files or programmatic constraints.

## Features

- ✅ **12 Constraint Types** - Data quality, ranges, statistics, strings, and more
- ✅ **Field-Based Schema** - Define fields with explicit types and constraints
- ✅ **Type Validation** - Automatically validate DataFrame column types
- ✅ **Native Polars** - Uses native Polars expressions for high performance
- ✅ **JSON Schema Support** - Define validation schemas in JSON files
- ✅ **ValidationError Exception** - Automatic error raising with detailed messages

## Documentation

📚 **[Complete Documentation](docs/index.md)**

- [Getting Started](docs/getting-started.md) - Installation and quick start
- [Constraints Reference](docs/constraints/index.md) - All 12 constraint types
- [API Reference](docs/api-reference.md) - Programmatic usage
- [Examples](examples/) - Working code examples

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

### Installation

```bash
pip install polarseal
```

### Basic Usage

Create a schema file (`schema.json`):

```json
{
  "fields": {
    "user_id": {
      "type": "Int64",
      "constraints": [
        {"type": "nullability", "max_null_ratio": 0.0},
        {"type": "uniqueness", "min_unique_ratio": 1.0}
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

Validate your DataFrame:

```python
import polars as pl
from polarseal import load_schema, ValidationError

df = pl.DataFrame({
    "user_id": [1, 2, 3, 4, 5],
    "age": [25, 32, 28, 45, 38],
})

try:
    validator = load_schema("schema.json")
    result = validator.validate(df)
    print("✓ Validation passed!")
except ValidationError as e:
    print(f"✗ Validation failed: {e}")
```

## Available Constraints

PolarSeal provides **12 constraint types** for comprehensive validation:

### Data Quality
- **[NullabilityConstraint](docs/constraints/nullability.md)** - Control null value rates
- **[UniquenessConstraint](docs/constraints/uniqueness.md)** - Ensure unique values

### Value Ranges
- **[MinimumValueConstraint](docs/constraints/minimum-value.md)** - Lower bounds
- **[MaximumValueConstraint](docs/constraints/maximum-value.md)** - Upper bounds

### Statistics
- **[MeanConstraint](docs/constraints/mean.md)** - Average value bounds
- **[MedianConstraint](docs/constraints/median.md)** - Median value bounds
- **[PercentileConstraint](docs/constraints/percentile.md)** - Percentile bounds
- **[StandardDeviationConstraint](docs/constraints/standard-deviation.md)** - Variance bounds

### Strings
- **[StringLengthConstraint](docs/constraints/string-length.md)** - Length validation
- **[RegexPatternConstraint](docs/constraints/regex-pattern.md)** - Pattern matching

### Categorical
- **[ValueSetConstraint](docs/constraints/value-set.md)** - Predefined value sets

### DataFrame
- **[RowCountConstraint](docs/constraints/row-count.md)** - Row count validation

## Examples

See the [examples/](examples/) directory for complete working examples:

- [user_schema.json](examples/user_schema.json) - User data validation
- [sales_schema.json](examples/sales_schema.json) - Sales transactions
- [sensor_schema.json](examples/sensor_schema.json) - IoT sensor data
- [advanced_schema.json](examples/advanced_schema.json) - All constraint types
- [new_constraints_examples.py](examples/new_constraints_examples.py) - Programmatic examples

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

## Running Tests

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run all tests
pytest

# Run with coverage
pytest --cov=polarseal --cov-report=html
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

See the [complete documentation](docs/index.md) for architecture details and contribution guidelines.

## License

MIT License - see LICENSE file for details.

## Acknowledgments

Built with [Polars](https://www.pola.rs/) - A blazingly fast DataFrames library
