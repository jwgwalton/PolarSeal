"""
Example demonstrating the new constraints in PolarSeal.

This example showcases:
- UniquenessConstraint
- StandardDeviationConstraint
- StringLengthConstraint
- RegexPatternConstraint
- ValueSetConstraint
- RowCountConstraint
"""

import polars as pl
from polarseal import (
    load_schema,
    SchemaValidator,
    ValidationError,
    UniquenessConstraint,
    StandardDeviationConstraint,
    StringLengthConstraint,
    RegexPatternConstraint,
    ValueSetConstraint,
    RowCountConstraint,
)


def example_uniqueness_constraint():
    """Example: Validate that user IDs are mostly unique."""
    print("\n=== Uniqueness Constraint Example ===")
    
    # Sample data with high uniqueness
    df = pl.DataFrame({
        "user_id": [f"user_{i}" for i in range(1000)]
    })
    
    # Create constraint - require 95% unique values
    constraint = UniquenessConstraint(
        column="user_id",
        min_unique_ratio=0.95
    )
    
    result = constraint.validate(df)
    print(f"Passed: {result['passed']}")
    print(f"Unique ratio: {result['details']['unique_ratio']:.2%}")


def example_standard_deviation_constraint():
    """Example: Validate temperature readings have reasonable variance."""
    print("\n=== Standard Deviation Constraint Example ===")
    
    # Sample temperature data
    df = pl.DataFrame({
        "temperature": [20.1, 20.5, 19.8, 21.2, 20.3, 19.9, 20.7, 20.4]
    })
    
    # Create constraint - expect std dev between 0.2 and 1.0
    constraint = StandardDeviationConstraint(
        column="temperature",
        lower_bound=0.2,
        upper_bound=1.0
    )
    
    result = constraint.validate(df)
    print(f"Passed: {result['passed']}")
    print(f"Actual std dev: {result['details']['actual_std']:.4f}")


def example_string_length_constraint():
    """Example: Validate product codes have proper length."""
    print("\n=== String Length Constraint Example ===")
    
    df = pl.DataFrame({
        "product_code": ["ABC123", "DEF456", "GHI789", "JKL012"]
    })
    
    # Create constraint - codes must be exactly 6 characters
    constraint = StringLengthConstraint(
        column="product_code",
        min_length=6,
        max_length=6
    )
    
    result = constraint.validate(df)
    print(f"Passed: {result['passed']}")
    print(f"Min length: {result['details']['min_length_found']}")
    print(f"Max length: {result['details']['max_length_found']}")


def example_regex_pattern_constraint():
    """Example: Validate email addresses contain @ symbol."""
    print("\n=== Regex Pattern Constraint Example ===")
    
    df = pl.DataFrame({
        "email": [
            "user1@example.com",
            "user2@test.org",
            "admin@company.net"
        ]
    })
    
    # Create constraint - emails must contain @ symbol
    constraint = RegexPatternConstraint(
        column="email",
        pattern=r"@.*\."  # @ followed eventually by .
    )
    
    result = constraint.validate(df)
    print(f"Passed: {result['passed']}")
    print(f"Matches: {result['details']['match_count']}/{result['details']['total_count']}")


def example_value_set_constraint():
    """Example: Validate status values are from allowed set."""
    print("\n=== Value Set Constraint Example ===")
    
    df = pl.DataFrame({
        "status": ["active", "inactive", "active", "pending", "active"]
    })
    
    # Create constraint - only specific statuses allowed
    constraint = ValueSetConstraint(
        column="status",
        allowed_values=["active", "inactive", "pending", "suspended"]
    )
    
    result = constraint.validate(df)
    print(f"Passed: {result['passed']}")
    print(f"Valid values: {result['details']['valid_count']}/{result['details']['total_count']}")


def example_row_count_constraint():
    """Example: Validate DataFrame has acceptable number of rows."""
    print("\n=== Row Count Constraint Example ===")
    
    df = pl.DataFrame({
        "id": range(100)
    })
    
    # Create constraint - expect between 50 and 200 rows
    constraint = RowCountConstraint(
        column="",  # Not used for row count
        min_rows=50,
        max_rows=200
    )
    
    result = constraint.validate(df)
    print(f"Passed: {result['passed']}")
    print(f"Row count: {result['details']['row_count']}")


def example_advanced_schema():
    """Example: Load and validate using the advanced schema."""
    print("\n=== Advanced Schema Example ===")
    
    # Create sample data that should pass validation
    df = pl.DataFrame({
        "user_id": [f"user_{i:03d}" for i in range(1, 101)],
        "email": [f"user{i}@example.com" for i in range(1, 101)],
        "status": ["active"] * 50 + ["inactive"] * 30 + ["pending"] * 20,
        "age": [25 + i % 40 for i in range(100)],
        "score": [70.0 + i % 25 for i in range(100)]
    })
    
    try:
        validator = load_schema("examples/advanced_schema.json")
        result = validator.validate(df)
        print("✓ All validations passed!")
    except ValidationError as e:
        print(f"✗ Validation failed: {e}")
        for failure in e.failures:
            print(f"  - {failure['constraint']}: {failure['message']}")


def example_programmatic_new_constraints():
    """Example: Use new constraints programmatically."""
    print("\n=== Programmatic New Constraints Example ===")
    
    df = pl.DataFrame({
        "transaction_id": [f"TXN-{i:04d}" for i in range(1, 51)],
        "amount": [100.0 + i * 10 for i in range(50)],
        "category": ["food"] * 20 + ["transport"] * 15 + ["entertainment"] * 15
    })
    
    # Create multiple new constraint types
    constraints = [
        # Transaction IDs should be unique
        UniquenessConstraint(
            column="transaction_id",
            min_unique_ratio=1.0
        ),
        # Transaction IDs should match pattern
        RegexPatternConstraint(
            column="transaction_id",
            pattern=r"^TXN-\d{4}$"
        ),
        # String length should be exactly 8 characters
        StringLengthConstraint(
            column="transaction_id",
            min_length=8,
            max_length=8
        ),
        # Amount variance should be reasonable
        StandardDeviationConstraint(
            column="amount",
            lower_bound=50.0,
            upper_bound=300.0
        ),
        # Categories must be from predefined set
        ValueSetConstraint(
            column="category",
            allowed_values=["food", "transport", "entertainment", "utilities"]
        ),
        # Should have between 10 and 100 transactions
        RowCountConstraint(
            column="",
            min_rows=10,
            max_rows=100
        )
    ]
    
    field_definitions = {
        "transaction_id": "String",
        "amount": "Float64",
        "category": "String"
    }
    
    validator = SchemaValidator(constraints, field_definitions)
    
    try:
        result = validator.validate(df)
        print("✓ All validations passed!")
        print(f"  - Validated {len(df)} transactions")
        print(f"  - Ran {len(constraints)} constraint checks")
    except ValidationError as e:
        print(f"✗ Validation failed: {e}")


if __name__ == "__main__":
    print("=" * 60)
    print("PolarSeal New Constraints Examples")
    print("=" * 60)
    
    example_uniqueness_constraint()
    example_standard_deviation_constraint()
    example_string_length_constraint()
    example_regex_pattern_constraint()
    example_value_set_constraint()
    example_row_count_constraint()
    example_advanced_schema()
    example_programmatic_new_constraints()
    
    print("\n" + "=" * 60)
    print("All examples completed!")
    print("=" * 60)
