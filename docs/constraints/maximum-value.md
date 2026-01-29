# MaximumValueConstraint

Ensures all values in a column are below or equal to a maximum value.

## Overview

The `MaximumValueConstraint` validates that all non-null values in a numeric column do not exceed a maximum threshold. This is useful for ensuring data falls within expected ranges and detecting outliers.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `column` | str | Yes | The column name to validate |
| `max_value` | float | Yes | The maximum acceptable value |

## Usage

### Python API

```python
from polarseal import MaximumValueConstraint
import polars as pl

df = pl.DataFrame({
    "age": [18, 25, 30, 45, 60]
})

# Ensure no ages exceed 120
constraint = MaximumValueConstraint(
    column="age",
    max_value=120
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
          "type": "maximum_value",
          "max_value": 120
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
    "message": "Maximum value check passed",
    "details": {
        "actual_max": 60,
        "max_value": 120
    }
}
```

### Failure

```python
{
    "passed": False,
    "message": "Maximum value 150 exceeds limit 120",
    "details": {
        "actual_max": 150,
        "max_value": 120
    }
}
```

## Common Use Cases

### Age Validation

```python
MaximumValueConstraint(column="age", max_value=120)
```

### Percentage Bounds

```python
MaximumValueConstraint(column="completion_rate", max_value=100.0)
```

### Temperature Sensor Validation

```python
MaximumValueConstraint(column="temperature", max_value=50.0)
```

### Rating Validation

```python
MaximumValueConstraint(column="rating", max_value=5)
```

## Implementation Details

- Uses native Polars expression: `pl.col(column).max()`
- Null values are excluded from the maximum calculation
- Returns success if column contains only null values
- Works with integer and floating-point numeric types

## Notes

- Often used in combination with `MinimumValueConstraint` to define a valid range
- The constraint uses `<=` comparison (inclusive)
- Null values do not cause validation to fail

## See Also

- [Constraints Overview](index.md)
- [MinimumValueConstraint](minimum-value.md) - For lower bounds
- [PercentileConstraint](percentile.md) - For validating specific percentiles
