# API Reference

Complete API reference for PolarSeal's programmatic interface.

## Core Classes

### SchemaValidator

Main class for validating DataFrames against a set of constraints.

```python
from polarseal import SchemaValidator

validator = SchemaValidator(
    constraints: List[Constraint],
    field_definitions: Optional[Dict[str, str]] = None
)
```

**Parameters:**
- `constraints` (List[Constraint]): List of constraint objects to validate
- `field_definitions` (Optional[Dict[str, str]]): Dictionary mapping column names to data types

**Methods:**

#### validate()

```python
result = validator.validate(
    df: pl.DataFrame,
    raise_on_error: bool = True
) -> ValidationResult
```

Validates a DataFrame against all constraints.

**Parameters:**
- `df` (pl.DataFrame): The DataFrame to validate
- `raise_on_error` (bool): If True, raises ValidationError on failure. If False, returns ValidationResult. Default: True

**Returns:**
- `ValidationResult`: Result object containing validation details

**Raises:**
- `ValidationError`: If validation fails and raise_on_error=True

**Example:**

```python
from polarseal import SchemaValidator, NullabilityConstraint
import polars as pl

df = pl.DataFrame({"user_id": [1, 2, 3]})
constraints = [NullabilityConstraint(column="user_id", max_null_ratio=0.0)]
validator = SchemaValidator(constraints)

try:
    result = validator.validate(df)
    print("Validation passed!")
except ValidationError as e:
    print(f"Validation failed: {e}")
```

### ValidationResult

Contains the results of validation.

**Attributes:**
- `passed` (bool): Whether all validations passed
- `results` (List[Dict]): List of individual constraint results
- `type_validation_results` (List[Dict]): Type validation results

**Methods:**

#### to_dict()

```python
result_dict = result.to_dict()
```

Returns validation result as a dictionary.

**Returns:**
- Dictionary with keys: `passed_constraints`, `failed_constraints`, `total_constraints`, `results`

#### summary()

```python
summary = result.summary()
```

Returns a human-readable summary string.

#### get_failures()

```python
failures = result.get_failures()
```

Returns only the failed constraint results.

**Returns:**
- List of failed constraint dictionaries

### ValidationError

Exception raised when validation fails (when raise_on_error=True).

**Attributes:**
- `failures` (List[Dict]): List of constraint failures
- `message` (str): Error message

**Example:**

```python
try:
    validator.validate(df)
except ValidationError as e:
    print(f"Error: {e}")
    for failure in e.failures:
        print(f"- {failure['constraint']}: {failure['message']}")
```

## Schema Loading

### load_schema()

```python
from polarseal import load_schema

validator = load_schema(schema_path: Union[str, Path]) -> SchemaValidator
```

Loads a validation schema from a JSON file.

**Parameters:**
- `schema_path` (Union[str, Path]): Path to the JSON schema file

**Returns:**
- `SchemaValidator`: Configured validator object

**Raises:**
- `FileNotFoundError`: If schema file doesn't exist
- `ValueError`: If schema is invalid

**Example:**

```python
from polarseal import load_schema

validator = load_schema("schema.json")
result = validator.validate(df)
```

## Constraint Classes

All constraint classes follow a common pattern:

```python
constraint = ConstraintType(
    column: str,
    # ... constraint-specific parameters
)

result = constraint.validate(df: pl.DataFrame) -> Dict[str, Any]
```

### Base Constraint

All constraints inherit from the `Constraint` base class.

```python
from polarseal.constraints import Constraint

class CustomConstraint(Constraint):
    def validate(self, df: pl.DataFrame) -> Dict[str, Any]:
        # Return {"passed": bool, "message": str, "details": dict}
        pass
```

### Data Quality Constraints

#### NullabilityConstraint

```python
from polarseal import NullabilityConstraint

constraint = NullabilityConstraint(
    column: str,
    max_null_ratio: Optional[float] = None,
    max_null_count: Optional[int] = None
)
```

[Full documentation →](constraints/nullability.md)

#### UniquenessConstraint

```python
from polarseal import UniquenessConstraint

constraint = UniquenessConstraint(
    column: str,
    min_unique_ratio: Optional[float] = None,
    min_unique_count: Optional[int] = None
)
```

[Full documentation →](constraints/uniqueness.md)

### Value Range Constraints

#### MinimumValueConstraint

