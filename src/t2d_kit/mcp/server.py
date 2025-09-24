"""Main MCP server for t2d-kit."""

import asyncio
import os
import sys
from pathlib import Path
from typing import Optional

from fastmcp import FastMCP

from .resources import register_resources
from .tools import register_tools


async def create_server_async(
    recipe_dir: Path | None = None,
    processed_dir: Path | None = None
) -> FastMCP:
    """Create and configure the MCP server asynchronously.

    Args:
        recipe_dir: Directory for user recipes (defaults to ./recipes)
        processed_dir: Directory for processed recipes (defaults to ./.t2d-state/processed)

    Returns:
        Configured FastMCP server instance
    """
    # Create server with descriptive metadata and instructions
    instructions = """t2d-kit MCP Server - Multi-Framework Diagram Pipeline

This server helps you create and manage recipes for generating diagrams and documentation from Product Requirements Documents (PRDs).

## Quick Start:
1. Create a user recipe with `create_user_recipe` tool
2. The recipe needs: a name, PRD content, and diagram specifications
3. The t2d-transform agent will process your recipe automatically

## Recipe Structure:
User recipes require:
- name: Alphanumeric with hyphens/underscores (e.g., "my-system")
- prd_content OR prd_file_path: Your PRD text or file location
- diagrams: List of diagram requests, each with:
  - type: The diagram type (e.g., "flowchart", "architecture", "sequence", "erd")
  - description: Optional description of what to show
  - framework_preference: Optional ("d2", "mermaid", "plantuml")

## Example Recipe Creation:
```json
{
  "name": "ecommerce-platform",
  "prd_content": "# E-commerce Platform\n\nA system for online shopping with cart, checkout, and inventory management.",
  "diagrams": [
    {"type": "architecture", "description": "System components"},
    {"type": "sequence", "description": "Order flow"}
  ]
}
```

## Available Resources:
- diagram-types://: List all supported diagram types
- user-recipes://: Browse existing user recipes
- user-recipe-schema://: View complete schema for user recipes

## Common Diagram Types:
- architecture: System architecture overview
- flowchart: Process or workflow diagrams
- sequence: Interaction sequences
- erd: Entity relationship diagrams
- component: Component relationships
- deployment: Infrastructure layout
- state: State machine diagrams
- class: Class structure diagrams

For more details, explore the resources or check the schema documentation.
"""

    server = FastMCP("t2d-kit", instructions=instructions)

    # Set default directories
    if recipe_dir is None:
        recipe_dir = Path("./recipes")
    if processed_dir is None:
        processed_dir = Path("./.t2d-state/processed")

    # Register components
    await register_resources(server, recipe_dir, processed_dir)
    await register_tools(server, recipe_dir, processed_dir)

    return server


def create_server(
    recipe_dir: Path | None = None,
    processed_dir: Path | None = None
) -> FastMCP:
    """Create and configure the MCP server (synchronous wrapper).

    Args:
        recipe_dir: Directory for user recipes (defaults to ./recipes)
        processed_dir: Directory for processed recipes (defaults to ./.t2d-state/processed)

    Returns:
        Configured FastMCP server instance
    """
    return asyncio.run(create_server_async(recipe_dir, processed_dir))


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
