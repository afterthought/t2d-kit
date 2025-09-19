"""FastMCP server implementation for t2d-kit.

This module provides MCP tools for recipe management and processing.
"""

from pathlib import Path
from typing import Any

import yaml
from fastmcp import FastMCP
from pydantic import ValidationError

from t2d_kit.models import (
    ProcessedRecipe,
    UserRecipe,
)

# T025: Create FastMCP server initialization
mcp = FastMCP("t2d-kit")

# T026: Implement read_user_recipe MCP tool
@mcp.tool()
async def read_user_recipe(file_path: str) -> dict[str, Any]:
    """Read and validate a user recipe YAML file.

    Args:
        file_path: Path to the recipe.yaml file

    Returns:
        Dict containing the validated user recipe data

    Raises:
        FileNotFoundError: If the recipe file doesn't exist
        ValidationError: If the recipe data is invalid
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Recipe file not found: {file_path}")

    with open(path) as f:
        recipe_data = yaml.safe_load(f)

    # Validate using Pydantic model
    try:
        recipe = UserRecipe(**recipe_data)
        return recipe.model_dump()
    except ValidationError as e:
        return {
            "error": "Recipe validation failed",
            "details": e.errors()
        }

# T027: Implement write_processed_recipe MCP tool
@mcp.tool()
async def write_processed_recipe(
    file_path: str,
    processed_data: dict[str, Any]
) -> dict[str, Any]:
    """Write a processed recipe to a YAML file.

    Args:
        file_path: Path where recipe.t2d.yaml will be written
        processed_data: The processed recipe data to write

    Returns:
        Dict with success status and file path

    Raises:
        ValidationError: If the processed data is invalid
    """
    # Validate the processed data
    try:
        recipe = ProcessedRecipe(**processed_data)
    except ValidationError as e:
        return {
            "error": "Processed recipe validation failed",
            "details": e.errors()
        }

    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    # Write as YAML
    with open(path, 'w') as f:
        yaml.safe_dump(
            recipe.model_dump(exclude_none=True),
            f,
            default_flow_style=False,
            sort_keys=False,
            width=120
        )

    return {
        "success": True,
        "file_path": str(path.absolute()),
        "message": f"Processed recipe written to {path}"
    }

# T028: Implement read_processed_recipe MCP tool
@mcp.tool()
async def read_processed_recipe(file_path: str) -> dict[str, Any]:
    """Read a processed recipe from a YAML file.

    Args:
        file_path: Path to the recipe.t2d.yaml file

    Returns:
        Dict containing the processed recipe data

    Raises:
        FileNotFoundError: If the recipe file doesn't exist
        ValidationError: If the recipe data is invalid
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Processed recipe not found: {file_path}")

    with open(path) as f:
        recipe_data = yaml.safe_load(f)

    try:
        recipe = ProcessedRecipe(**recipe_data)
        return recipe.model_dump()
    except ValidationError as e:
        return {
            "error": "Processed recipe validation failed",
            "details": e.errors()
        }

# T029: Implement validate_recipe MCP tool
@mcp.tool()
async def validate_recipe(
    recipe_data: dict[str, Any],
    recipe_type: str = "user"
) -> dict[str, Any]:
    """Validate a recipe without reading/writing files.

    Args:
        recipe_data: The recipe data to validate
        recipe_type: Either "user" or "processed"

    Returns:
        Dict with validation status and any errors
    """
    try:
        if recipe_type == "user":
            recipe = UserRecipe(**recipe_data)
            return {
                "valid": True,
                "type": "user",
                "message": "User recipe is valid"
            }
        elif recipe_type == "processed":
            recipe = ProcessedRecipe(**recipe_data)
            return {
                "valid": True,
                "type": "processed",
                "message": "Processed recipe is valid"
            }
        else:
            return {
                "valid": False,
                "error": f"Unknown recipe type: {recipe_type}"
            }
    except ValidationError as e:
        return {
            "valid": False,
            "type": recipe_type,
            "errors": e.errors()
        }

# T046: Implement recipe file watching
@mcp.tool()
async def watch_recipe_changes(directory: str = ".") -> dict[str, Any]:
    """Watch for changes to recipe files in a directory.

    Args:
        directory: Directory to watch for recipe files

    Returns:
        Dict with list of recipe files found
    """
    import time
    from pathlib import Path

    watch_dir = Path(directory)
    recipe_files = []

    # Find all recipe files
    for pattern in ["recipe.yaml", "recipe.yml", "recipe.t2d.yaml", "recipe.t2d.yml"]:
        recipe_files.extend(watch_dir.glob(f"**/{pattern}"))

    # Get modification times
    file_info = []
    for file in recipe_files:
        stat = file.stat()
        file_info.append({
            "path": str(file.relative_to(watch_dir)),
            "modified": time.ctime(stat.st_mtime),
            "size": stat.st_size
        })

    return {
        "directory": str(watch_dir.absolute()),
        "recipe_count": len(recipe_files),
        "recipes": file_info
    }

@mcp.resource("recipe://example/simple")
async def example_recipe() -> str:
    """Provide an example user recipe."""
    example = {
        "recipe": {
            "name": "Example System",
            "prd": {
                "content": "A simple system with users and orders..."
            },
            "instructions": {
                "diagrams": [
                    {
                        "type": "architecture",
                        "description": "System architecture overview"
                    }
                ],
                "documentation": {
                    "style": "technical",
                    "audience": "developers"
                }
            }
        }
    }
    return yaml.safe_dump(example, default_flow_style=False)

def serve():
    """Serve the MCP server."""
    # T044: Connect MCP server to Claude Desktop config detection
    import sys
    from pathlib import Path

    # Check for Claude Desktop config
    claude_config_paths = [
        Path.home() / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json",
        Path.home() / ".config" / "Claude" / "claude_desktop_config.json",
        Path.home() / "AppData" / "Roaming" / "Claude" / "claude_desktop_config.json",
    ]

    config_found = any(p.exists() for p in claude_config_paths)

    if config_found and sys.stdout.isatty():
        # Running in terminal but Claude Desktop config exists
        print("Claude Desktop configuration detected.", file=sys.stderr)
        print("To use with Claude Desktop, add to your config:", file=sys.stderr)
        print('  "t2d-kit": {', file=sys.stderr)
        print('    "command": "t2d",', file=sys.stderr)
        print('    "args": ["mcp", "."]', file=sys.stderr)
        print('  }', file=sys.stderr)

    mcp.run()
