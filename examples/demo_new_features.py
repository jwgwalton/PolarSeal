"""
Demonstration of PolarSeal's new field-based schema format and ValidationError.

This script demonstrates:
1. Field-based schema with type validation
2. ValidationError exception on failure
3. Empty constraints list (type-only validation)
4. Type mismatch detection
5. Missing field detection
"""

import json
import tempfile
from pathlib import Path
import polars as pl
from polarseal import load_schema, ValidationError

print("=" * 70)
print("PolarSeal Demo - Field-Based Schema & ValidationError")
print("=" * 70)

# Demo 1: Complete validation with type and constraints
print("\n1. COMPLETE VALIDATION (Type + Constraints)")
print("-" * 70)

schema1 = {
    "fields": {
        "user_id": {
            "type": "Int64",
            "constraints": [
                {"type": "nullability", "max_null_ratio": 0.0}
            ]
        },
        "age": {
            "type": "Int64",
            "constraints": [
                {"type": "minimum_value", "min_value": 18},
                {"type": "maximum_value", "max_value": 100}
            ]
        },
        "score": {
            "type": "Float64",
            "constraints": [
                {"type": "mean", "lower_bound": 0, "upper_bound": 100}
            ]
        }
    }
}

df1 = pl.DataFrame({
    "user_id": [1, 2, 3, 4, 5],
    "age": [25, 30, 35, 40, 45],
    "score": [85.5, 90.2, 88.7, 92.1, 87.3],
})

print("DataFrame:")
print(df1)
print("\nValidating...")

with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
    json.dump(schema1, f)
    temp_path1 = f.name

try:
    validator = load_schema(temp_path1)
    result = validator.validate(df1)
    print("✓ PASSED - All types and constraints satisfied!")
except ValidationError as e:
    print(f"✗ FAILED - {e}")
finally:
    Path(temp_path1).unlink()

# Demo 2: Type-only validation (empty constraints)
print("\n\n2. TYPE-ONLY VALIDATION (Empty Constraints)")
print("-" * 70)

schema2 = {
    "fields": {
        "id": {
            "type": "Int64",
            "constraints": []
        },
        "name": {
            "type": "String",
            "constraints": []
        },
        "active": {
            "type": "Boolean",
            "constraints": []
        }
    }
}

df2 = pl.DataFrame({
    "id": [1, 2, 3],
    "name": ["Alice", "Bob", "Charlie"],
    "active": [True, False, True],
})

print("DataFrame:")
print(df2)
print("\nSchema requires: id (Int64), name (String), active (Boolean)")
print("Constraints: None (empty list)")
print("\nValidating...")

with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
    json.dump(schema2, f)
    temp_path2 = f.name

try:
    validator = load_schema(temp_path2)
    result = validator.validate(df2)
    print("✓ PASSED - All field types match!")
except ValidationError as e:
    print(f"✗ FAILED - {e}")
finally:
    Path(temp_path2).unlink()

# Demo 3: Type mismatch error
print("\n\n3. TYPE MISMATCH DETECTION")
print("-" * 70)

schema3 = {
    "fields": {
        "user_id": {
            "type": "Int64",
            "constraints": []
        }
    }
}

df3 = pl.DataFrame({
    "user_id": ["a", "b", "c"],  # String instead of Int64
})

print("DataFrame:")
print(df3)
print("\nSchema requires: user_id (Int64)")
print("Actual type: String")
print("\nValidating...")

with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
    json.dump(schema3, f)
    temp_path3 = f.name

try:
    validator = load_schema(temp_path3)
    result = validator.validate(df3)
    print("✓ PASSED")
except ValidationError as e:
    print(f"✗ FAILED - Type mismatch detected!")
    print(f"\nError details:\n{e}")
finally:
    Path(temp_path3).unlink()

# Demo 4: Missing field error
print("\n\n4. MISSING FIELD DETECTION")
print("-" * 70)

schema4 = {
    "fields": {
        "user_id": {
            "type": "Int64",
            "constraints": []
        },
        "email": {
            "type": "String",
            "constraints": []
        }
    }
}

df4 = pl.DataFrame({
    "user_id": [1, 2, 3],
    # email field is missing!
})

print("DataFrame:")
print(df4)
print("\nSchema requires: user_id (Int64), email (String)")
print("Missing: email")
print("\nValidating...")

with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
    json.dump(schema4, f)
    temp_path4 = f.name

try:
    validator = load_schema(temp_path4)
    result = validator.validate(df4)
    print("✓ PASSED")
except ValidationError as e:
    print(f"✗ FAILED - Missing field detected!")
    print(f"\nError details:\n{e}")
finally:
    Path(temp_path4).unlink()

# Demo 5: Constraint violation
print("\n\n5. CONSTRAINT VIOLATION")
print("-" * 70)

schema5 = {
    "fields": {
        "age": {
            "type": "Int64",
            "constraints": [
                {"type": "minimum_value", "min_value": 0},
                {"type": "maximum_value", "max_value": 120}
            ]
        }
    }
}

df5 = pl.DataFrame({
    "age": [25, 150, 35],  # 150 exceeds maximum
})

print("DataFrame:")
print(df5)
print("\nConstraints: age must be between 0 and 120")
print("Issue: age=150 exceeds maximum")
print("\nValidating...")

with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
    json.dump(schema5, f)
    temp_path5 = f.name

try:
    validator = load_schema(temp_path5)
    result = validator.validate(df5)
    print("✓ PASSED")
except ValidationError as e:
    print(f"✗ FAILED - Constraint violated!")
    print(f"\nError details:\n{e}")
finally:
    Path(temp_path5).unlink()

# Demo 6: Legacy behavior with raise_on_error=False
print("\n\n6. LEGACY BEHAVIOR (raise_on_error=False)")
print("-" * 70)

print("Using the same schema and data from Demo 5...")
print("But with raise_on_error=False\n")

with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
    json.dump(schema5, f)
    temp_path6 = f.name

try:
    validator = load_schema(temp_path6)
    result = validator.validate(df5, raise_on_error=False)
    
    print(f"Result: {result}")
    print(f"Passed: {result.passed}")
    print(f"\nFailed constraints:")
    for failure in result.get_failures():
        print(f"  - {failure['constraint']}: {failure['message']}")
finally:
    Path(temp_path6).unlink()

print("\n" + "=" * 70)
print("Demo completed!")
print("=" * 70)
