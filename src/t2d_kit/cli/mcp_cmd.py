"""T033: Implement 't2d mcp' server command."""

import sys
from pathlib import Path

import click
from rich.console import Console

console = Console()


@click.command(name="mcp")
@click.argument(
    "working_dir",
    default=".",
    type=click.Path(exists=True, file_okay=False, dir_okay=True)
)
@click.option(
    "--port",
    default=0,
    help="Port to run the MCP server on (0 for stdio mode)",
    type=int
)
def mcp_command(working_dir: str, port: int):
    """Start the MCP server for recipe management.

    The MCP server provides tools for:
    - Reading and writing recipe files
    - Validating recipe structure
    - Managing recipe transformations

    By default, runs in stdio mode for Claude Desktop integration.
    """
    work_path = Path(working_dir).resolve()

    if port > 0:
        console.print(f"[bold]Starting MCP server on port {port}...[/bold]")
        console.print(f"Working directory: {work_path}")
        # Network mode would go here if FastMCP supports it
        console.print("[red]Network mode not yet supported by FastMCP[/red]")
        sys.exit(1)
    else:
        # Stdio mode for Claude Desktop
        import os
        os.chdir(work_path)

        # Import and run the server
        from t2d_kit.mcp.server import serve

        # In stdio mode, we don't print to console (would interfere with protocol)
        serve()
