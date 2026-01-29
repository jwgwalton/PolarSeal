# NullabilityConstraint

Controls the acceptable rate of null values in a column.

## Overview

The `NullabilityConstraint` validates that a column does not exceed specified null value thresholds. You can specify either a maximum ratio (percentage) or a maximum count of null values, or both.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `column` | str | Yes | The column name to validate |
| `max_null_ratio` | float | No* | Maximum acceptable ratio of null values (0.0 to 1.0) |
| `max_null_count` | int | No* | Maximum acceptable count of null values |

\* At least one of `max_null_ratio` or `max_null_count` must be specified.

## Usage

### Python API

```python
from polarseal import NullabilityConstraint
import polars as pl

df = pl.DataFrame({
    "user_id": [1, 2, 3, None, 5]
})

# By ratio (20% nulls allowed)
constraint = NullabilityConstraint(
    column="user_id",
    max_null_ratio=0.2
)

# By count (1 null allowed)
constraint = NullabilityConstraint(
    column="user_id",
    max_null_count=1
)

# Both criteria
constraint = NullabilityConstraint(
    column="user_id",
    max_null_ratio=0.1,
    max_null_count=5
)

result = constraint.validate(df)
```

### JSON Schema

```json
{
  "fields": {
    "user_id": {
      "type": "Int64",
      "constraints": [
        {
          "type": "nullability",
          "max_null_ratio": 0.1,
          "max_null_count": 10
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
    "message": "Nullability check passed",
    "details": {
        "null_count": 1,
        "total_count": 5,
        "null_ratio": 0.2
    }
}
```

### Failure

```python
{
    "passed": False,
    "message": "Null ratio 0.4000 exceeds maximum 0.2000",
    "details": {
        "null_count": 2,
        "total_count": 5,
        "null_ratio": 0.4
    }
}
```

## Common Use Cases

### Require Non-Null Primary Keys

```python
NullabilityConstraint(column="user_id", max_null_ratio=0.0)
```

### Allow Small Percentage of Missing Data

```python
NullabilityConstraint(column="email", max_null_ratio=0.05)  # 5% nulls OK
```

### Limit Absolute Number of Nulls

```python
NullabilityConstraint(column="phone", max_null_count=100)
```

## Implementation Details

- Uses native Polars expression: `pl.col(column).is_null().sum()`
- Null ratio is calculated as: `null_count / total_count`
- Both constraints are checked if both parameters are provided
- Returns success if column contains only null values when ratio/count allows it

## See Also

- [Constraints Overview](index.md)
- [UniquenessConstraint](uniqueness.md) - For detecting duplicate values
- [ValueSetConstraint](value-set.md) - For categorical validation
