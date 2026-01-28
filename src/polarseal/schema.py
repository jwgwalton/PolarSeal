"""Schema loading from JSON files."""

import json
from pathlib import Path
from typing import Dict, List, Union

from .constraints import (
    Constraint,
    NullabilityConstraint,
    MaximumValueConstraint,
    MinimumValueConstraint,
    MedianConstraint,
    MeanConstraint,
    PercentileConstraint,
)


def load_schema(schema_path: Union[str, Path]) -> List[Constraint]:
    """Load a validation schema from a JSON file.
    
    Args:
        schema_path: Path to the JSON schema file.
        
    Returns:
        A list of Constraint objects.
        
    Raises:
        FileNotFoundError: If the schema file doesn't exist.
        ValueError: If the schema is invalid.
    """
    schema_path = Path(schema_path)
    
    if not schema_path.exists():
        raise FileNotFoundError(f"Schema file not found: {schema_path}")
    
    with open(schema_path, "r") as f:
        schema_data = json.load(f)
    
    return _parse_schema(schema_data)


def _parse_schema(schema_data: Dict) -> List[Constraint]:
    """Parse schema data into Constraint objects.
    
    Args:
        schema_data: Dictionary containing schema definition.
        
    Returns:
        A list of Constraint objects.
        
    Raises:
        ValueError: If the schema is invalid.
    """
    if "constraints" not in schema_data:
        raise ValueError("Schema must contain a 'constraints' key")
    
    constraints = []
    
    for constraint_def in schema_data["constraints"]:
        constraint = _create_constraint(constraint_def)
        constraints.append(constraint)
    
    return constraints


def _create_constraint(constraint_def: Dict) -> Constraint:
    """Create a Constraint object from a definition dictionary.
    
    Args:
        constraint_def: Dictionary defining a single constraint.
        
    Returns:
        A Constraint object.
        
    Raises:
        ValueError: If the constraint definition is invalid.
    """
    if "type" not in constraint_def:
        raise ValueError("Constraint definition must contain a 'type' key")
    
    if "column" not in constraint_def:
        raise ValueError("Constraint definition must contain a 'column' key")
    
    constraint_type = constraint_def["type"]
    column = constraint_def["column"]
    
    if constraint_type == "nullability":
        max_null_ratio = constraint_def.get("max_null_ratio")
        max_null_count = constraint_def.get("max_null_count")
        return NullabilityConstraint(
            column=column,
            max_null_ratio=max_null_ratio,
            max_null_count=max_null_count,
        )
    
    elif constraint_type == "maximum_value":
        if "max_value" not in constraint_def:
            raise ValueError("maximum_value constraint requires 'max_value' key")
        return MaximumValueConstraint(
            column=column,
            max_value=constraint_def["max_value"],
        )
    
    elif constraint_type == "minimum_value":
        if "min_value" not in constraint_def:
            raise ValueError("minimum_value constraint requires 'min_value' key")
        return MinimumValueConstraint(
            column=column,
            min_value=constraint_def["min_value"],
        )
    
    elif constraint_type == "median":
        lower_bound = constraint_def.get("lower_bound")
        upper_bound = constraint_def.get("upper_bound")
        return MedianConstraint(
            column=column,
            lower_bound=lower_bound,
            upper_bound=upper_bound,
        )
    
    elif constraint_type == "mean":
        lower_bound = constraint_def.get("lower_bound")
        upper_bound = constraint_def.get("upper_bound")
        return MeanConstraint(
            column=column,
            lower_bound=lower_bound,
            upper_bound=upper_bound,
        )
    
    elif constraint_type == "percentile":
        if "percentile" not in constraint_def:
            raise ValueError("percentile constraint requires 'percentile' key")
        percentile = constraint_def["percentile"]
        lower_bound = constraint_def.get("lower_bound")
        upper_bound = constraint_def.get("upper_bound")
        return PercentileConstraint(
            column=column,
            percentile=percentile,
            lower_bound=lower_bound,
            upper_bound=upper_bound,
        )
    
    else:
        raise ValueError(f"Unknown constraint type: {constraint_type}")
