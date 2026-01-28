"""Base constraint classes and implementations."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import polars as pl


class Constraint(ABC):
    """Base class for all constraints."""

    def __init__(self, column: str):
        """Initialize the constraint.
        
        Args:
            column: The column name to apply the constraint to.
        """
        self.column = column

    @abstractmethod
    def validate(self, df: pl.DataFrame) -> Dict[str, Any]:
        """Validate the constraint against a dataframe.
        
        Args:
            df: The Polars DataFrame to validate.
            
        Returns:
            A dictionary with validation results containing:
                - passed: bool indicating if validation passed
                - message: str describing the result
                - details: dict with additional information
        """
        pass


class NullabilityConstraint(Constraint):
    """Constraint for checking null values in a column."""

    def __init__(
        self,
        column: str,
        max_null_ratio: Optional[float] = None,
        max_null_count: Optional[int] = None,
    ):
        """Initialize the nullability constraint.
        
        Args:
            column: The column name to check.
            max_null_ratio: Maximum acceptable ratio of null values (0.0 to 1.0).
            max_null_count: Maximum acceptable count of null values.
        """
        super().__init__(column)
        self.max_null_ratio = max_null_ratio
        self.max_null_count = max_null_count

        if max_null_ratio is None and max_null_count is None:
            raise ValueError("Must specify either max_null_ratio or max_null_count")

    def validate(self, df: pl.DataFrame) -> Dict[str, Any]:
        """Validate null constraints."""
        if self.column not in df.columns:
            return {
                "passed": False,
                "message": f"Column '{self.column}' not found in dataframe",
                "details": {},
            }

        # Use native Polars expressions
        null_count = df.select(pl.col(self.column).is_null().sum()).item()
        total_count = len(df)
        null_ratio = null_count / total_count if total_count > 0 else 0.0

        passed = True
        messages = []

        if self.max_null_count is not None:
            if null_count > self.max_null_count:
                passed = False
                messages.append(
                    f"Null count {null_count} exceeds maximum {self.max_null_count}"
                )

        if self.max_null_ratio is not None:
            if null_ratio > self.max_null_ratio:
                passed = False
                messages.append(
                    f"Null ratio {null_ratio:.4f} exceeds maximum {self.max_null_ratio:.4f}"
                )

        message = "; ".join(messages) if messages else "Nullability check passed"

        return {
            "passed": passed,
            "message": message,
            "details": {
                "null_count": null_count,
                "total_count": total_count,
                "null_ratio": null_ratio,
            },
        }


class MaximumValueConstraint(Constraint):
    """Constraint for checking maximum values in a column."""

    def __init__(self, column: str, max_value: float):
        """Initialize the maximum value constraint.
        
        Args:
            column: The column name to check.
            max_value: The maximum acceptable value.
        """
        super().__init__(column)
        self.max_value = max_value

    def validate(self, df: pl.DataFrame) -> Dict[str, Any]:
        """Validate maximum value constraint."""
        if self.column not in df.columns:
            return {
                "passed": False,
                "message": f"Column '{self.column}' not found in dataframe",
                "details": {},
            }

        # Use native Polars expression
        actual_max = df.select(pl.col(self.column).max()).item()

        if actual_max is None:
            return {
                "passed": True,
                "message": "Column contains only null values",
                "details": {"actual_max": None},
            }

        passed = actual_max <= self.max_value
        message = (
            f"Maximum value check passed"
            if passed
            else f"Maximum value {actual_max} exceeds limit {self.max_value}"
        )

        return {
            "passed": passed,
            "message": message,
            "details": {"actual_max": actual_max, "max_value": self.max_value},
        }


class MinimumValueConstraint(Constraint):
    """Constraint for checking minimum values in a column."""

    def __init__(self, column: str, min_value: float):
        """Initialize the minimum value constraint.
        
        Args:
            column: The column name to check.
            min_value: The minimum acceptable value.
        """
        super().__init__(column)
        self.min_value = min_value

    def validate(self, df: pl.DataFrame) -> Dict[str, Any]:
        """Validate minimum value constraint."""
        if self.column not in df.columns:
            return {
                "passed": False,
                "message": f"Column '{self.column}' not found in dataframe",
                "details": {},
            }

        # Use native Polars expression
        actual_min = df.select(pl.col(self.column).min()).item()

        if actual_min is None:
            return {
                "passed": True,
                "message": "Column contains only null values",
                "details": {"actual_min": None},
            }

        passed = actual_min >= self.min_value
        message = (
            f"Minimum value check passed"
            if passed
            else f"Minimum value {actual_min} is below limit {self.min_value}"
        )

        return {
            "passed": passed,
            "message": message,
            "details": {"actual_min": actual_min, "min_value": self.min_value},
        }


class MedianConstraint(Constraint):
    """Constraint for checking median values in a column."""

    def __init__(
        self,
        column: str,
        lower_bound: Optional[float] = None,
        upper_bound: Optional[float] = None,
    ):
        """Initialize the median constraint.
        
        Args:
            column: The column name to check.
            lower_bound: The minimum acceptable median value.
            upper_bound: The maximum acceptable median value.
        """
        super().__init__(column)
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound

        if lower_bound is None and upper_bound is None:
            raise ValueError("Must specify at least one bound (lower or upper)")

    def validate(self, df: pl.DataFrame) -> Dict[str, Any]:
        """Validate median constraint."""
        if self.column not in df.columns:
            return {
                "passed": False,
                "message": f"Column '{self.column}' not found in dataframe",
                "details": {},
            }

        # Use native Polars expression
        actual_median = df.select(pl.col(self.column).median()).item()

        if actual_median is None:
            return {
                "passed": True,
                "message": "Column contains only null values",
                "details": {"actual_median": None},
            }

        passed = True
        messages = []

        if self.lower_bound is not None and actual_median < self.lower_bound:
            passed = False
            messages.append(
                f"Median {actual_median} is below lower bound {self.lower_bound}"
            )

        if self.upper_bound is not None and actual_median > self.upper_bound:
            passed = False
            messages.append(
                f"Median {actual_median} exceeds upper bound {self.upper_bound}"
            )

        message = "; ".join(messages) if messages else "Median check passed"

        return {
            "passed": passed,
            "message": message,
            "details": {
                "actual_median": actual_median,
                "lower_bound": self.lower_bound,
                "upper_bound": self.upper_bound,
            },
        }


class MeanConstraint(Constraint):
    """Constraint for checking mean values in a column."""

    def __init__(
        self,
        column: str,
        lower_bound: Optional[float] = None,
        upper_bound: Optional[float] = None,
    ):
        """Initialize the mean constraint.
        
        Args:
            column: The column name to check.
            lower_bound: The minimum acceptable mean value.
            upper_bound: The maximum acceptable mean value.
        """
        super().__init__(column)
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound

        if lower_bound is None and upper_bound is None:
            raise ValueError("Must specify at least one bound (lower or upper)")

    def validate(self, df: pl.DataFrame) -> Dict[str, Any]:
        """Validate mean constraint."""
        if self.column not in df.columns:
            return {
                "passed": False,
                "message": f"Column '{self.column}' not found in dataframe",
                "details": {},
            }

        # Use native Polars expression
        actual_mean = df.select(pl.col(self.column).mean()).item()

        if actual_mean is None:
            return {
                "passed": True,
                "message": "Column contains only null values",
                "details": {"actual_mean": None},
            }

        passed = True
        messages = []

        if self.lower_bound is not None and actual_mean < self.lower_bound:
            passed = False
            messages.append(
                f"Mean {actual_mean} is below lower bound {self.lower_bound}"
            )

        if self.upper_bound is not None and actual_mean > self.upper_bound:
            passed = False
            messages.append(
                f"Mean {actual_mean} exceeds upper bound {self.upper_bound}"
            )

        message = "; ".join(messages) if messages else "Mean check passed"

        return {
            "passed": passed,
            "message": message,
            "details": {
                "actual_mean": actual_mean,
                "lower_bound": self.lower_bound,
                "upper_bound": self.upper_bound,
            },
        }


class PercentileConstraint(Constraint):
    """Constraint for checking percentile values in a column."""

    def __init__(
        self,
        column: str,
        percentile: float,
        lower_bound: Optional[float] = None,
        upper_bound: Optional[float] = None,
    ):
        """Initialize the percentile constraint.
        
        Args:
            column: The column name to check.
            percentile: The percentile to check (0.0 to 1.0).
            lower_bound: The minimum acceptable percentile value.
            upper_bound: The maximum acceptable percentile value.
        """
        super().__init__(column)
        self.percentile = percentile
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound

        if not 0.0 <= percentile <= 1.0:
            raise ValueError("Percentile must be between 0.0 and 1.0")

        if lower_bound is None and upper_bound is None:
            raise ValueError("Must specify at least one bound (lower or upper)")

    def validate(self, df: pl.DataFrame) -> Dict[str, Any]:
        """Validate percentile constraint."""
        if self.column not in df.columns:
            return {
                "passed": False,
                "message": f"Column '{self.column}' not found in dataframe",
                "details": {},
            }

        # Use native Polars expression
        actual_percentile = df.select(
            pl.col(self.column).quantile(self.percentile)
        ).item()

        if actual_percentile is None:
            return {
                "passed": True,
                "message": "Column contains only null values",
                "details": {"actual_percentile": None},
            }

        passed = True
        messages = []

        if self.lower_bound is not None and actual_percentile < self.lower_bound:
            passed = False
            messages.append(
                f"Percentile {self.percentile} value {actual_percentile} is below lower bound {self.lower_bound}"
            )

        if self.upper_bound is not None and actual_percentile > self.upper_bound:
            passed = False
            messages.append(
                f"Percentile {self.percentile} value {actual_percentile} exceeds upper bound {self.upper_bound}"
            )

        message = "; ".join(messages) if messages else "Percentile check passed"

        return {
            "passed": passed,
            "message": message,
            "details": {
                "actual_percentile": actual_percentile,
                "percentile": self.percentile,
                "lower_bound": self.lower_bound,
                "upper_bound": self.upper_bound,
            },
        }
