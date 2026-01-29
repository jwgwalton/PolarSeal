# UniquenessConstraint

Validates that a column has a minimum ratio or count of unique values.

## Overview

The `UniquenessConstraint` ensures that a column maintains a specified level of uniqueness. This is useful for detecting duplicate data issues and validating that key columns are sufficiently unique.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `column` | str | Yes | The column name to validate |
| `min_unique_ratio` | float | No* | Minimum ratio of unique values (0.0 to 1.0) |
| `min_unique_count` | int | No* | Minimum count of unique values |

\* At least one of `min_unique_ratio` or `min_unique_count` must be specified.

## Usage

### Python API

```python
from polarseal import UniquenessConstraint
import polars as pl

df = pl.DataFrame({
    "user_id": [1, 2, 3, 4, 5, 1, 2]  # 5 unique out of 7 total
})

# By ratio (require 95% unique)
constraint = UniquenessConstraint(
    column="user_id",
    min_unique_ratio=0.95
)

# By count (require at least 100 unique)
constraint = UniquenessConstraint(
    column="user_id",
    min_unique_count=100
)

# Both criteria
constraint = UniquenessConstraint(
    column="user_id",
    min_unique_ratio=0.99,
    min_unique_count=1000
)

result = constraint.validate(df)
```

### JSON Schema

```json
{
  "fields": {
    "user_id": {
      "type": "String",
      "constraints": [
        {
          "type": "uniqueness",
          "min_unique_ratio": 0.99,
          "min_unique_count": 1000
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
    "message": "Uniqueness check passed",
    "details": {
        "unique_count": 5,
        "total_count": 7,
        "unique_ratio": 0.7143
    }
}
```

### Failure

```python
{
    "passed": False,
    "message": "Unique ratio 0.7143 is below minimum 0.9500",
    "details": {
        "unique_count": 5,
        "total_count": 7,
        "unique_ratio": 0.7143
    }
}
```

## Common Use Cases

### Ensure Primary Key Uniqueness

```python
UniquenessConstraint(column="user_id", min_unique_ratio=1.0)
```

### Detect Duplicate Records

```python
UniquenessConstraint(column="transaction_id", min_unique_ratio=0.99)
```

### Validate Dataset Diversity

```python
UniquenessConstraint(column="product_code", min_unique_count=100)
```

## Implementation Details

- Uses native Polars expression: `pl.col(column).n_unique()`
- Unique ratio is calculated as: `unique_count / total_count`
- Null values are counted as one unique value
- Both constraints are checked if both parameters are provided

## See Also

- [Constraints Overview](index.md)
- [NullabilityConstraint](nullability.md) - For controlling null values
- [ValueSetConstraint](value-set.md) - For categorical validation
