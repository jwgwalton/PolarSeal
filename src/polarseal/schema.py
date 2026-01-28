"""Schema loading from JSON files."""

import json
from pathlib import Path
from typing import Dict, List, Tuple, Union

from .constraints import (
    Constraint,
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
from .validator import SchemaValidator


def load_schema(schema_path: Union[str, Path]) -> SchemaValidator:
    """Load a validation schema from a JSON file.
    
    Args:
        schema_path: Path to the JSON schema file.
        
    Returns:
        A SchemaValidator object configured with the schema.
        
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


def _parse_schema(schema_data: Dict) -> SchemaValidator:
    """Parse schema data into a SchemaValidator object.
    
    Args:
        schema_data: Dictionary containing schema definition.
        
    Returns:
        A SchemaValidator object.
        
    Raises:
        ValueError: If the schema is invalid.
    """
    if "fields" not in schema_data:
        raise ValueError("Schema must contain a 'fields' key")
    
    return _parse_field_based_schema(schema_data)


def _parse_field_based_schema(schema_data: Dict) -> SchemaValidator:
    """Parse field-based schema format.
    
    Args:
        schema_data: Dictionary containing field-based schema definition.
        
    Returns:
        A SchemaValidator object.
        
    Raises:
        ValueError: If the schema is invalid.
    """
    if "fields" not in schema_data:
        raise ValueError("Schema must contain a 'fields' key")
    
    fields = schema_data["fields"]
    if not isinstance(fields, dict):
        raise ValueError("'fields' must be a dictionary")
    
    field_definitions = {}
    constraints = []
    
    for field_name, field_spec in fields.items():
        if not isinstance(field_spec, dict):
            raise ValueError(f"Field '{field_name}' specification must be a dictionary")
        
        if "type" not in field_spec:
            raise ValueError(f"Field '{field_name}' must specify a 'type'")
        
        # Store field type
        field_definitions[field_name] = field_spec["type"]
        
        # Parse constraints for this field (can be empty)
        field_constraints = field_spec.get("constraints", [])
        if not isinstance(field_constraints, list):
            raise ValueError(f"Field '{field_name}' constraints must be a list")
        
        for constraint_def in field_constraints:
            # Add column name to constraint definition
            constraint_def_with_column = dict(constraint_def)
            constraint_def_with_column["column"] = field_name
            constraint = _create_constraint(constraint_def_with_column)
            constraints.append(constraint)
    
    return SchemaValidator(constraints, field_definitions)


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
    
    elif constraint_type == "uniqueness":
        min_unique_ratio = constraint_def.get("min_unique_ratio")
        min_unique_count = constraint_def.get("min_unique_count")
        return UniquenessConstraint(
            column=column,
            min_unique_ratio=min_unique_ratio,
            min_unique_count=min_unique_count,
        )
    
    elif constraint_type == "standard_deviation":
        lower_bound = constraint_def.get("lower_bound")
        upper_bound = constraint_def.get("upper_bound")
        return StandardDeviationConstraint(
            column=column,
            lower_bound=lower_bound,
            upper_bound=upper_bound,
        )
    
    elif constraint_type == "string_length":
        min_length = constraint_def.get("min_length")
        max_length = constraint_def.get("max_length")
        return StringLengthConstraint(
            column=column,
            min_length=min_length,
            max_length=max_length,
        )
    
    elif constraint_type == "regex_pattern":
        if "pattern" not in constraint_def:
            raise ValueError("regex_pattern constraint requires 'pattern' key")
        return RegexPatternConstraint(
            column=column,
            pattern=constraint_def["pattern"],
        )
    
    elif constraint_type == "value_set":
        if "allowed_values" not in constraint_def:
            raise ValueError("value_set constraint requires 'allowed_values' key")
        return ValueSetConstraint(
            column=column,
            allowed_values=constraint_def["allowed_values"],
        )
    
    elif constraint_type == "row_count":
        min_rows = constraint_def.get("min_rows")
        max_rows = constraint_def.get("max_rows")
        return RowCountConstraint(
            column=column,
            min_rows=min_rows,
            max_rows=max_rows,
        )
    
    else:
        raise ValueError(f"Unknown constraint type: {constraint_type}")
