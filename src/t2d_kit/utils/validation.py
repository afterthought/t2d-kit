"""Validation utilities for recipes."""

import time
from pathlib import Path
from typing import Any, Dict, List, Tuple

import yaml

from t2d_kit.models.processed_recipe import ProcessedRecipe
from t2d_kit.models.user_recipe import UserRecipe


def validate_user_recipe_file(recipe_path: Path) -> tuple[bool, list[str], list[str]]:
    """Validate a user recipe file.

    Args:
        recipe_path: Path to recipe file

    Returns:
        Tuple of (is_valid, errors, warnings)
    """
    errors = []
    warnings = []

    if not recipe_path.exists():
        errors.append(f"File not found: {recipe_path}")
        return False, errors, warnings

    if recipe_path.suffix != ".yaml":
        errors.append("Recipe file must have .yaml extension")
        return False, errors, warnings

    # Check file size
    size_bytes = recipe_path.stat().st_size
    if size_bytes > 1048576:  # 1MB
        errors.append(f"Recipe file too large: {size_bytes} bytes (max 1MB)")
        return False, errors, warnings
    elif size_bytes > 524288:  # 512KB
        warnings.append(f"Recipe file is large: {size_bytes} bytes")

    # Try to parse YAML
    try:
        with open(recipe_path) as f:
            content = yaml.safe_load(f)
    except yaml.YAMLError as e:
        errors.append(f"Invalid YAML: {str(e)}")
        return False, errors, warnings
    except Exception as e:
        errors.append(f"Failed to read file: {str(e)}")
        return False, errors, warnings

    # Validate with Pydantic
    try:
        recipe = UserRecipe.model_validate(content)

        # Additional checks
        if len(recipe.instructions.diagrams) > 20:
            warnings.append(f"Recipe has {len(recipe.instructions.diagrams)} diagrams (recommended max: 20)")

        if recipe.prd.file_path:
            prd_path = Path(recipe.prd.file_path)
            if not prd_path.is_absolute():
                prd_path = recipe_path.parent / prd_path
            if not prd_path.exists():
                warnings.append(f"PRD file not found: {recipe.prd.file_path}")

        return True, errors, warnings

    except Exception as e:
        errors.append(f"Validation error: {str(e)}")
        return False, errors, warnings


def validate_processed_recipe_file(recipe_path: Path) -> tuple[bool, list[str], list[str]]:
    """Validate a processed recipe file.

    Args:
        recipe_path: Path to processed recipe file

    Returns:
        Tuple of (is_valid, errors, warnings)
    """
    errors = []
    warnings = []

    if not recipe_path.exists():
        errors.append(f"File not found: {recipe_path}")
        return False, errors, warnings

    if not recipe_path.name.endswith(".t2d.yaml"):
        warnings.append("Processed recipe should have .t2d.yaml extension")

    # Try to parse YAML
    try:
        with open(recipe_path) as f:
            content = yaml.safe_load(f)
    except yaml.YAMLError as e:
        errors.append(f"Invalid YAML: {str(e)}")
        return False, errors, warnings
    except Exception as e:
        errors.append(f"Failed to read file: {str(e)}")
        return False, errors, warnings

    # Validate with Pydantic
    try:
        recipe = ProcessedRecipe.model_validate(content)

        # Check for consistency
        spec_ids = {spec.id for spec in recipe.diagram_specs}
        ref_ids = {ref.id for ref in recipe.diagram_refs}

        missing_refs = spec_ids - ref_ids
        if missing_refs:
            errors.append(f"Missing diagram references: {missing_refs}")

        extra_refs = ref_ids - spec_ids
        if extra_refs:
            errors.append(f"Extra diagram references: {extra_refs}")

        # Check content file references
        for content_file in recipe.content_files:
            invalid_refs = set(content_file.diagram_refs or []) - spec_ids
            if invalid_refs:
                warnings.append(f"Content file '{content_file.path}' references invalid diagrams: {invalid_refs}")

        # Check for orphaned diagrams
        referenced = set()
        for content_file in recipe.content_files:
            referenced.update(content_file.diagram_refs or [])

        orphaned = spec_ids - referenced
        if orphaned:
            warnings.append(f"Diagrams not referenced by any content: {orphaned}")

        return len(errors) == 0, errors, warnings

    except Exception as e:
        errors.append(f"Validation error: {str(e)}")
        return False, errors, warnings


def validate_diagram_type(diagram_type: str) -> bool:
    """Check if a diagram type is valid.

    Args:
        diagram_type: Diagram type identifier

    Returns:
        True if valid, False otherwise
    """
    from t2d_kit.mcp.resources.diagram_types import DIAGRAM_TYPES

    valid_types = {dt.type_id for dt in DIAGRAM_TYPES}
    return diagram_type in valid_types


def validate_framework(framework: str) -> bool:
    """Check if a framework is valid.

    Args:
        framework: Framework name

    Returns:
        True if valid, False otherwise
    """
    valid_frameworks = {"mermaid", "d2", "plantuml", "auto"}
    return framework.lower() in valid_frameworks
