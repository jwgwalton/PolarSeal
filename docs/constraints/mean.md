# MeanConstraint

Validates that the mean (average) of a column falls within specified bounds.

## Overview

The `MeanConstraint` validates that the arithmetic mean of a numeric column is within acceptable bounds. This is useful for ensuring data distributions meet expected statistical properties.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `column` | str | Yes | The column name to validate |
| `lower_bound` | float | No* | The minimum acceptable mean value |
| `upper_bound` | float | No* | The maximum acceptable mean value |

\* At least one of `lower_bound` or `upper_bound` must be specified.

## Usage

### Python API

```python
from polarseal import MeanConstraint
import polars as pl

df = pl.DataFrame({
    "temperature": [20.5, 21.3, 19.8, 22.1, 20.9]
})

# Both bounds
constraint = MeanConstraint(
    column="temperature",
    lower_bound=19.0,
    upper_bound=23.0
)

# Only upper bound
constraint = MeanConstraint(
    column="temperature",
    upper_bound=25.0
)

# Only lower bound
constraint = MeanConstraint(
    column="temperature",
    lower_bound=18.0
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
          "type": "mean",
          "lower_bound": 19.0,
          "upper_bound": 23.0
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
    "message": "Mean check passed",
    "details": {
        "actual_mean": 20.92,
        "lower_bound": 19.0,
        "upper_bound": 23.0
    }
}
```

### Failure

```python
{
    "passed": False,
    "message": "Mean 25.5 exceeds upper bound 23.0",
    "details": {
        "actual_mean": 25.5,
        "lower_bound": 19.0,
        "upper_bound": 23.0
    }
}
```

## Common Use Cases

### Sensor Data Validation

```python
MeanConstraint(column="temperature", lower_bound=15.0, upper_bound=35.0)
```

### Age Demographics

```python
MeanConstraint(column="age", lower_bound=18, upper_bound=65)
```

### Performance Metrics

```python
MeanConstraint(column="response_time_ms", upper_bound=100.0)
```

### Quality Scores

```python
MeanConstraint(column="quality_score", lower_bound=80.0)
```

## Implementation Details

- Uses native Polars expression: `pl.col(column).mean()`
- Null values are excluded from the mean calculation
- Returns success if column contains only null values
- Both bounds are checked if both parameters are provided

## See Also

- [Constraints Overview](index.md)
- [MedianConstraint](median.md) - For validating median values
- [StandardDeviationConstraint](standard-deviation.md) - For validating variance
- [PercentileConstraint](percentile.md) - For validating specific percentiles
