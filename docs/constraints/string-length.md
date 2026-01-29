# StringLengthConstraint

Validates that string values in a column have lengths within specified bounds.

## Overview

The `StringLengthConstraint` validates that string values (measured in characters) fall within minimum and maximum length requirements. This is useful for format validation and database schema enforcement.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `column` | str | Yes | The column name to validate |
| `min_length` | int | No* | Minimum acceptable string length (characters) |
| `max_length` | int | No* | Maximum acceptable string length (characters) |

\* At least one of `min_length` or `max_length` must be specified.

## Usage

### Python API

```python
from polarseal import StringLengthConstraint
import polars as pl

df = pl.DataFrame({
    "product_code": ["ABC123", "DEF456", "GHI789"]
})

# Both bounds
constraint = StringLengthConstraint(
    column="product_code",
    min_length=6,
    max_length=6
)

# Only maximum
constraint = StringLengthConstraint(
    column="description",
    max_length=500
)

# Only minimum
constraint = StringLengthConstraint(
    column="password",
    min_length=8
)

result = constraint.validate(df)
```

### JSON Schema

```json
{
  "fields": {
    "product_code": {
      "type": "String",
      "constraints": [
        {
          "type": "string_length",
          "min_length": 6,
          "max_length": 6
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
    "message": "String length check passed",
    "details": {
        "min_length_found": 6,
        "max_length_found": 6,
        "min_length": 6,
        "max_length": 6
    }
}
```

### Failure

```python
{
    "passed": False,
    "message": "Minimum string length 3 is below required minimum 6",
    "details": {
        "min_length_found": 3,
        "max_length_found": 10,
        "min_length": 6,
        "max_length": 10
    }
}
```

## Common Use Cases

### Fixed-Length Codes

```python
StringLengthConstraint(column="product_code", min_length=8, max_length=8)
```

### Password Requirements

```python
StringLengthConstraint(column="password", min_length=8, max_length=128)
```

### Database VARCHAR Limits

```python
StringLengthConstraint(column="description", max_length=255)
```

### Form Input Validation

```python
StringLengthConstraint(column="username", min_length=3, max_length=20)
```

### Postal Codes

```python
StringLengthConstraint(column="postal_code", min_length=5, max_length=10)
```

## Implementation Details

- Uses native Polars expression: `pl.col(column).str.len_chars()`
- Counts Unicode characters (not bytes)
- Null values are excluded from validation
- Returns success if column contains only null values
- Both bounds are checked if both parameters are provided
- Checks all non-null strings; all must pass for validation to succeed

## Notes

- Length is measured in characters, not bytes (important for Unicode)
- Empty strings ("") have length 0
- Whitespace characters count toward length
- Use `min_length=max_length` to enforce exact length

## See Also

- [Constraints Overview](index.md)
- [RegexPatternConstraint](regex-pattern.md) - For format/pattern validation
- [ValueSetConstraint](value-set.md) - For categorical validation
