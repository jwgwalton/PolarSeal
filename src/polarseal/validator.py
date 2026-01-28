"""Schema validator for Polars DataFrames."""

from typing import Any, Dict, List
import polars as pl

from .constraints import Constraint


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

    def __init__(self, constraints: List[Constraint]):
        """Initialize the schema validator.
        
        Args:
            constraints: List of Constraint objects to apply.
        """
        self.constraints = constraints

    def validate(self, df: pl.DataFrame) -> ValidationResult:
        """Validate a DataFrame against the schema.
        
        Args:
            df: The Polars DataFrame to validate.
            
        Returns:
            A ValidationResult object containing the results.
        """
        results = []
        
        for constraint in self.constraints:
            result = constraint.validate(df)
            # Add constraint information
            result["constraint"] = f"{constraint.__class__.__name__}({constraint.column})"
            results.append(result)
        
        return ValidationResult(results)
