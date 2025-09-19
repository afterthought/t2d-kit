"""MCP tools for t2d-kit."""

from pathlib import Path
from typing import Optional

from fastmcp import FastMCP

from .processed_recipe_tools import register_processed_recipe_tools
from .user_recipe_tools import register_user_recipe_tools


async def register_tools(
    server: FastMCP,
    recipe_dir: Path | None = None,
    processed_dir: Path | None = None
) -> None:
    """Register all MCP tools with the server.

    Args:
        server: FastMCP server instance
        recipe_dir: Directory for user recipes
        processed_dir: Directory for processed recipes
    """
    # Register all tools
    await register_user_recipe_tools(server, recipe_dir)
    await register_processed_recipe_tools(server, processed_dir)


__all__ = [
    "register_tools",
    "register_user_recipe_tools",
    "register_processed_recipe_tools",
]
