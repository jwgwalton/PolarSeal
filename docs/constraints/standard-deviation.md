# StandardDeviationConstraint

Validates that the standard deviation of a column falls within specified bounds.

## Overview

The `StandardDeviationConstraint` validates that the variance (spread) of a numeric column is within acceptable bounds. This is useful for ensuring data has expected consistency and detecting anomalous distributions.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `column` | str | Yes | The column name to validate |
| `lower_bound` | float | No* | The minimum acceptable standard deviation |
| `upper_bound` | float | No* | The maximum acceptable standard deviation |

\* At least one of `lower_bound` or `upper_bound` must be specified.

## Usage

### Python API

```python
from polarseal import StandardDeviationConstraint
import polars as pl

df = pl.DataFrame({
    "temperature": [20.1, 20.5, 19.8, 21.2, 20.3]
})

# Both bounds
constraint = StandardDeviationConstraint(
    column="temperature",
    lower_bound=0.2,
    upper_bound=2.0
)

# Only upper bound (limit variance)
constraint = StandardDeviationConstraint(
    column="temperature",
    upper_bound=1.0
)

# Only lower bound (ensure minimum variance)
constraint = StandardDeviationConstraint(
    column="temperature",
    lower_bound=0.5
)

result = constraint.validate(df)
```

### JSON Schema

```json
{
  "fields": {
    "temperature": {
      "type": "Float64",
      "constraints": [
        {
          "type": "standard_deviation",
          "lower_bound": 0.2,
          "upper_bound": 2.0
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
    "message": "Standard deviation check passed",
    "details": {
        "actual_std": 0.5164,
        "lower_bound": 0.2,
        "upper_bound": 2.0
    }
}
```

### Failure

```python
{
    "passed": False,
    "message": "Standard deviation 5.2 exceeds upper bound 2.0",
    "details": {
        "actual_std": 5.2,
        "lower_bound": 0.2,
        "upper_bound": 2.0
    }
}
```

## Common Use Cases

### Sensor Consistency Validation

```python
StandardDeviationConstraint(column="temperature", lower_bound=0.1, upper_bound=5.0)
```

### Data Quality - Detect Too Little Variance

```python
# Ensure data isn't all the same value
StandardDeviationConstraint(column="measurements", lower_bound=0.01)
```

### Data Quality - Detect Too Much Variance

```python
# Ensure data isn't too noisy
StandardDeviationConstraint(column="measurements", upper_bound=10.0)
```

### Manufacturing Tolerance

```python
StandardDeviationConstraint(column="part_dimension", upper_bound=0.05)
```

## Implementation Details

- Uses native Polars expression: `pl.col(column).std()`
- Calculates sample standard deviation (N-1 denominator)
- Null values are excluded from the calculation
- Returns success if column contains only null values
- Both bounds are checked if both parameters are provided
- Returns 0.0 for columns with identical non-null values

## Notes

- Standard deviation measures the spread/dispersion of data
- Higher std = more variance, lower std = more consistency
- A std of 0 means all values are identical
- Use upper bound to ensure consistency
- Use lower bound to ensure sufficient variance/diversity

## See Also

- [Constraints Overview](index.md)
- [MeanConstraint](mean.md) - For validating average values
- [MedianConstraint](median.md) - For validating typical values
- [PercentileConstraint](percentile.md) - For validating distribution tails
