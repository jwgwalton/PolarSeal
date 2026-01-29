# RowCountConstraint

Validates that the DataFrame has a minimum or maximum number of rows.

## Overview

The `RowCountConstraint` validates that the entire DataFrame contains an acceptable number of rows. This is useful for ensuring datasets meet size requirements, detecting empty datasets, or preventing overly large datasets from being processed.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `column` | str | Yes* | Not used for this constraint (required by base class) |
| `min_rows` | int | No** | Minimum acceptable row count |
| `max_rows` | int | No** | Maximum acceptable row count |

\* Use empty string (`""`) for the column parameter as it's not used.  
\** At least one of `min_rows` or `max_rows` must be specified.

## Usage

### Python API

```python
from polarseal import RowCountConstraint
import polars as pl

df = pl.DataFrame({
    "id": range(100)
})

# Both bounds
constraint = RowCountConstraint(
    column="",  # Not used
    min_rows=10,
    max_rows=1000
)

# Only minimum
constraint = RowCountConstraint(
    column="",
    min_rows=1
)

# Only maximum
constraint = RowCountConstraint(
    column="",
    max_rows=10000
)

result = constraint.validate(df)
```

### JSON Schema

```json
{
  "fields": {
    "any_column": {
      "type": "String",
      "constraints": [
        {
          "type": "row_count",
          "min_rows": 10,
          "max_rows": 1000
        }
      ]
    }
  }
}
```

**Note:** The row count constraint validates the entire DataFrame, not individual columns. The column specified in the schema is ignored.

## Validation Result

### Success

```python
{
    "passed": True,
    "message": "Row count check passed",
    "details": {
        "row_count": 100,
        "min_rows": 10,
        "max_rows": 1000
    }
}
```

### Failure

```python
{
    "passed": False,
    "message": "Row count 5 is below minimum 10",
    "details": {
        "row_count": 5,
        "min_rows": 10,
        "max_rows": 1000
    }
}
```

## Common Use Cases

### Ensure Non-Empty Dataset

```python
RowCountConstraint(column="", min_rows=1)
```

### Batch Processing Requirements

```python
RowCountConstraint(column="", min_rows=100, max_rows=10000)
```

### Prevent Processing Large Datasets

```python
RowCountConstraint(column="", max_rows=1000000)
```

### Sample Size Validation

```python
RowCountConstraint(column="", min_rows=30)  # Minimum for statistical validity
```

### API Response Validation

```python
RowCountConstraint(column="", min_rows=1, max_rows=100)
```

## Implementation Details

- Uses Python's built-in `len(df)` function
- Validates the entire DataFrame, not a specific column
- Both bounds are checked if both parameters are provided
- Works with empty DataFrames (0 rows)

## Notes

- The `column` parameter is required by the base class but is not used
- Use empty string (`""`) as a convention for the column parameter
- This is a DataFrame-level constraint, unlike other column-level constraints
- Exact row count can be enforced with `min_rows=max_rows`

## See Also

- [Constraints Overview](index.md)
- [NullabilityConstraint](nullability.md) - For validating data completeness
- [UniquenessConstraint](uniqueness.md) - For validating data quality
