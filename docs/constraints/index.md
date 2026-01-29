# Constraints Reference

PolarSeal provides 12 powerful constraint types for validating your DataFrames. All constraints use native Polars expressions for optimal performance.

## Constraint Categories

### Data Quality Constraints
- [NullabilityConstraint](nullability.md) - Control acceptable rates of null values
- [UniquenessConstraint](uniqueness.md) - Ensure columns have unique values

### Value Range Constraints
- [MinimumValueConstraint](minimum-value.md) - Ensure values are above a minimum
- [MaximumValueConstraint](maximum-value.md) - Ensure values are below a maximum

### Statistical Constraints
- [MeanConstraint](mean.md) - Validate column mean falls within bounds
- [MedianConstraint](median.md) - Validate column median falls within bounds
- [PercentileConstraint](percentile.md) - Validate arbitrary percentiles fall within bounds
- [StandardDeviationConstraint](standard-deviation.md) - Validate variance falls within bounds

### String Constraints
- [StringLengthConstraint](string-length.md) - Validate string lengths (min/max)
- [RegexPatternConstraint](regex-pattern.md) - Validate strings match regex patterns

### Categorical Constraints
- [ValueSetConstraint](value-set.md) - Ensure values are from a predefined set

### DataFrame Constraints
- [RowCountConstraint](row-count.md) - Validate DataFrame has acceptable row count

## Common Patterns

### Constraint Structure

All constraints follow a consistent pattern:

```python
from polarseal import SomeConstraint

constraint = SomeConstraint(
    column="column_name",
    # constraint-specific parameters
)

result = constraint.validate(df)
# Returns: {"passed": bool, "message": str, "details": dict}
```

### JSON Schema Format

All constraints can be defined in JSON schemas:

```json
{
  "fields": {
    "column_name": {
      "type": "DataType",
      "constraints": [
        {
          "type": "constraint_type",
          "param1": "value1",
          "param2": "value2"
        }
      ]
    }
  }
}
```

### Null Value Handling

Most constraints handle null values gracefully:
- Statistical constraints (mean, median, etc.) exclude nulls from calculations
- String constraints skip null values
- Value set and regex pattern constraints treat nulls as valid
- Use NullabilityConstraint explicitly to control null values

### Validation Results

All constraints return a consistent result dictionary:

```python
{
    "passed": bool,          # True if validation passed
    "message": str,          # Human-readable message
    "details": {             # Constraint-specific details
        # ... additional information
    }
}
```

## Quick Reference

| Constraint | Use Case | Key Parameters |
|-----------|----------|----------------|
| Nullability | Control null values | `max_null_ratio`, `max_null_count` |
| Uniqueness | Detect duplicates | `min_unique_ratio`, `min_unique_count` |
| Minimum Value | Value >= minimum | `min_value` |
| Maximum Value | Value <= maximum | `max_value` |
| Mean | Statistical mean bounds | `lower_bound`, `upper_bound` |
| Median | Statistical median bounds | `lower_bound`, `upper_bound` |
| Percentile | Percentile bounds | `percentile`, `lower_bound`, `upper_bound` |
| Standard Deviation | Variance bounds | `lower_bound`, `upper_bound` |
| String Length | String length bounds | `min_length`, `max_length` |
| Regex Pattern | String format validation | `pattern` |
| Value Set | Categorical validation | `allowed_values` |
| Row Count | DataFrame size | `min_rows`, `max_rows` |

## See Also

- [Getting Started Guide](../getting-started.md)
- [API Reference](../api-reference.md)
- [Examples](../../examples/)
