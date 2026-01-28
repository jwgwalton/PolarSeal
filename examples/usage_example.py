"""Example usage of PolarSeal validation library."""

import polars as pl
from polarseal import load_schema, ValidationError

# Example 1: Basic usage with new field-based schema format
print("=" * 60)
print("Example 1: User Data Validation with New Schema Format")
print("=" * 60)

# Create sample user data
user_df = pl.DataFrame({
    "user_id": [1, 2, 3, 4, 5],
    "email": ["user1@example.com", "user2@example.com", None, "user4@example.com", "user5@example.com"],
    "age": [25, 32, 28, 45, 38],
})

print("\nUser DataFrame:")
print(user_df)

# Load schema and validate (will raise ValidationError if validation fails)
try:
    validator = load_schema("examples/user_schema.json")
    result = validator.validate(user_df)
    print("\n✓ Validation passed!")
except ValidationError as e:
    print(f"\n✗ Validation failed: {e}")

# Example 2: Demonstrating ValidationError with failing data
print("\n" + "=" * 60)
print("Example 2: Handling ValidationError")
print("=" * 60)

# Create data that will fail validation
bad_df = pl.DataFrame({
    "user_id": [1, 2, 3],
    "email": ["user1@example.com", "user2@example.com", "user3@example.com"],
    "age": [25, 150, 28],  # 150 exceeds maximum of 120
})

print("\nDataFrame with invalid age:")
print(bad_df)

try:
    validator = load_schema("examples/user_schema.json")
    result = validator.validate(bad_df)
    print("\n✓ Validation passed!")
except ValidationError as e:
    print(f"\n✗ Validation failed!")
    print(f"\nError details:\n{e}")

# Example 3: Legacy behavior with raise_on_error=False
print("\n" + "=" * 60)
print("Example 3: Legacy Behavior (raise_on_error=False)")
print("=" * 60)

print("\nSame invalid DataFrame:")
print(bad_df)

validator = load_schema("examples/user_schema.json")
result = validator.validate(bad_df, raise_on_error=False)

print(f"\nValidation result: {result}")
print(f"Passed: {result.passed}")
print(f"\nFailed constraints:")
for failure in result.get_failures():
    print(f"  - {failure['constraint']}: {failure['message']}")

# Example 4: Type validation
print("\n" + "=" * 60)
print("Example 4: Type Validation")
print("=" * 60)

# Create data with wrong type
wrong_type_df = pl.DataFrame({
    "user_id": ["a", "b", "c"],  # String instead of Int64
    "email": ["user1@example.com", "user2@example.com", "user3@example.com"],
    "age": [25, 30, 35],
})

print("\nDataFrame with wrong type for user_id:")
print(wrong_type_df)

try:
    validator = load_schema("examples/user_schema.json")
    result = validator.validate(wrong_type_df)
    print("\n✓ Validation passed!")
except ValidationError as e:
    print(f"\n✗ Validation failed!")
    print(f"\nError details:\n{e}")

# Example 5: Programmatic constraint creation still works
print("\n" + "=" * 60)
print("Example 5: Programmatic Constraint Creation")
print("=" * 60)

from polarseal import (
    SchemaValidator,
    NullabilityConstraint,
    MaximumValueConstraint,
    MinimumValueConstraint,
    MeanConstraint,
)

# Create temperature data
temp_df = pl.DataFrame({
    "sensor_id": [f"S{i:03d}" for i in range(1, 21)],
    "temperature": [20.5, 21.3, 19.8, 22.1, 20.9, 21.5, 20.2, 22.8, 21.1, 20.7,
                   21.9, 20.3, 22.5, 21.7, 20.1, 22.3, 21.2, 20.8, 22.0, 21.4],
})

print("\nTemperature DataFrame (first 5 rows):")
print(temp_df.head())

# Create constraints programmatically with type definitions
constraints = [
    NullabilityConstraint(column="sensor_id", max_null_ratio=0.0),
    NullabilityConstraint(column="temperature", max_null_ratio=0.05),
    MinimumValueConstraint(column="temperature", min_value=15.0),
    MaximumValueConstraint(column="temperature", max_value=30.0),
    MeanConstraint(column="temperature", lower_bound=19.0, upper_bound=23.0),
]

# Define field types
field_definitions = {
    "sensor_id": "String",
    "temperature": "Float64"
}

validator = SchemaValidator(constraints, field_definitions)

try:
    result = validator.validate(temp_df)
    print("\n✓ Validation passed!")
except ValidationError as e:
    print(f"\n✗ Validation failed: {e}")

# Example 6: Field with empty constraints
print("\n" + "=" * 60)
print("Example 6: Field with Type but No Constraints")
print("=" * 60)

simple_df = pl.DataFrame({
    "id": [1, 2, 3, 4, 5],
    "name": ["Alice", "Bob", "Charlie", "David", "Eve"],
})

print("\nSimple DataFrame:")
print(simple_df)

# Create a simple schema with just type definitions, no constraints
import json
import tempfile
from pathlib import Path

simple_schema = {
    "fields": {
        "id": {
            "type": "Int64",
            "constraints": []
        },
        "name": {
            "type": "String",
            "constraints": []
        }
    }
}

with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
    json.dump(simple_schema, f)
    temp_path = f.name

try:
    validator = load_schema(temp_path)
    result = validator.validate(simple_df)
    print("\n✓ Validation passed! (type checking only, no constraints)")
finally:
    Path(temp_path).unlink()

print("\n" + "=" * 60)
print("Examples completed!")
print("=" * 60)
