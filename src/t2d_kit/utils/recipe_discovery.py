"""Utility functions for recipe discovery and management."""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


def discover_user_recipes(recipe_dir: Path = Path("./recipes")) -> list[dict[str, Any]]:
    """Discover all user recipes in a directory.

    Args:
        recipe_dir: Directory to search for recipes

    Returns:
        List of recipe metadata dictionaries
    """
    recipes = []

    if not recipe_dir.exists():
        return recipes

    for recipe_file in recipe_dir.glob("*.yaml"):
        # Skip processed recipes
        if recipe_file.name.endswith(".t2d.yaml"):
            continue

        try:
            with open(recipe_file) as f:
                content = yaml.safe_load(f)

            stat = recipe_file.stat()
            recipes.append({
                "name": recipe_file.stem,
                "path": str(recipe_file),
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "size_bytes": stat.st_size,
                "valid": bool(content and content.get("name") and content.get("instructions"))
            })
        except Exception:
            # Skip invalid files
            pass

    return sorted(recipes, key=lambda r: r["name"])


def discover_processed_recipes(
    processed_dir: Path = Path("./.t2d-state/processed")
) -> list[dict[str, Any]]:
    """Discover all processed recipes in a directory.

    Args:
        processed_dir: Directory to search for processed recipes

    Returns:
        List of processed recipe metadata dictionaries
    """
    recipes = []

    if not processed_dir.exists():
        return recipes

    for recipe_file in processed_dir.glob("*.t2d.yaml"):
        try:
            with open(recipe_file) as f:
                content = yaml.safe_load(f)

            stat = recipe_file.stat()
            recipes.append({
                "name": recipe_file.stem.replace(".t2d", ""),
                "path": str(recipe_file),
                "generated_at": content.get("generated_at", "unknown"),
                "source_recipe": content.get("source_recipe", "unknown"),
                "diagram_count": len(content.get("diagram_specs", [])),
                "content_count": len(content.get("content_files", [])),
                "size_bytes": stat.st_size
            })
        except Exception:
            # Skip invalid files
            pass

    return sorted(recipes, key=lambda r: r.get("generated_at", ""), reverse=True)


def find_recipe_by_name(name: str, recipe_dir: Path = Path("./recipes")) -> Path | None:
    """Find a recipe file by name.

    Args:
        name: Recipe name (without extension)
        recipe_dir: Directory to search

    Returns:
        Path to recipe file if found, None otherwise
    """
    # Try exact match
    recipe_path = recipe_dir / f"{name}.yaml"
    if recipe_path.exists():
        return recipe_path

    # Try case-insensitive match
    for recipe_file in recipe_dir.glob("*.yaml"):
        if recipe_file.stem.lower() == name.lower():
            return recipe_file

    return None


def get_recipe_summary(recipe_path: Path) -> dict[str, Any]:
    """Get a summary of a recipe file.

    Args:
        recipe_path: Path to recipe file

    Returns:
        Dictionary with recipe summary information
    """
    if not recipe_path.exists():
        return {"error": "File not found"}

    try:
        with open(recipe_path) as f:
            content = yaml.safe_load(f)

        stat = recipe_path.stat()

        # Determine if user or processed recipe
        is_processed = recipe_path.name.endswith(".t2d.yaml")

        if is_processed:
            return {
                "type": "processed",
                "name": content.get("name", "unknown"),
                "version": content.get("version", "unknown"),
                "source_recipe": content.get("source_recipe", "unknown"),
                "generated_at": content.get("generated_at", "unknown"),
                "diagrams": len(content.get("diagram_specs", [])),
                "content_files": len(content.get("content_files", [])),
                "size_bytes": stat.st_size,
                "path": str(recipe_path)
            }
        else:
            return {
                "type": "user",
                "name": content.get("name", "unknown"),
                "version": content.get("version", "1.0.0"),
                "has_prd": bool(content.get("prd")),
                "diagrams": len(content.get("instructions", {}).get("diagrams", [])),
                "has_documentation": bool(content.get("instructions", {}).get("documentation")),
                "has_presentation": bool(content.get("instructions", {}).get("presentation")),
                "size_bytes": stat.st_size,
                "path": str(recipe_path)
            }
    except Exception as e:
        return {"error": str(e), "path": str(recipe_path)}
