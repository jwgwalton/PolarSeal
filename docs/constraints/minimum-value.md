# MinimumValueConstraint

Ensures all values in a column are above or equal to a minimum value.

## Overview

The `MinimumValueConstraint` validates that all non-null values in a numeric column meet a minimum threshold. This is useful for ensuring data falls within expected ranges.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `column` | str | Yes | The column name to validate |
| `min_value` | float | Yes | The minimum acceptable value |

## Usage

### Python API

```python
from polarseal import MinimumValueConstraint
import polars as pl

df = pl.DataFrame({
    "age": [18, 25, 30, 45, 60]
})

# Ensure all ages are at least 18
constraint = MinimumValueConstraint(
    column="age",
    min_value=18
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
          "type": "minimum_value",
          "min_value": 18
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
    "message": "Minimum value check passed",
    "details": {
        "actual_min": 18,
        "min_value": 18
    }
}
```

### Failure

```python
{
    "passed": False,
    "message": "Minimum value 5 is below limit 18",
    "details": {
        "actual_min": 5,
        "min_value": 18
    }
}
```

## Common Use Cases

### Age Validation

```python
MinimumValueConstraint(column="age", min_value=0)
```

### Price Validation

```python
MinimumValueConstraint(column="price", min_value=0.0)
```

### Temperature Sensor Validation

```python
MinimumValueConstraint(column="temperature", min_value=-40.0)
```

### Percentage Bounds

```python
MinimumValueConstraint(column="completion_rate", min_value=0.0)
```

## Implementation Details

- Uses native Polars expression: `pl.col(column).min()`
- Null values are excluded from the minimum calculation
- Returns success if column contains only null values
- Works with integer and floating-point numeric types

## Notes

- Often used in combination with `MaximumValueConstraint` to define a valid range
- The constraint uses `>=` comparison (inclusive)
- Null values do not cause validation to fail

## See Also

- [Constraints Overview](index.md)
- [MaximumValueConstraint](maximum-value.md) - For upper bounds
- [MeanConstraint](mean.md) - For validating average values
