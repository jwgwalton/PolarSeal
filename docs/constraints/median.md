# MedianConstraint

Validates that the median (middle value) of a column falls within specified bounds.

## Overview

The `MedianConstraint` validates that the median of a numeric column is within acceptable bounds. The median is less sensitive to outliers than the mean, making it useful for validating typical values in skewed distributions.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `column` | str | Yes | The column name to validate |
| `lower_bound` | float | No* | The minimum acceptable median value |
| `upper_bound` | float | No* | The maximum acceptable median value |

\* At least one of `lower_bound` or `upper_bound` must be specified.

## Usage

### Python API

```python
from polarseal import MedianConstraint
import polars as pl

df = pl.DataFrame({
    "age": [25, 28, 30, 32, 35, 40, 45]
})

# Both bounds
constraint = MedianConstraint(
    column="age",
    lower_bound=25,
    upper_bound=50
)

# Only upper bound
constraint = MedianConstraint(
    column="age",
    upper_bound=40
)

# Only lower bound
constraint = MedianConstraint(
    column="age",
    lower_bound=20
)

result = constraint.validate(df)
```

### JSON Schema

```json
{
  "fields": {
    "age": {
      "type": "Int64",
      "constraints": [
        {
          "type": "median",
          "lower_bound": 25,
          "upper_bound": 50
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
    "message": "Median check passed",
    "details": {
        "actual_median": 32,
        "lower_bound": 25,
        "upper_bound": 50
    }
}
```

### Failure

```python
{
    "passed": False,
    "message": "Median 55 exceeds upper bound 50",
    "details": {
        "actual_median": 55,
        "lower_bound": 25,
        "upper_bound": 50
    }
}
```

## Common Use Cases

### Age Demographics

```python
MedianConstraint(column="age", lower_bound=25, upper_bound=50)
```

### Pricing Validation

```python
MedianConstraint(column="price", lower_bound=10.0, upper_bound=100.0)
```

### Response Time Validation

```python
MedianConstraint(column="response_time_ms", upper_bound=200.0)
```

### Salary Bands

```python
MedianConstraint(column="salary", lower_bound=50000, upper_bound=150000)
```

## Implementation Details

- Uses native Polars expression: `pl.col(column).median()`
- Null values are excluded from the median calculation
- Returns success if column contains only null values
- Both bounds are checked if both parameters are provided
- For even-sized datasets, the median is the average of the two middle values

## Notes

- Median is more robust to outliers than mean
- Use median for skewed distributions where extreme values might affect the mean
- For symmetric distributions, median and mean should be similar

## See Also

- [Constraints Overview](index.md)
- [MeanConstraint](mean.md) - For validating mean values
- [PercentileConstraint](percentile.md) - For validating other percentiles (median is 50th percentile)
- [StandardDeviationConstraint](standard-deviation.md) - For validating variance
