"""MCP resource for user recipe discovery and reading."""

import os
from datetime import datetime
from pathlib import Path
from typing import Optional

import yaml
from fastmcp import FastMCP

from t2d_kit.models.mcp_resources import RecipeDetailResource, RecipeSummary

DEFAULT_RECIPE_DIR = Path("./recipes")


def get_recipe_metadata(recipe_path: Path) -> RecipeSummary:
    """Extract metadata from a recipe file.

    Args:
        recipe_path: Path to recipe YAML file

    Returns:
        RecipeSummary with file metadata
    """
    stat = recipe_path.stat()

    # Try to read and validate the recipe
    validation_status = "unknown"
    diagram_count = 0
    has_prd = False

    try:
        with open(recipe_path) as f:
            content = yaml.safe_load(f)

        # Check for required fields
        if content and isinstance(content, dict):
            if "instructions" in content:
                if "diagrams" in content.get("instructions", {}):
                    diagram_count = len(content["instructions"]["diagrams"])

            if "prd" in content:
                prd = content["prd"]
                has_prd = bool(prd.get("content") or prd.get("file_path"))

            # Basic validation
            if content.get("name") and content.get("instructions"):
                validation_status = "valid"
            else:
                validation_status = "invalid"

    except Exception:
        validation_status = "invalid"

    return RecipeSummary(
        name=recipe_path.stem,
        file_path=str(recipe_path.absolute()),
        created_at=datetime.fromtimestamp(stat.st_ctime).isoformat() + "Z",
        modified_at=datetime.fromtimestamp(stat.st_mtime).isoformat() + "Z",
        size_bytes=stat.st_size,
        diagram_count=diagram_count,
        has_prd=has_prd,
        validation_status=validation_status
    )


async def register_user_recipe_resources(server: FastMCP, recipe_dir: Path | None = None) -> None:
    """Register user recipe resources with the MCP server.

    Args:
        server: FastMCP server instance
        recipe_dir: Directory containing recipe files (defaults to ./recipes)
    """
    if recipe_dir is None:
        recipe_dir = DEFAULT_RECIPE_DIR

    # Register a resource template for user recipes using file:// URI with absolute path
    # The template uses the absolute path to the recipe directory
    base_path = recipe_dir.resolve()

    @server.resource(f"file://{base_path}/{{name}}.yaml", mime_type="application/json")
    async def get_user_recipe(name: str) -> dict:
        """Get a specific user recipe by name.

        Args:
            name: Name of the recipe file (without .yaml extension)

        Returns:
            Full recipe content and metadata
        """
        recipe_path = base_path / f"{name}.yaml"

        if not recipe_path.exists():
            raise FileNotFoundError(f"Recipe not found: {name}")

        # Read content
        with open(recipe_path) as f:
            raw_yaml = f.read()
            content = yaml.safe_load(raw_yaml)

        # Get metadata
        metadata = get_recipe_metadata(recipe_path)

        # Try to validate
        validation_result = None
        try:
            from t2d_kit.models.user_recipe import UserRecipe
            UserRecipe.model_validate(content)
            validation_result = {
                "valid": True,
                "errors": [],
                "warnings": []
            }
        except Exception as e:
            validation_result = {
                "valid": False,
                "errors": [{"message": str(e)}],
                "warnings": []
            }

        resource = RecipeDetailResource(
            name=name,
            content=content,
            raw_yaml=raw_yaml,
            validation_result=validation_result,
            file_path=str(recipe_path.absolute()),
            metadata=metadata
        )

        # Return the data directly - FastMCP will handle wrapping
        return resource.model_dump()
