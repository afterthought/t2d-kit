"""MCP resources for t2d-kit."""

from pathlib import Path
from typing import Optional

from fastmcp import FastMCP

from .diagram_types import register_diagram_types_resource
from .processed_recipes import register_processed_recipe_resources
from .schemas import register_schema_resources
from .user_recipes import register_user_recipe_resources


async def register_resources(
    server: FastMCP,
    recipe_dir: Path | None = None,
    processed_dir: Path | None = None
) -> None:
    """Register all MCP resources with the server.

    Args:
        server: FastMCP server instance
        recipe_dir: Directory for user recipes
        processed_dir: Directory for processed recipes
    """
    # Register all resources
    await register_diagram_types_resource(server)
    await register_user_recipe_resources(server, recipe_dir)
    await register_processed_recipe_resources(server, processed_dir)
    await register_schema_resources(server)


__all__ = [
    "register_resources",
    "register_diagram_types_resource",
    "register_user_recipe_resources",
    "register_processed_recipe_resources",
    "register_schema_resources",
]
