"""T032: Implement 't2d setup' command."""

import shutil
from importlib import resources
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


@click.command(name="setup")
@click.option(
    "--level",
    type=click.Choice(["project", "user"], case_sensitive=False),
    help="Installation level: 'project' (./.claude/agents) or 'user' (~/.claude/agents)",
)
@click.option(
    "--agent-dir",
    help="Custom directory for agent installation (overrides --level)",
    type=click.Path(),
)
@click.option("--force", is_flag=True, help="Overwrite existing agent files")
def setup_command(level: str, agent_dir: str, force: bool):
    """Setup t2d-kit agents and dependencies.

    This command:
    1. Installs Claude Code agents to chosen location
    2. Verifies mise dependencies
    3. Sets up the environment for diagram generation
    """
    # Determine installation path
    if agent_dir:
        # Custom path takes precedence
        agent_path = Path(agent_dir).expanduser()
        install_type = "custom"
    elif level:
        # Explicit level choice
        if level == "project":
            agent_path = Path("./.claude/agents")
            install_type = "project"
        else:
            agent_path = Path("~/.claude/agents").expanduser()
            install_type = "user"
    else:
        # Interactive prompt if no option provided
        console.print("\n[bold]Choose installation level:[/bold]")
        console.print("1. Project level (./.claude/agents) - agents for this project only")
        console.print("2. User level (~/.claude/agents) - agents available globally")

        choice = click.prompt("\nSelect", type=click.Choice(["1", "2"]), default="1")
        if choice == "1":
            agent_path = Path("./.claude/agents")
            install_type = "project"
        else:
            agent_path = Path("~/.claude/agents").expanduser()
            install_type = "user"

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        # Create agent directory
        task = progress.add_task("Creating agent directory...", total=1)
        agent_path.mkdir(parents=True, exist_ok=True)
        progress.update(task, completed=1)

        # Copy agent files
        task = progress.add_task("Installing Claude Code agents...", total=6)
        agent_names = [
            "t2d-create-recipe",
            "t2d-transform",
            "t2d-d2-generator",
            "t2d-mermaid-generator",
            "t2d-plantuml-generator",
            "t2d-docs-generator",
            "t2d-slides-generator",
        ]

        import t2d_kit.agents

        agent_files = resources.files(t2d_kit.agents)

        for i, agent_name in enumerate(agent_names):
            agent_file = agent_files / f"{agent_name}.md"
            target_path = agent_path / f"{agent_name}.md"

            if target_path.exists() and not force:
                console.print(
                    f"[yellow]⚠[/yellow] {agent_name} already exists (use --force to overwrite)"
                )
            else:
                if agent_file.is_file():
                    with agent_file.open("rb") as src:
                        target_path.write_bytes(src.read())
                    console.print(f"[green]✓[/green] Installed {agent_name}")
                else:
                    console.print(f"[red]✗[/red] Agent file not found: {agent_name}")

            progress.update(task, completed=i + 1)

        progress.update(task, completed=6)

        # Check mise installation
        task = progress.add_task("Checking mise dependencies...", total=1)
        if shutil.which("mise"):
            console.print("[green]✓[/green] mise is installed")
        else:
            console.print("[yellow]⚠[/yellow] mise not found - install from https://mise.run")
        progress.update(task, completed=1)

    # Success message
    console.print("")
    level_msg = {
        "project": "[yellow]Project-level[/yellow] installation",
        "user": "[cyan]User-level[/cyan] installation",
        "custom": "[magenta]Custom[/magenta] installation"
    }[install_type]

    console.print(
        Panel.fit(
            f"[bold green]✅ t2d-kit setup complete![/bold green]\n\n"
            f"   {level_msg}\n"
            f"   Agents installed to: [bold]{agent_path}[/bold]\n\n"
            "🤖 Intelligent agents ready:\n"
            "   - Create Recipe Agent: Helps create new user recipes\n"
            "   - Transform Agent: Converts simple recipes to detailed specs\n"
            "   - Diagram Agents: Generate D2, Mermaid, PlantUML diagrams\n"
            "   - Content Agents: Create documentation and presentations\n"
            "   - All agents self-activate based on 'use proactively' instructions\n\n"
            "📝 Recipe CLI commands:\n"
            "   - t2d recipe list: Show available recipes\n"
            "   - t2d recipe load: Load and display a recipe\n"
            "   - t2d recipe save: Save a new recipe\n"
            "   - t2d recipe validate: Validate recipe structure",
            title="Setup Complete",
            border_style="green",
        )
    )

    # Next steps
    console.print("\n[bold]Next steps:[/bold]")
    console.print("1. Run [cyan]mise install[/cyan] to install diagram tools")
    console.print("2. Test recipe commands: [cyan]t2d recipe list[/cyan]")
    console.print("3. Verify installation: [cyan]t2d verify[/cyan]")
