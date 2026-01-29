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


class UniquenessConstraint(Constraint):
    """Constraint for checking uniqueness of values in a column."""

    def __init__(
        self,
        column: str,
        min_unique_ratio: Optional[float] = None,
        min_unique_count: Optional[int] = None,
    ):
        """Initialize the uniqueness constraint.
        
        Args:
            column: The column name to check.
            min_unique_ratio: Minimum ratio of unique values (0.0 to 1.0).
            min_unique_count: Minimum count of unique values.
        """
        super().__init__(column)
        self.min_unique_ratio = min_unique_ratio
        self.min_unique_count = min_unique_count

        if min_unique_ratio is None and min_unique_count is None:
            raise ValueError("Must specify either min_unique_ratio or min_unique_count")

    def validate(self, df: pl.DataFrame) -> Dict[str, Any]:
        """Validate uniqueness constraint."""
        if self.column not in df.columns:
            return {
                "passed": False,
                "message": f"Column '{self.column}' not found in dataframe",
                "details": {},
            }

        # Use native Polars expressions
        unique_count = df.select(pl.col(self.column).n_unique()).item()
        total_count = len(df)
        unique_ratio = unique_count / total_count if total_count > 0 else 0.0

        passed = True
        messages = []

        if self.min_unique_count is not None:
            if unique_count < self.min_unique_count:
                passed = False
                messages.append(
                    f"Unique count {unique_count} is below minimum {self.min_unique_count}"
                )

        if self.min_unique_ratio is not None:
            if unique_ratio < self.min_unique_ratio:
                passed = False
                messages.append(
                    f"Unique ratio {unique_ratio:.4f} is below minimum {self.min_unique_ratio:.4f}"
                )

        message = "; ".join(messages) if messages else "Uniqueness check passed"

        return {
            "passed": passed,
            "message": message,
            "details": {
                "unique_count": unique_count,
                "total_count": total_count,
                "unique_ratio": unique_ratio,
            },
        }


class StandardDeviationConstraint(Constraint):
    """Constraint for checking standard deviation values in a column."""

    def __init__(
        self,
        column: str,
        lower_bound: Optional[float] = None,
        upper_bound: Optional[float] = None,
    ):
        """Initialize the standard deviation constraint.
        
        Args:
            column: The column name to check.
            lower_bound: The minimum acceptable standard deviation value.
            upper_bound: The maximum acceptable standard deviation value.
        """
        super().__init__(column)
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound

        if lower_bound is None and upper_bound is None:
            raise ValueError("Must specify at least one bound (lower or upper)")

    def validate(self, df: pl.DataFrame) -> Dict[str, Any]:
        """Validate standard deviation constraint."""
        if self.column not in df.columns:
            return {
                "passed": False,
                "message": f"Column '{self.column}' not found in dataframe",
                "details": {},
            }

        # Use native Polars expression
        actual_std = df.select(pl.col(self.column).std()).item()

        if actual_std is None:
            return {
                "passed": True,
                "message": "Column contains only null values",
                "details": {"actual_std": None},
            }

        passed = True
        messages = []

        if self.lower_bound is not None and actual_std < self.lower_bound:
            passed = False
            messages.append(
                f"Standard deviation {actual_std} is below lower bound {self.lower_bound}"
            )

        if self.upper_bound is not None and actual_std > self.upper_bound:
            passed = False
            messages.append(
                f"Standard deviation {actual_std} exceeds upper bound {self.upper_bound}"
            )

        message = "; ".join(messages) if messages else "Standard deviation check passed"

        return {
            "passed": passed,
            "message": message,
            "details": {
                "actual_std": actual_std,
                "lower_bound": self.lower_bound,
                "upper_bound": self.upper_bound,
            },
        }


class StringLengthConstraint(Constraint):
    """Constraint for checking string length in a column."""

    def __init__(
        self,
        column: str,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
    ):
        """Initialize the string length constraint.
        
        Args:
            column: The column name to check.
            min_length: Minimum acceptable string length.
            max_length: Maximum acceptable string length.
        """
        super().__init__(column)
        self.min_length = min_length
        self.max_length = max_length

        if min_length is None and max_length is None:
            raise ValueError("Must specify at least one of min_length or max_length")

    def validate(self, df: pl.DataFrame) -> Dict[str, Any]:
        """Validate string length constraint."""
        if self.column not in df.columns:
            return {
                "passed": False,
                "message": f"Column '{self.column}' not found in dataframe",
                "details": {},
            }

        # Check if column is all nulls
        non_null_count = df.select(pl.col(self.column).is_not_null().sum()).item()
        
        if non_null_count == 0:
            return {
                "passed": True,
                "message": "Column contains only null values",
                "details": {"min_length_found": None, "max_length_found": None},
            }

        # Use native Polars expressions
        lengths = df.select(pl.col(self.column).str.len_chars()).to_series()
        
        # Filter out nulls for min/max calculations
        non_null_lengths = lengths.drop_nulls()

        min_length_found = non_null_lengths.min()
        max_length_found = non_null_lengths.max()

        passed = True
        messages = []

        if self.min_length is not None and min_length_found < self.min_length:
            passed = False
            messages.append(
                f"Minimum string length {min_length_found} is below required minimum {self.min_length}"
            )

        if self.max_length is not None and max_length_found > self.max_length:
            passed = False
            messages.append(
                f"Maximum string length {max_length_found} exceeds allowed maximum {self.max_length}"
            )

        message = "; ".join(messages) if messages else "String length check passed"

        return {
            "passed": passed,
            "message": message,
            "details": {
                "min_length_found": min_length_found,
                "max_length_found": max_length_found,
                "min_length": self.min_length,
                "max_length": self.max_length,
            },
        }


