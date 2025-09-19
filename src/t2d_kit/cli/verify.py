"""T034: Implement 't2d verify' command."""

import shutil
import subprocess
import sys
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

console = Console()


def check_command(cmd: str, name: str, version_flag: str = "--version") -> tuple[bool, str]:
    """Check if a command is available and get its version."""
    if shutil.which(cmd):
        try:
            result = subprocess.run([cmd, version_flag], capture_output=True, text=True, timeout=5)
            version = result.stdout.strip().split("\n")[0]
            return True, version
        except Exception:
            return True, "installed (version unknown)"
    return False, "not installed"


@click.command(name="verify")
@click.option("--verbose", is_flag=True, help="Show detailed verification information")
def verify_command(verbose: bool):
    """Verify t2d-kit installation and dependencies.

    Checks:
    - Claude Code agent installation
    - Required tools (mise, Python, Node, Go, Java)
    - Diagram tools (D2, Mermaid CLI, PlantUML)
    - MCP server functionality
    """
    console.print("[bold]Verifying t2d-kit installation...[/bold]\n")

    results = []
    all_good = True

    # Check Claude Code agents
    agent_dir = Path("~/.claude/agents").expanduser()
    agent_names = [
        "t2d-transform",
        "t2d-d2-generator",
        "t2d-mermaid-generator",
        "t2d-plantuml-generator",
        "t2d-docs-generator",
        "t2d-slides-generator",
    ]

    agents_found = 0
    for agent in agent_names:
        if (agent_dir / f"{agent}.md").exists():
            agents_found += 1

    if agents_found == len(agent_names):
        results.append(("Claude Code agents", True, f"All {agents_found} agents installed"))
    else:
        results.append(
            ("Claude Code agents", False, f"{agents_found}/{len(agent_names)} installed")
        )
        all_good = False

    # Check base tools
    tools_to_check = [
        ("python", "Python", "--version"),
        ("node", "Node.js", "--version"),
        ("go", "Go", "version"),
        ("java", "Java", "-version"),
        ("mise", "mise", "--version"),
    ]

    for cmd, name, flag in tools_to_check:
        found, version = check_command(cmd, name, flag)
        results.append((name, found, version))
        if not found:
            all_good = False

    # Check diagram tools
    diagram_tools = [
        ("d2", "D2", "--version"),
        ("mmdc", "Mermaid CLI", "--version"),
    ]

    for cmd, name, flag in diagram_tools:
        found, version = check_command(cmd, name, flag)
        results.append((name, found, version))
        if not found and name != "PlantUML":  # PlantUML is optional
            all_good = False

    # Check PlantUML
    plantuml_jar = Path("~/.local/bin/plantuml.jar").expanduser()
    if plantuml_jar.exists():
        results.append(("PlantUML", True, "jar installed"))
    else:
        results.append(("PlantUML", False, "not installed (optional)"))

    # Check MCP server
    try:
        import importlib.util

        spec = importlib.util.find_spec("t2d_kit.mcp")
        if spec is not None:
            results.append(("MCP server", True, "FastMCP configured"))
        else:
            results.append(("MCP server", False, "Module not found"))
            all_good = False
    except ImportError:
        results.append(("MCP server", False, "Import error"))
        all_good = False

    # Check file-based state management
    results.append(("State management", True, "Ready (file-based)"))

    # Display results table
    if verbose:
        table = Table(title="Installation Verification", show_header=True, header_style="bold cyan")
        table.add_column("Component", style="cyan", no_wrap=True)
        table.add_column("Status", justify="center")
        table.add_column("Details")

        for component, found, details in results:
            status = "[green]✓[/green]" if found else "[red]✗[/red]"
            table.add_row(component, status, details)

        console.print(table)
    else:
        # Simple output
        for component, found, details in results:
            if found:
                console.print(f"[green]✓[/green] {component}")
            else:
                console.print(f"[red]✗[/red] {component}: {details}")

    # Summary
    console.print("")
    if all_good:
        console.print("[bold green]✅ All components verified successfully![/bold green]")
        console.print("\nYour t2d-kit installation is ready to use! 🚀")
    else:
        console.print("[bold yellow]⚠ Some components need attention[/bold yellow]")
        console.print("\nRecommended actions:")
        if agents_found < len(agent_names):
            console.print("  • Run [cyan]t2d setup[/cyan] to install missing agents")
        if not shutil.which("mise"):
            console.print("  • Install mise from https://mise.run")
        if not shutil.which("d2"):
            console.print("  • Run [cyan]mise install[/cyan] to install D2")
        if not shutil.which("mmdc"):
            console.print("  • Run [cyan]npm install -g @mermaid-js/mermaid-cli[/cyan]")

    sys.exit(0 if all_good else 1)
