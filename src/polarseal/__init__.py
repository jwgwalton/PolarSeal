"""PolarSeal - A data validation library built on Polars."""

from .validator import SchemaValidator
from .constraints import (
    NullabilityConstraint,
    MaximumValueConstraint,
    MinimumValueConstraint,
    MedianConstraint,
    MeanConstraint,
    PercentileConstraint,
)
from .schema import load_schema

__version__ = "0.1.0"

__all__ = [
    "SchemaValidator",
    "NullabilityConstraint",
    "MaximumValueConstraint",
    "MinimumValueConstraint",
    "MedianConstraint",
    "MeanConstraint",
    "PercentileConstraint",
    "load_schema",
]
