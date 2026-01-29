# PolarSeal Documentation

Welcome to the PolarSeal documentation! PolarSeal is a powerful data validation library built on Polars that goes beyond type checking.

## What is PolarSeal?

PolarSeal allows you to define comprehensive validation schemas for your DataFrames using JSON configuration files or programmatic constraints. It provides 12 constraint types for validating data quality, ranges, statistical properties, formats, and more.

## Quick Links

- [Getting Started](getting-started.md) - Installation and basic usage
- [Constraints Reference](constraints/index.md) - Complete constraint documentation
- [API Reference](api-reference.md) - Programmatic API documentation
- [Examples](../examples/) - Working code examples

## Key Features

- ✅ **12 Constraint Types** - Comprehensive validation capabilities
- ✅ **Field-Based Schema** - Define fields with explicit types and constraints
- ✅ **Type Validation** - Automatically validate DataFrame column types
- ✅ **Native Polars** - Uses native Polars expressions for high performance
- ✅ **JSON Schema Support** - Define validation schemas in JSON files
- ✅ **ValidationError Exception** - Automatic error raising with detailed messages

## Constraint Categories

### 📊 Data Quality Constraints
- [NullabilityConstraint](constraints/nullability.md) - Control null value rates
- [UniquenessConstraint](constraints/uniqueness.md) - Ensure unique values

### 📏 Value Range Constraints
- [MinimumValueConstraint](constraints/minimum-value.md) - Lower bounds
- [MaximumValueConstraint](constraints/maximum-value.md) - Upper bounds

### 📈 Statistical Constraints
- [MeanConstraint](constraints/mean.md) - Average value bounds
- [MedianConstraint](constraints/median.md) - Median value bounds
- [PercentileConstraint](constraints/percentile.md) - Arbitrary percentile bounds
- [StandardDeviationConstraint](constraints/standard-deviation.md) - Variance bounds

### 📝 String Constraints
- [StringLengthConstraint](constraints/string-length.md) - Min/max length
- [RegexPatternConstraint](constraints/regex-pattern.md) - Pattern matching

### 🏷️ Categorical Constraints
- [ValueSetConstraint](constraints/value-set.md) - Predefined value sets

### 📋 DataFrame Constraints
- [RowCountConstraint](constraints/row-count.md) - DataFrame size validation

## Quick Example

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
```

## Schema Example

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
        {"type": "maximum_value", "max_value": 120},
        {"type": "mean", "lower_bound": 18, "upper_bound": 65}
      ]
    }
  }
}
```

## Architecture

PolarSeal is designed for high performance:

- **Native Polars Expressions** - All validations use Polars' optimized query engine
- **Single-Pass Validation** - Each constraint requires only one pass over the data
- **Minimal Memory Overhead** - No intermediate data copies
- **Lazy Evaluation Support** - Works with both eager and lazy DataFrames

## Learn More

- **Getting Started**: [Installation and quick start guide](getting-started.md)
- **Constraints**: [Detailed constraint documentation](constraints/index.md)
- **API Reference**: [Programmatic API guide](api-reference.md)
- **Examples**: [Working code examples](../examples/)

## Contributing

Contributions are welcome! The codebase follows these principles:

- Native Polars expressions for all operations
- Comprehensive test coverage
- Clear, informative error messages
- Well-documented public API

## License

MIT License - see LICENSE file for details.

## Acknowledgments

Built with [Polars](https://www.pola.rs/) - A blazingly fast DataFrames library
