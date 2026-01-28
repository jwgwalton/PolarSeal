"""Schema validator for Polars DataFrames."""

from typing import Any, Dict, List, Optional
import polars as pl

from .constraints import Constraint


class ValidationError(Exception):
    """Exception raised when DataFrame validation fails."""

    def __init__(self, message: str, failures: Optional[List[Dict[str, Any]]] = None):
        """Initialize the validation error.
        
        Args:
            message: Error message describing the validation failure.
            failures: Optional list of failed constraint results.
        """
        super().__init__(message)
        self.failures = failures or []

    def __str__(self):
        """Return string representation of the error."""
        lines = [super().__str__()]
        if self.failures:
            lines.append("\nFailed constraints:")
            for failure in self.failures:
                lines.append(f"  - {failure.get('constraint', 'Unknown')}: {failure['message']}")
        return "\n".join(lines)


class ValidationResult:
    """Result of a schema validation."""

    def __init__(self, results: List[Dict[str, Any]]):
        """Initialize the validation result.
        
        Args:
            results: List of individual constraint validation results.
        """
        self.results = results
        self.passed = all(r["passed"] for r in results)

    def __bool__(self):
        """Return True if validation passed."""
        return self.passed

    def __repr__(self):
        """String representation of the validation result."""
        status = "PASSED" if self.passed else "FAILED"
        return f"ValidationResult(status={status}, total={len(self.results)})"

    def to_dict(self) -> Dict[str, Any]:
        """Convert the result to a dictionary.
        
        Returns:
            Dictionary containing validation results.
        """
        return {
            "passed": self.passed,
            "total_constraints": len(self.results),
            "passed_constraints": sum(1 for r in self.results if r["passed"]),
            "failed_constraints": sum(1 for r in self.results if not r["passed"]),
            "results": self.results,
        }

    def get_failures(self) -> List[Dict[str, Any]]:
        """Get only the failed constraint results.
        
        Returns:
            List of failed constraint results.
        """
        return [r for r in self.results if not r["passed"]]

    def summary(self) -> str:
        """Get a summary of the validation results.
        
        Returns:
            A string summary of the results.
        """
        lines = [f"Validation {'PASSED' if self.passed else 'FAILED'}"]
        lines.append(f"Total constraints: {len(self.results)}")
        lines.append(f"Passed: {sum(1 for r in self.results if r['passed'])}")
        lines.append(f"Failed: {sum(1 for r in self.results if not r['passed'])}")
        
        if not self.passed:
            lines.append("\nFailed constraints:")
            for result in self.get_failures():
                lines.append(f"  - {result.get('constraint', 'Unknown')}: {result['message']}")
        
        return "\n".join(lines)


class SchemaValidator:
    """Validator for applying constraints to Polars DataFrames."""

    def __init__(self, constraints: List[Constraint], field_definitions: Optional[Dict[str, str]] = None):
        """Initialize the schema validator.
        
        Args:
            constraints: List of Constraint objects to apply.
            field_definitions: Optional dictionary mapping field names to their expected types.
        """
        self.constraints = constraints
        self.field_definitions = field_definitions or {}

    def validate(self, df: pl.DataFrame, raise_on_error: bool = True) -> ValidationResult:
        """Validate a DataFrame against the schema.
        
        Args:
            df: The Polars DataFrame to validate.
            raise_on_error: If True, raises ValidationError on validation failure.
                           If False, returns ValidationResult (legacy behavior).
            
        Returns:
            A ValidationResult object containing the results.
            
        Raises:
            ValidationError: If validation fails and raise_on_error is True.
        """
        results = []
        
        # First, validate field types if field definitions are provided
        if self.field_definitions:
            type_errors = self._validate_field_types(df)
            if type_errors:
                if raise_on_error:
                    raise ValidationError(
                        f"Schema validation failed: {len(type_errors)} type error(s)",
                        type_errors
                    )
                else:
                    results.extend(type_errors)
        
        # Then validate constraints
        for constraint in self.constraints:
            result = constraint.validate(df)
            # Add constraint information
            result["constraint"] = f"{constraint.__class__.__name__}({constraint.column})"
            results.append(result)
        
        validation_result = ValidationResult(results)
        
        # Raise ValidationError if validation failed and raise_on_error is True
        if raise_on_error and not validation_result.passed:
            failures = validation_result.get_failures()
            raise ValidationError(
                f"Validation failed: {len(failures)} constraint(s) not satisfied",
                failures
            )
        
        return validation_result
    
    def _validate_field_types(self, df: pl.DataFrame) -> List[Dict[str, Any]]:
        """Validate that DataFrame fields match expected types.
        
        Args:
            df: The Polars DataFrame to validate.
            
        Returns:
            List of validation errors for type mismatches.
        """
        errors = []
        
        # Check all defined fields are present
        for field_name, expected_type in self.field_definitions.items():
            if field_name not in df.columns:
                errors.append({
                    "passed": False,
                    "message": f"Required field '{field_name}' not found in DataFrame",
                    "details": {"field": field_name, "expected_type": expected_type},
                    "constraint": f"FieldType({field_name})"
                })
            else:
                # Check type matches
                actual_type = str(df[field_name].dtype)
                if not self._types_match(actual_type, expected_type):
                    errors.append({
                        "passed": False,
                        "message": f"Field '{field_name}' has type '{actual_type}', expected '{expected_type}'",
                        "details": {
                            "field": field_name,
                            "expected_type": expected_type,
                            "actual_type": actual_type
                        },
                        "constraint": f"FieldType({field_name})"
                    })
        
        return errors
    
    def _types_match(self, actual_type: str, expected_type: str) -> bool:
        """Check if actual type matches expected type.
        
        Args:
            actual_type: The actual Polars dtype as string.
            expected_type: The expected type name.
            
        Returns:
            True if types match, False otherwise.
        """
        # Direct match
        if actual_type == expected_type:
            return True
        
        # Handle common type aliases
        type_aliases = {
            "Int64": ["Int64", "i64"],
            "Int32": ["Int32", "i32"],
            "Int16": ["Int16", "i16"],
            "Int8": ["Int8", "i8"],
            "UInt64": ["UInt64", "u64"],
            "UInt32": ["UInt32", "u32"],
            "UInt16": ["UInt16", "u16"],
            "UInt8": ["UInt8", "u8"],
            "Float64": ["Float64", "f64"],
            "Float32": ["Float32", "f32"],
            "String": ["String", "Utf8", "str"],
            "Boolean": ["Boolean", "Bool"],
        }
        
        for canonical, aliases in type_aliases.items():
            if expected_type in aliases and actual_type in aliases:
                return True
        
        return False