class RegexPatternConstraint(Constraint):
    """Constraint for validating strings match a regex pattern."""

    def __init__(self, column: str, pattern: str):
        """Initialize the regex pattern constraint.
        
        Args:
            column: The column name to check.
            pattern: Regular expression pattern to match.
        """
        super().__init__(column)
        self.pattern = pattern

    def validate(self, df: pl.DataFrame) -> Dict[str, Any]:
        """Validate regex pattern constraint."""
        if self.column not in df.columns:
            return {
                "passed": False,
                "message": f"Column '{self.column}' not found in dataframe",
                "details": {},
            }

        # Use native Polars expression to count matches
        # Contains returns true if pattern is found anywhere in the string
        matches = df.select(
            pl.col(self.column).str.contains(self.pattern).fill_null(True)
        ).to_series()
        
        total_count = len(df)
        match_count = matches.sum()
        mismatch_count = total_count - match_count

        passed = mismatch_count == 0
        message = (
            "Regex pattern check passed"
            if passed
            else f"{mismatch_count} value(s) do not match pattern '{self.pattern}'"
        )

        return {
            "passed": passed,
            "message": message,
            "details": {
                "pattern": self.pattern,
                "match_count": match_count,
                "mismatch_count": mismatch_count,
                "total_count": total_count,
            },
        }


class ValueSetConstraint(Constraint):
    """Constraint for validating values are within a predefined set."""

    def __init__(self, column: str, allowed_values: list):
        """Initialize the value set constraint.
        
        Args:
            column: The column name to check.
            allowed_values: List of allowed values.
        """
        super().__init__(column)
        self.allowed_values = allowed_values

        if not allowed_values:
            raise ValueError("allowed_values must contain at least one value")

    def validate(self, df: pl.DataFrame) -> Dict[str, Any]:
        """Validate value set constraint."""
        if self.column not in df.columns:
            return {
                "passed": False,
                "message": f"Column '{self.column}' not found in dataframe",
                "details": {},
            }

        # Use native Polars expression to check if values are in the allowed set
        is_in_set = df.select(
            pl.col(self.column).is_in(self.allowed_values).fill_null(True)
        ).to_series()
        
        total_count = len(df)
        valid_count = is_in_set.sum()
        invalid_count = total_count - valid_count

        passed = invalid_count == 0
        
        if passed:
            message = "Value set check passed"
        else:
            # Get unique invalid values for better error message
            invalid_values = df.filter(
                ~pl.col(self.column).is_in(self.allowed_values) & pl.col(self.column).is_not_null()
            ).select(pl.col(self.column).unique()).to_series().to_list()
            message = f"{invalid_count} value(s) not in allowed set. Invalid values: {invalid_values[:5]}"

        return {
            "passed": passed,
            "message": message,
            "details": {
                "allowed_values": self.allowed_values,
                "valid_count": valid_count,
                "invalid_count": invalid_count,
                "total_count": total_count,
            },
        }


class RowCountConstraint(Constraint):
    """Constraint for validating DataFrame row count."""

    def __init__(
        self,
        column: str,  # Required by base class, but not used
        min_rows: Optional[int] = None,
        max_rows: Optional[int] = None,
    ):
        """Initialize the row count constraint.
        
        Args:
            column: Not used for this constraint, but required by base class.
            min_rows: Minimum acceptable row count.
            max_rows: Maximum acceptable row count.
        """
        super().__init__(column)
        self.min_rows = min_rows
        self.max_rows = max_rows

        if min_rows is None and max_rows is None:
            raise ValueError("Must specify at least one of min_rows or max_rows")

    def validate(self, df: pl.DataFrame) -> Dict[str, Any]:
        """Validate row count constraint."""
        row_count = len(df)

        passed = True
        messages = []

        if self.min_rows is not None and row_count < self.min_rows:
            passed = False
            messages.append(
                f"Row count {row_count} is below minimum {self.min_rows}"
            )

        if self.max_rows is not None and row_count > self.max_rows:
            passed = False
            messages.append(
                f"Row count {row_count} exceeds maximum {self.max_rows}"
            )

        message = "; ".join(messages) if messages else "Row count check passed"

        return {
            "passed": passed,
            "message": message,
            "details": {
                "row_count": row_count,
                "min_rows": self.min_rows,
                "max_rows": self.max_rows,
            },
        }
