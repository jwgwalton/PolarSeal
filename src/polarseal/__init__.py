"""PolarSeal - A data validation library built on Polars."""

from .validator import SchemaValidator, ValidationError
from .constraints import (
    NullabilityConstraint,
    MaximumValueConstraint,
    MinimumValueConstraint,
    MedianConstraint,
    MeanConstraint,
    PercentileConstraint,
    UniquenessConstraint,
    StandardDeviationConstraint,
    StringLengthConstraint,
    RegexPatternConstraint,
    ValueSetConstraint,
    RowCountConstraint,
)
from .schema import load_schema

__version__ = "0.1.0"

__all__ = [
    "SchemaValidator",
    "ValidationError",
    "NullabilityConstraint",
    "MaximumValueConstraint",
    "MinimumValueConstraint",
    "MedianConstraint",
    "MeanConstraint",
    "PercentileConstraint",
    "UniquenessConstraint",
    "StandardDeviationConstraint",
    "StringLengthConstraint",
    "RegexPatternConstraint",
    "ValueSetConstraint",
    "RowCountConstraint",
    "load_schema",
]
