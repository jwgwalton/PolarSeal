# RegexPatternConstraint

Validates that string values match a regular expression pattern.

## Overview

The `RegexPatternConstraint` validates that all non-null string values in a column match a specified regular expression pattern. This is useful for format validation such as emails, phone numbers, product codes, and custom formats.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `column` | str | Yes | The column name to validate |
| `pattern` | str | Yes | Regular expression pattern to match |

## Usage

### Python API

```python
from polarseal import RegexPatternConstraint
import polars as pl

df = pl.DataFrame({
    "email": ["user@example.com", "admin@test.org"]
})

# Email validation (simple)
constraint = RegexPatternConstraint(
    column="email",
    pattern=r"@"
)

# Product code format
constraint = RegexPatternConstraint(
    column="product_code",
    pattern=r"^[A-Z]{3}-\d{4}$"
)

# Phone number format
constraint = RegexPatternConstraint(
    column="phone",
    pattern=r"^\d{3}-\d{3}-\d{4}$"
)

result = constraint.validate(df)
```

### JSON Schema

```json
{
  "fields": {
    "email": {
      "type": "String",
      "constraints": [
        {
          "type": "regex_pattern",
          "pattern": "@.*\\."
        }
      ]
    }
  }
}
```

**Note:** In JSON, backslashes must be escaped (e.g., `\\d` instead of `\d`).

## Validation Result

### Success

```python
{
    "passed": True,
    "message": "Regex pattern check passed",
    "details": {
        "pattern": "@",
        "match_count": 2,
        "mismatch_count": 0,
        "total_count": 2
    }
}
```

### Failure

```python
{
    "passed": False,
    "message": "1 value(s) do not match pattern '@'",
    "details": {
        "pattern": "@",
        "match_count": 1,
        "mismatch_count": 1,
        "total_count": 2
    }
}
```

## Common Patterns

### Email Validation

```python
# Simple - contains @ and .
RegexPatternConstraint(column="email", pattern=r"@.*\.")

# More strict
RegexPatternConstraint(column="email", pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
```

### Phone Numbers

```python
# US format: 123-456-7890
RegexPatternConstraint(column="phone", pattern=r"^\d{3}-\d{3}-\d{4}$")

# International: +1-123-456-7890
RegexPatternConstraint(column="phone", pattern=r"^\+\d{1,3}-\d{3}-\d{3}-\d{4}$")
```

### Product Codes

```python
# Format: ABC-1234
RegexPatternConstraint(column="product_code", pattern=r"^[A-Z]{3}-\d{4}$")
```

### URLs

```python
# Basic URL validation
RegexPatternConstraint(column="url", pattern=r"^https?://")
```

### Alphanumeric

```python
# Only letters and numbers
RegexPatternConstraint(column="username", pattern=r"^[a-zA-Z0-9]+$")
```

## Regex Syntax Quick Reference

| Pattern | Description |
|---------|-------------|
| `^` | Start of string |
| `$` | End of string |
| `.` | Any character |
| `\d` | Digit (0-9) |
| `\w` | Word character (a-z, A-Z, 0-9, _) |
| `\s` | Whitespace |
| `[abc]` | Character set (a, b, or c) |
| `[a-z]` | Range (any lowercase letter) |
| `*` | Zero or more |
| `+` | One or more |
| `?` | Zero or one |
| `{n}` | Exactly n times |
| `{n,m}` | Between n and m times |
| `|` | OR |
| `()` | Grouping |

## Implementation Details

- Uses native Polars expression: `pl.col(column).str.contains(pattern)`
- Pattern matching is partial by default (matches if pattern found anywhere)
- Use `^` and `$` anchors for exact matching
- Null values are treated as matching (they pass validation)
- All non-null values must match for validation to succeed

## Notes

- Regex syntax follows Rust regex engine (similar to PCRE)
- Pattern matching is case-sensitive by default
- Null values are considered valid (use NullabilityConstraint if needed)
- Complex patterns may impact performance on large datasets

## See Also

- [Constraints Overview](index.md)
- [StringLengthConstraint](string-length.md) - For length validation
- [ValueSetConstraint](value-set.md) - For categorical validation
