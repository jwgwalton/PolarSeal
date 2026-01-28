"""Example usage of PolarSeal validation library."""

import polars as pl
from polarseal import load_schema, SchemaValidator

# Example 1: Basic usage with user data
print("=" * 60)
print("Example 1: User Data Validation")
print("=" * 60)

# Create sample user data
user_df = pl.DataFrame({
    "user_id": [1, 2, 3, 4, 5],
    "email": ["user1@example.com", "user2@example.com", None, "user4@example.com", "user5@example.com"],
    "age": [25, 32, 28, 45, 38],
})

print("\nUser DataFrame:")
print(user_df)

# Load schema and validate
constraints = load_schema("examples/user_schema.json")
validator = SchemaValidator(constraints)
result = validator.validate(user_df)

print(f"\n{result.summary()}")

# Example 2: Sales data validation
print("\n" + "=" * 60)
print("Example 2: Sales Data Validation")
print("=" * 60)

# Create sample sales data
sales_df = pl.DataFrame({
    "transaction_id": list(range(1, 101)),
    "amount": [50 + i * 5 + (i % 10) * 2 for i in range(100)],
})

print("\nSales DataFrame (first 5 rows):")
print(sales_df.head())

# Load schema and validate
constraints = load_schema("examples/sales_schema.json")
validator = SchemaValidator(constraints)
result = validator.validate(sales_df)

print(f"\n{result.summary()}")

# Example 3: Programmatic constraint creation
print("\n" + "=" * 60)
print("Example 3: Programmatic Constraint Creation")
print("=" * 60)

from polarseal import (
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

# Create constraints programmatically
constraints = [
    NullabilityConstraint(column="sensor_id", max_null_ratio=0.0),
    NullabilityConstraint(column="temperature", max_null_ratio=0.05),
    MinimumValueConstraint(column="temperature", min_value=15.0),
    MaximumValueConstraint(column="temperature", max_value=30.0),
    MeanConstraint(column="temperature", lower_bound=19.0, upper_bound=23.0),
]

validator = SchemaValidator(constraints)
result = validator.validate(temp_df)

print(f"\n{result.summary()}")

# Example 4: Detailed result inspection
print("\n" + "=" * 60)
print("Example 4: Detailed Result Inspection")
print("=" * 60)

result_dict = result.to_dict()
print(f"\nValidation passed: {result_dict['passed']}")
print(f"Total constraints: {result_dict['total_constraints']}")
print(f"Passed constraints: {result_dict['passed_constraints']}")
print(f"Failed constraints: {result_dict['failed_constraints']}")

print("\nDetailed results:")
for i, constraint_result in enumerate(result_dict['results'], 1):
    print(f"\n{i}. {constraint_result['constraint']}")
    print(f"   Status: {'✓ PASSED' if constraint_result['passed'] else '✗ FAILED'}")
    print(f"   Message: {constraint_result['message']}")
    if constraint_result['details']:
        print(f"   Details: {constraint_result['details']}")
