# ValueSetConstraint

Validates that values are within a predefined set (categorical validation).

## Overview

The `ValueSetConstraint` ensures that all non-null values in a column belong to a predefined set of allowed values. This is useful for validating categorical data, status fields, enums, and ensuring only approved values are present.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `column` | str | Yes | The column name to validate |
| `allowed_values` | list | Yes | List of allowed values (must be non-empty) |

## Usage

### Python API

```python
from polarseal import ValueSetConstraint
import polars as pl

df = pl.DataFrame({
    "status": ["active", "inactive", "pending"]
})

# String categorical values
constraint = ValueSetConstraint(
    column="status",
    allowed_values=["active", "inactive", "pending", "suspended"]
)

# Numeric categorical values
constraint = ValueSetConstraint(
    column="priority",
    allowed_values=[1, 2, 3, 4, 5]
)

result = constraint.validate(df)
```

### JSON Schema

```json
{
  "fields": {
    "status": {
      "type": "String",
      "constraints": [
        {
          "type": "value_set",
          "allowed_values": ["active", "inactive", "pending", "suspended"]
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
    "message": "Value set check passed",
    "details": {
        "allowed_values": ["active", "inactive", "pending"],
        "valid_count": 3,
        "invalid_count": 0,
        "total_count": 3
    }
}
```

### Failure

```python
{
    "passed": False,
    "message": "1 value(s) not in allowed set. Invalid values: ['cancelled']",
    "details": {
        "allowed_values": ["active", "inactive", "pending"],
        "valid_count": 2,
        "invalid_count": 1,
        "total_count": 3
    }
}
```

## Common Use Cases

### Status Field Validation

```python
ValueSetConstraint(
    column="status",
    allowed_values=["active", "inactive", "pending", "suspended"]
)
```

### Priority Levels

```python
ValueSetConstraint(
    column="priority",
    allowed_values=[1, 2, 3, 4, 5]
)
```

### Category Validation

```python
ValueSetConstraint(
    column="category",
    allowed_values=["food", "transport", "entertainment", "utilities"]
)
```

### Yes/No Fields

```python
ValueSetConstraint(
    column="is_active",
    allowed_values=["yes", "no"]
)
```

### Country Codes

```python
ValueSetConstraint(
    column="country",
    allowed_values=["US", "CA", "MX", "GB", "DE", "FR"]
)
```

### Rating Validation

```python
ValueSetConstraint(
    column="rating",
    allowed_values=["poor", "fair", "good", "excellent"]
)
```

## Implementation Details

- Uses native Polars expression: `pl.col(column).is_in(allowed_values)`
- Null values are treated as valid (they pass validation)
- All non-null values must be in the allowed set
- Error message includes up to 5 unique invalid values for debugging
- Works with any data type (strings, integers, floats, etc.)

## Notes

- Use this for validating categorical/enum-like data
- Null values are considered valid (use NullabilityConstraint if needed)
- The `allowed_values` list must contain at least one value
- Value comparison is exact (case-sensitive for strings)
- Order of `allowed_values` doesn't matter

## See Also

- [Constraints Overview](index.md)
- [RegexPatternConstraint](regex-pattern.md) - For pattern-based validation
- [NullabilityConstraint](nullability.md) - For controlling null values
