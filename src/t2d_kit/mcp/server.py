"""Main MCP server for t2d-kit."""

import asyncio
import os
import sys
from pathlib import Path
from typing import Optional

from fastmcp import FastMCP

from .resources import register_resources
from .tools import register_tools


def create_server(
    recipe_dir: Path | None = None,
    processed_dir: Path | None = None
) -> FastMCP:
    """Create and configure the MCP server.

    Args:
        recipe_dir: Directory for user recipes (defaults to ./recipes)
        processed_dir: Directory for processed recipes (defaults to ./.t2d-state/processed)

    Returns:
        Configured FastMCP server instance
    """
    # Create server with descriptive metadata
    server = FastMCP("t2d-kit")

    # Set default directories
    if recipe_dir is None:
        recipe_dir = Path("./recipes")
    if processed_dir is None:
        processed_dir = Path("./.t2d-state/processed")

    # Register components asynchronously
    async def setup():
        await register_resources(server, recipe_dir, processed_dir)
        await register_tools(server, recipe_dir, processed_dir)

    # Run setup
    asyncio.run(setup())

    return server


def main():
    """Main entry point for the MCP server.

    This function is called when the server is run in stdio mode
    by Claude Desktop or other MCP clients.
    """
    # Get configuration from environment variables
    recipe_dir = os.environ.get("T2D_RECIPE_DIR")
    processed_dir = os.environ.get("T2D_PROCESSED_DIR")

    # Convert to Path objects if provided
    if recipe_dir:
        recipe_dir = Path(recipe_dir)
    if processed_dir:
        processed_dir = Path(processed_dir)

    # Create and run server
    server = create_server(recipe_dir, processed_dir)

    # Run in stdio mode for Claude Desktop
    server.run()


if __name__ == "__main__":
    main()
