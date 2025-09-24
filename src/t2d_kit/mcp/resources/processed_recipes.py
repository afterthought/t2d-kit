"""MCP resource for processed recipe discovery and reading."""

import os
from datetime import datetime
from pathlib import Path
from typing import Optional

import yaml
from fastmcp import FastMCP

from t2d_kit.models.mcp_resources import (
    ProcessedRecipeDetailResource,
    ProcessedRecipeListResource,
    ProcessedRecipeSummary,
)

DEFAULT_PROCESSED_DIR = Path("./.t2d-state/processed")


def get_processed_metadata(recipe_path: Path) -> ProcessedRecipeSummary:
    """Extract metadata from a processed recipe file.

    Args:
        recipe_path: Path to processed recipe YAML file

    Returns:
        ProcessedRecipeSummary with file metadata
    """
    stat = recipe_path.stat()

    # Try to read and validate the recipe
    validation_status = "unknown"
    diagram_count = 0
    content_file_count = 0
    source_recipe = ""
    generated_at = datetime.fromtimestamp(stat.st_ctime).isoformat() + "Z"

    try:
        with open(recipe_path) as f:
            content = yaml.safe_load(f)

        # Check for required fields
        if content and isinstance(content, dict):
            if "diagram_specs" in content:
                diagram_count = len(content["diagram_specs"])

            if "content_files" in content:
                content_file_count = len(content["content_files"])

            if "source_recipe" in content:
                source_recipe = content["source_recipe"]

            if "generated_at" in content:
                generated_at = content["generated_at"]

            # Basic validation
            if (content.get("name") and
                content.get("diagram_specs") and
                content.get("content_files")):
                validation_status = "valid"
            else:
                validation_status = "invalid"

    except Exception:
        validation_status = "invalid"

    return ProcessedRecipeSummary(
        name=recipe_path.stem.replace(".t2d", ""),
        file_path=str(recipe_path.absolute()),
        source_recipe=source_recipe,
        generated_at=generated_at,
        modified_at=datetime.fromtimestamp(stat.st_mtime).isoformat() + "Z",
        size_bytes=stat.st_size,
        diagram_count=diagram_count,
        content_file_count=content_file_count,
        validation_status=validation_status
    )


async def register_processed_recipe_resources(
    server: FastMCP,
    processed_dir: Path | None = None
) -> None:
    """Register processed recipe resources with the MCP server.

    Args:
        server: FastMCP server instance
        processed_dir: Directory containing processed recipe files
    """
    if processed_dir is None:
        processed_dir = DEFAULT_PROCESSED_DIR

    @server.resource("processed-recipes://")
    async def list_processed_recipes() -> dict:
        """Get list of all processed recipes.

        Returns a list of processed recipe summaries with metadata.
        """
        recipes = []

        # Ensure directory exists
        if processed_dir.exists() and processed_dir.is_dir():
            # Find all .t2d.yaml files
            for recipe_file in processed_dir.glob("*.t2d.yaml"):
                try:
                    summary = get_processed_metadata(recipe_file)
                    recipes.append(summary)
                except Exception:
                    # Skip files that can't be read
                    pass

        # Sort by generation time (newest first)
        recipes.sort(key=lambda r: r.generated_at, reverse=True)

        resource = ProcessedRecipeListResource(
            recipes=recipes,
            total_count=len(recipes),
            directory=str(processed_dir.absolute())
        )

        return {
            "uri": "processed-recipes://",
            "name": "Processed Recipe List",
            "description": f"List of {len(recipes)} processed recipe(s) in {processed_dir}",
            "mimeType": "application/json",
            "content": resource.model_dump()
        }

    # Register individual resources for each existing processed recipe
    if processed_dir.exists() and processed_dir.is_dir():
        for recipe_file in processed_dir.glob("*.t2d.yaml"):
            recipe_name = recipe_file.stem.replace(".t2d", "")

            # Create a closure to capture the recipe_name
            def create_processed_handler(name: str, path: Path):
                @server.resource(f"processed-recipes://{name}")
                async def get_specific_processed_recipe() -> dict:
                    """Get a specific processed recipe by name.

                    Returns:
                        Full processed recipe content and metadata
                    """
                    if not path.exists():
                        raise FileNotFoundError(f"Processed recipe not found: {name}")

                    # Read content
                    with open(path) as f:
                        raw_yaml = f.read()
                        content = yaml.safe_load(raw_yaml)

                    # Get metadata
                    metadata = get_processed_metadata(path)

                    # Try to validate
                    validation_result = None
                    try:
                        from t2d_kit.models.processed_recipe import ProcessedRecipe
                        ProcessedRecipe.model_validate(content)
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

                    resource = ProcessedRecipeDetailResource(
                        name=name,
                        content=content,
                        raw_yaml=raw_yaml,
                        validation_result=validation_result,
                        file_path=str(path.absolute()),
                        metadata=metadata
                    )

                    return {
                        "uri": f"processed-recipes://{name}",
                        "name": f"Processed Recipe: {name}",
                        "description": f"Processed recipe with {metadata.diagram_count} diagram(s) and {metadata.content_file_count} content file(s)",
                        "mimeType": "application/x-yaml",
                        "content": resource.model_dump()
                    }

                return get_specific_processed_recipe

            # Register the handler for this specific recipe
            create_processed_handler(recipe_name, recipe_file)