```python
from polarseal import MinimumValueConstraint

constraint = MinimumValueConstraint(
    column: str,
    min_value: float
)
```

[Full documentation →](constraints/minimum-value.md)

#### MaximumValueConstraint

```python
from polarseal import MaximumValueConstraint

constraint = MaximumValueConstraint(
    column: str,
    max_value: float
)
```

[Full documentation →](constraints/maximum-value.md)

### Statistical Constraints

#### MeanConstraint

```python
from polarseal import MeanConstraint

constraint = MeanConstraint(
    column: str,
    lower_bound: Optional[float] = None,
    upper_bound: Optional[float] = None
)
```

[Full documentation →](constraints/mean.md)

#### MedianConstraint

```python
from polarseal import MedianConstraint

constraint = MedianConstraint(
    column: str,
    lower_bound: Optional[float] = None,
    upper_bound: Optional[float] = None
)
```

[Full documentation →](constraints/median.md)

#### PercentileConstraint

```python
from polarseal import PercentileConstraint

constraint = PercentileConstraint(
    column: str,
    percentile: float,  # 0.0 to 1.0
    lower_bound: Optional[float] = None,
    upper_bound: Optional[float] = None
)
```

[Full documentation →](constraints/percentile.md)

#### StandardDeviationConstraint

```python
from polarseal import StandardDeviationConstraint

constraint = StandardDeviationConstraint(
    column: str,
    lower_bound: Optional[float] = None,
    upper_bound: Optional[float] = None
)
```

[Full documentation →](constraints/standard-deviation.md)

### String Constraints

#### StringLengthConstraint

```python
from polarseal import StringLengthConstraint

constraint = StringLengthConstraint(
    column: str,
    min_length: Optional[int] = None,
    max_length: Optional[int] = None
)
```

[Full documentation →](constraints/string-length.md)

#### RegexPatternConstraint

```python
from polarseal import RegexPatternConstraint

constraint = RegexPatternConstraint(
    column: str,
    pattern: str
)
```

[Full documentation →](constraints/regex-pattern.md)

### Categorical Constraints

#### ValueSetConstraint

```python
from polarseal import ValueSetConstraint

constraint = ValueSetConstraint(
    column: str,
    allowed_values: list
)
```

[Full documentation →](constraints/value-set.md)

### DataFrame Constraints

#### RowCountConstraint

```python
from polarseal import RowCountConstraint

constraint = RowCountConstraint(
    column: str,  # Not used, use ""
    min_rows: Optional[int] = None,
    max_rows: Optional[int] = None
)
```

[Full documentation →](constraints/row-count.md)

## Validation Result Format

All constraint `validate()` methods return a dictionary:

```python
{
    "passed": bool,          # True if validation passed
    "message": str,          # Human-readable message
    "details": {             # Constraint-specific details
        # ... additional information
    }
}
```

## Complete Example

```python
import polars as pl
from polarseal import (
    SchemaValidator,
    ValidationError,
    NullabilityConstraint,
    UniquenessConstraint,
    MinimumValueConstraint,
    MaximumValueConstraint,
    MeanConstraint,
    ValueSetConstraint,
)

# Create DataFrame
df = pl.DataFrame({
    "user_id": [1, 2, 3, 4, 5],
    "status": ["active", "inactive", "active", "pending", "active"],
    "age": [25, 30, 35, 40, 45],
})

# Define constraints
constraints = [
    NullabilityConstraint(column="user_id", max_null_ratio=0.0),
    UniquenessConstraint(column="user_id", min_unique_ratio=1.0),
    MinimumValueConstraint(column="age", min_value=18),
    MaximumValueConstraint(column="age", max_value=120),
    MeanConstraint(column="age", lower_bound=20, upper_bound=50),
    ValueSetConstraint(column="status", allowed_values=["active", "inactive", "pending"]),
]

# Define field types
field_definitions = {
    "user_id": "Int64",
    "status": "String",
    "age": "Int64",
}

# Create validator
validator = SchemaValidator(constraints, field_definitions)

# Validate
try:
    result = validator.validate(df)
    print("✓ All validations passed!")
except ValidationError as e:
    print(f"✗ Validation failed: {e}")
    for failure in e.failures:
        print(f"  - {failure['constraint']}: {failure['message']}")
```

## See Also

- [Getting Started Guide](getting-started.md)
- [Constraints Reference](constraints/index.md)
- [Examples](../examples/)
