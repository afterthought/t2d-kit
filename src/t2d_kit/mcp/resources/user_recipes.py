"""MCP resource for user recipe discovery and reading."""

import os
from datetime import datetime
from pathlib import Path
from typing import Optional

import yaml
from fastmcp import FastMCP

from t2d_kit.models.mcp_resources import RecipeDetailResource, RecipeListResource, RecipeSummary

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

    # Register a handler for the base URI pattern
    @server.resource("user-recipes://")
    async def list_user_recipes() -> dict:
        """Get list of all user recipes.

        Returns a list of recipe summaries with metadata about each recipe file.
        """
        recipes = []

        # Ensure directory exists
        if recipe_dir.exists() and recipe_dir.is_dir():
            # Find all YAML files (excluding .t2d.yaml files)
            for recipe_file in recipe_dir.glob("*.yaml"):
                if not recipe_file.name.endswith(".t2d.yaml"):
                    try:
                        summary = get_recipe_metadata(recipe_file)
                        recipes.append(summary)
                    except Exception:
                        # Skip files that can't be read
                        pass

        # Sort by name
        recipes.sort(key=lambda r: r.name)

        resource = RecipeListResource(
            recipes=recipes,
            total_count=len(recipes),
            directory=str(recipe_dir.absolute())
        )

        return {
            "uri": "user-recipes://",
            "name": "User Recipe List",
            "description": f"List of {len(recipes)} user recipe(s) in {recipe_dir}",
            "mimeType": "application/json",
            "content": resource.model_dump()
        }

    # Register individual resources for each existing recipe
    if recipe_dir.exists() and recipe_dir.is_dir():
        for recipe_file in recipe_dir.glob("*.yaml"):
            if not recipe_file.name.endswith(".t2d.yaml"):
                recipe_name = recipe_file.stem

                # Create a closure to capture the recipe_name
                def create_recipe_handler(name: str, path: Path):
                    @server.resource(f"user-recipes://{name}")
                    async def get_specific_recipe() -> dict:
                        """Get a specific user recipe by name.

                        Returns:
                            Full recipe content and metadata
                        """
                        if not path.exists():
                            raise FileNotFoundError(f"Recipe not found: {name}")

                        # Read content
                        with open(path) as f:
                            raw_yaml = f.read()
                            content = yaml.safe_load(raw_yaml)

                        # Get metadata
                        metadata = get_recipe_metadata(path)

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
                            file_path=str(path.absolute()),
                            metadata=metadata
                        )

                        return {
                            "uri": f"user-recipes://{name}",
                            "name": f"User Recipe: {name}",
                            "description": f"User recipe with {metadata.diagram_count} diagram(s)",
                            "mimeType": "application/x-yaml",
                            "content": resource.model_dump()
                        }

                    return get_specific_recipe

                # Register the handler for this specific recipe
                create_recipe_handler(recipe_name, recipe_file)
