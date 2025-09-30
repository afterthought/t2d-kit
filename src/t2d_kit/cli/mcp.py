"""MCP server management commands for t2d-kit."""

import json
import sys
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

console = Console()


@click.group(name="mcp")
def mcp_command():
    """Manage the T2D Kit MCP server for Claude Code integration."""
    pass


@mcp_command.command()
def start():
    """Start the T2D Kit MCP server.

    This runs the FastMCP server that provides schema and documentation
    resources to Claude Code agents.

    The server runs in stdio mode and communicates via stdin/stdout.
    """
    try:
        from t2d_kit.mcp.server import main

        console.print("[green]Starting T2D Kit MCP server...[/green]")
        main()
    except ImportError as e:
        console.print(f"[red]Error:[/red] FastMCP not installed. Install with: pip install fastmcp")
        console.print(f"[dim]{e}[/dim]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error:[/red] Failed to start MCP server: {e}")
        sys.exit(1)


@mcp_command.command()
@click.option('--format', '-f', type=click.Choice(['json', 'text']), default='text',
              help='Output format: json or text')
def config(format):
    """Generate Claude Code MCP configuration.

    Outputs the configuration needed to add T2D Kit MCP server
    to Claude Code's settings.
    """
    # Get absolute path to current installation
    import t2d_kit
    package_path = Path(t2d_kit.__file__).parent.parent

    config_dict = {
        "mcpServers": {
            "t2d-kit": {
                "type": "stdio",
                "command": sys.executable,  # Use current Python interpreter
                "args": ["-m", "t2d_kit.mcp.server"],
                "description": "T2D Kit schema and documentation resources for Claude Code agents"
            }
        }
    }

    if format == 'json':
        print(json.dumps(config_dict, indent=2))
    else:
        console.print("\n[bold cyan]T2D Kit MCP Configuration[/bold cyan]\n")
        console.print("Add this to your Claude Code configuration:\n")
        console.print(f"[dim]~/.claude.json or .claude/mcp-config.json[/dim]\n")

        console.print(Panel(
            json.dumps(config_dict, indent=2),
            title="Configuration",
            border_style="green"
        ))

        console.print("\n[bold]Quick Setup:[/bold]")
        console.print("1. Copy the configuration above")
        console.print("2. Add it to your Claude Code config file")
        console.print("3. Restart Claude Code")
        console.print("4. Access resources like: [cyan]recipe://schema/user/agent-friendly[/cyan]")
        console.print("\nFor more details, see: [cyan]docs/mcp-setup.md[/cyan]")


@mcp_command.command()
def resources():
    """List all available MCP resources.

    Shows the schema, documentation, and example resources
    provided by the T2D Kit MCP server.
    """
    resources_info = [
        {
            "category": "Schema Resources",
            "items": [
                ("recipe://schema/user", "Raw JSON schema for UserRecipe"),
                ("recipe://schema/processed", "Raw JSON schema for ProcessedRecipe"),
                ("recipe://schema/user/agent-friendly", "Concise UserRecipe schema"),
                ("recipe://schema/processed/agent-friendly", "Concise ProcessedRecipe schema"),
            ]
        },
        {
            "category": "Documentation Resources",
            "items": [
                ("recipe://docs/user-recipe", "Complete UserRecipe documentation"),
                ("recipe://docs/processed-recipe", "Complete ProcessedRecipe documentation"),
                ("recipe://docs/quick-start", "Quick start guide with common patterns"),
            ]
        },
        {
            "category": "Example Resources",
            "items": [
                ("recipe://examples/recipes", "Real-world recipe examples"),
                ("recipe://examples/diagram-types", "Diagram type reference with styling"),
            ]
        }
    ]

    console.print("\n[bold cyan]Available T2D Kit MCP Resources[/bold cyan]\n")

    for category_info in resources_info:
        console.print(f"[bold]{category_info['category']}[/bold]")
        for uri, description in category_info['items']:
            console.print(f"  • [green]{uri}[/green]")
            console.print(f"    [dim]{description}[/dim]")
        console.print()

    console.print("[bold]Usage in Claude Code:[/bold]")
    console.print("  Use ReadMcpResource() to access these resources")
    console.print("  Example: [cyan]ReadMcpResource('recipe://schema/user/agent-friendly')[/cyan]")


@mcp_command.command()
def info():
    """Show MCP server information and status.

    Displays information about the MCP server, including
    version, resources, and setup status.
    """
    try:
        from t2d_kit.mcp.server import mcp
        from t2d_kit._version import __version__

        console.print("\n[bold cyan]T2D Kit MCP Server Information[/bold cyan]\n")
        console.print(f"[bold]Version:[/bold] {__version__}")
        console.print(f"[bold]Server:[/bold] FastMCP")
        console.print(f"[bold]Status:[/bold] [green]✓ Available[/green]")

        console.print("\n[bold]Quick Commands:[/bold]")
        console.print("  [cyan]t2d mcp start[/cyan]      - Start the MCP server")
        console.print("  [cyan]t2d mcp config[/cyan]     - Generate configuration")
        console.print("  [cyan]t2d mcp resources[/cyan]  - List available resources")

        console.print("\n[bold]Setup Steps:[/bold]")
        console.print("  1. Run: [cyan]t2d mcp config[/cyan]")
        console.print("  2. Add configuration to Claude Code settings")
        console.print("  3. Restart Claude Code")
        console.print("  4. Use resources in your agents")

        console.print("\n[bold]Documentation:[/bold]")
        console.print("  • Setup guide: [cyan]docs/mcp-setup.md[/cyan]")
        console.print("  • Quick reference: [cyan]docs/schema-access-quick-reference.md[/cyan]")

    except ImportError:
        console.print("\n[yellow]Warning:[/yellow] FastMCP not installed")
        console.print("Install with: [cyan]pip install fastmcp[/cyan]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[red]Error:[/red] {e}")
        sys.exit(1)


@mcp_command.command()
def test():
    """Test MCP server functionality.

    Verifies that the MCP server can be loaded and is functioning correctly.
    """
    console.print("[cyan]Testing T2D Kit MCP server...[/cyan]\n")

    try:
        from t2d_kit.mcp.server import mcp
        console.print("[green]✓[/green] MCP server module loaded")

        # Test schema generation directly
        from t2d_kit.models.user_recipe import UserRecipe
        from t2d_kit.utils.schema_formatter import format_schema_agent_friendly

        schema = UserRecipe.model_json_schema()
        formatted = format_schema_agent_friendly(schema, "UserRecipe")

        if formatted and "UserRecipe Schema" in formatted:
            console.print("[green]✓[/green] Schema generation working")
        else:
            console.print("[red]✗[/red] Schema generation failed")
            sys.exit(1)

        console.print("[green]✓[/green] All tests passed")
        console.print("\n[bold]Server is ready to use![/bold]")
        console.print("Run [cyan]t2d mcp config[/cyan] to get setup instructions")

    except ImportError as e:
        console.print(f"[red]✗[/red] Import failed: {e}")
        console.print("\nInstall dependencies: [cyan]pip install fastmcp[/cyan]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]✗[/red] Test failed: {e}")
        sys.exit(1)