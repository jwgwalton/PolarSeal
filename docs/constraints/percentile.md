# PercentileConstraint

Validates that a specific percentile of a column falls within specified bounds.

## Overview

The `PercentileConstraint` validates that an arbitrary percentile (quantile) of a numeric column is within acceptable bounds. Percentiles are useful for understanding data distribution and detecting outliers.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `column` | str | Yes | The column name to validate |
| `percentile` | float | Yes | The percentile to check (0.0 to 1.0) |
| `lower_bound` | float | No* | The minimum acceptable percentile value |
| `upper_bound` | float | No* | The maximum acceptable percentile value |

\* At least one of `lower_bound` or `upper_bound` must be specified.

## Usage

### Python API

```python
from polarseal import PercentileConstraint
import polars as pl

df = pl.DataFrame({
    "score": [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
})

# 95th percentile (top 5% of values)
constraint = PercentileConstraint(
    column="score",
    percentile=0.95,
    lower_bound=80,
    upper_bound=100
)

# 25th percentile (bottom quartile)
constraint = PercentileConstraint(
    column="score",
    percentile=0.25,
    upper_bound=30
)

# 99th percentile (outlier detection)
constraint = PercentileConstraint(
    column="response_time",
    percentile=0.99,
    upper_bound=1000
)

result = constraint.validate(df)
```

### JSON Schema

```json
{
  "fields": {
    "score": {
      "type": "Float64",
      "constraints": [
        {
          "type": "percentile",
          "percentile": 0.95,
          "lower_bound": 80,
          "upper_bound": 100
        }
      ]
    }
  }
}
```

## Validation Result

### Success

```python
{
    "passed": True,
    "message": "Percentile check passed",
    "details": {
        "actual_percentile": 95.0,
        "percentile": 0.95,
        "lower_bound": 80,
        "upper_bound": 100
    }
}
```

### Failure

```python
{
    "passed": False,
    "message": "Percentile 0.95 value 105 exceeds upper bound 100",
    "details": {
        "actual_percentile": 105.0,
        "percentile": 0.95,
        "lower_bound": 80,
        "upper_bound": 100
    }
}
```

## Common Percentiles

| Percentile | Meaning |
|-----------|---------|
| 0.01 (1st) | Minimum values / lower outliers |
| 0.25 (25th) | First quartile (Q1) |
| 0.50 (50th) | Median (Q2) |
| 0.75 (75th) | Third quartile (Q3) |
| 0.90 (90th) | High values |
| 0.95 (95th) | Very high values |
| 0.99 (99th) | Upper outliers |

## Common Use Cases

### Performance Monitoring (P95)

```python
PercentileConstraint(column="response_time_ms", percentile=0.95, upper_bound=500)
```

### Quality Assurance (P99)

```python
PercentileConstraint(column="error_rate", percentile=0.99, upper_bound=0.05)
```

### Outlier Detection

```python
PercentileConstraint(column="transaction_amount", percentile=0.99, upper_bound=10000)
```

### Data Quality Checks

```python
PercentileConstraint(column="temperature", percentile=0.01, lower_bound=-10)
PercentileConstraint(column="temperature", percentile=0.99, upper_bound=50)
```

## Implementation Details

- Uses native Polars expression: `pl.col(column).quantile(percentile)`
- Percentile parameter must be between 0.0 and 1.0 (inclusive)
- Null values are excluded from the percentile calculation
- Returns success if column contains only null values
- Both bounds are checked if both parameters are provided

## Notes

- 0.0 percentile = minimum value
- 0.5 percentile = median
- 1.0 percentile = maximum value
- P95 and P99 are commonly used in SLA monitoring
- Use multiple percentile constraints to validate the full distribution

## See Also

- [Constraints Overview](index.md)
- [MedianConstraint](median.md) - For the 50th percentile specifically
- [MinimumValueConstraint](minimum-value.md) - For the 0th percentile
- [MaximumValueConstraint](maximum-value.md) - For the 100th percentile
