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
        task = progress.add_task("Installing Claude Code agents...", total=8)
        agent_names = [
            "t2d-create-recipe",
            "t2d-transform",
            "t2d-d2-generator",
            "t2d-mermaid-generator",
            "t2d-plantuml-generator",
            "t2d-mkdocs-generator",
            "t2d-zudoku-generator",
            "t2d-slides-generator",
        ]

        # Try to read from source directory first (development mode)
        # This ensures we always get the latest agent definitions
        import t2d_kit
        package_path = Path(t2d_kit.__file__).parent
        source_agents_dir = package_path / "agents"

        # Fall back to package resources if source directory doesn't exist
        use_source_dir = source_agents_dir.exists()

        if not use_source_dir:
            import t2d_kit.agents
            agent_files = resources.files(t2d_kit.agents)

        for i, agent_name in enumerate(agent_names):
            if use_source_dir:
                agent_file = source_agents_dir / f"{agent_name}.md"
                file_exists = agent_file.exists()
            else:
                agent_file = agent_files / f"{agent_name}.md"
                file_exists = agent_file.is_file()

            target_path = agent_path / f"{agent_name}.md"

            if target_path.exists() and not force:
                console.print(
                    f"[yellow]⚠[/yellow] {agent_name} already exists (use --force to overwrite)"
                )
            else:
                if file_exists:
                    if use_source_dir:
                        # Read directly from source file
                        target_path.write_bytes(agent_file.read_bytes())
                    else:
                        # Read from package resources
                        with agent_file.open("rb") as src:
                            target_path.write_bytes(src.read())
                    console.print(f"[green]✓[/green] Installed {agent_name}")
                else:
                    console.print(f"[red]✗[/red] Agent file not found: {agent_name}")

            progress.update(task, completed=i + 1)

        progress.update(task, completed=8)

        # Check mise installation and configure tools
        task = progress.add_task("Configuring mise tools...", total=1)
        mise_installed = shutil.which("mise")

        if not mise_installed:
            console.print("[red]✗[/red] mise is not installed")
            console.print("[yellow]→[/yellow] Please install mise from https://mise.run")
            console.print("[yellow]→[/yellow] Then run [cyan]t2d setup[/cyan] again")
            progress.update(task, completed=1)
        else:
            console.print("[green]✓[/green] mise is installed")

            import subprocess
            import toml

            # Check if mise.toml exists in current directory
            mise_config_path = Path.cwd() / "mise.toml"

            # Load existing config or create new one
            if mise_config_path.exists():
                console.print("[cyan]→[/cyan] Found existing mise.toml, updating...")
                try:
                    with open(mise_config_path, "r") as f:
                        config = toml.load(f)
                except Exception as e:
                    console.print(f"[yellow]⚠[/yellow] Could not read mise.toml: {e}")
                    config = {}
            else:
                console.print("[cyan]→[/cyan] Creating mise.toml with required tools...")
                config = {}

            # Ensure tools section exists
            if "tools" not in config:
                config["tools"] = {}

            # Check which base languages are already installed
            has_python = shutil.which("python") or shutil.which("python3")
            has_node = shutil.which("node") or shutil.which("npm")
            has_go = shutil.which("go")
            has_java = shutil.which("java")

            # Define required tools (only add base languages if missing)
            required_tools = {}

            # Only add base languages if they're not already installed
            if not has_python:
                required_tools["python"] = "3.11"
                console.print("[yellow]⚠[/yellow] Python not found, will install via mise")
            else:
                console.print(f"[green]✓[/green] Python already installed")

            if not has_node:
                required_tools["node"] = "20"
                console.print("[yellow]⚠[/yellow] Node.js not found, will install via mise")
            else:
                console.print(f"[green]✓[/green] Node.js already installed")

            if not has_go:
                required_tools["go"] = "1.21"
                console.print("[yellow]⚠[/yellow] Go not found, will install via mise")
            else:
                console.print(f"[green]✓[/green] Go already installed")

            if not has_java:
                required_tools["java"] = "openjdk-17"
                console.print("[yellow]⚠[/yellow] Java not found, will install via mise")
            else:
                console.print(f"[green]✓[/green] Java already installed")

            # Always add the specific tool packages
            required_tools.update({
                "npm:@mermaid-js/mermaid-cli": "latest",
                "npm:@marp-team/marp-cli": "latest",
                "pipx:mkdocs": "latest",
                # Note: mkdocs-material cannot be installed via mise pipx
                # Users should install it manually: pipx install mkdocs-material
                "go:oss.terrastruct.com/d2": "latest"
            })

            # Add required tools to config
            tools_added = []
            for tool, version in required_tools.items():
                if tool not in config["tools"]:
                    config["tools"][tool] = version
                    tools_added.append(tool.split(":")[-1])

            # Add PlantUML setup task if not exists
            if "tasks" not in config:
                config["tasks"] = {}

            if "setup-plantuml" not in config.get("tasks", {}):
                config["tasks"]["setup-plantuml"] = {
                    "description": "Download and setup PlantUML",
                    "run": """mkdir -p ~/.local/bin
curl -L https://github.com/plantuml/plantuml/releases/download/v1.2024.0/plantuml-1.2024.0.jar -o ~/.local/bin/plantuml.jar
echo '#!/bin/bash\\njava -jar ~/.local/bin/plantuml.jar "$@"' > ~/.local/bin/plantuml
chmod +x ~/.local/bin/plantuml
echo "PlantUML installed to ~/.local/bin/plantuml"
"""
                }

            # Write updated config
            try:
                with open(mise_config_path, "w") as f:
                    toml.dump(config, f)
                if tools_added:
                    console.print(f"[green]✓[/green] Added tools to mise.toml: {', '.join(tools_added)}")
                else:
                    console.print("[green]✓[/green] mise.toml already has all required tools")
            except Exception as e:
                console.print(f"[red]✗[/red] Could not write mise.toml: {e}")

            # Run mise install to install the tools
            console.print("[cyan]→[/cyan] Running [bold]mise install[/bold] to install tools...")
            try:
                result = subprocess.run(
                    ["mise", "install"],
                    capture_output=False,  # Show output to user
                    text=True,
                    cwd=Path.cwd()
                )
                if result.returncode == 0:
                    console.print("[green]✓[/green] mise install completed successfully")

                    # Run PlantUML setup
                    console.print("[cyan]→[/cyan] Setting up PlantUML...")
                    plantuml_result = subprocess.run(
                        ["mise", "run", "setup-plantuml"],
                        capture_output=False,
                        text=True,
                        cwd=Path.cwd()
                    )
                    if plantuml_result.returncode == 0:
                        console.print("[green]✓[/green] PlantUML setup completed")
                    else:
                        console.print("[yellow]⚠[/yellow] PlantUML setup had issues - run [cyan]mise run setup-plantuml[/cyan] manually")
                else:
                    console.print("[yellow]⚠[/yellow] mise install had issues - please run [cyan]mise install[/cyan] manually")
            except Exception as e:
                console.print(f"[yellow]⚠[/yellow] Could not run mise install: {e}")
                console.print("[cyan]→[/cyan] Please run [bold]mise install[/bold] manually")

            # Check which tools are available after installation
            console.print("\n[cyan]→[/cyan] Verifying tool installation...")
            tools_status = {
                "D2": shutil.which("d2") is not None,
                "Mermaid CLI": shutil.which("mmdc") is not None,
                "MkDocs": shutil.which("mkdocs") is not None,
                "Marp": shutil.which("marp") is not None,
                "PlantUML": Path("~/.local/bin/plantuml.jar").expanduser().exists()
            }

            # Report status
            missing_tools = [name for name, installed in tools_status.items() if not installed]
            if missing_tools:
                console.print(f"[yellow]⚠[/yellow] Some tools are not available: {', '.join(missing_tools)}")
                console.print("[cyan]→[/cyan] Try running [bold]mise install[/bold] again or check your PATH")
            else:
                console.print("[green]✓[/green] All required tools are installed!")
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
            "   - Documentation Agents: Generate docs (MkDocs, Zudoku)\n"
            "   - Presentation Agent: Create slide presentations\n"
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
    console.print("1. Install mkdocs-material: [cyan]pipx install mkdocs-material[/cyan]")
    console.print("2. Verify installation: [cyan]t2d verify[/cyan]")
    console.print("3. Test recipe commands: [cyan]t2d recipe list[/cyan]")
    console.print("4. Create your first recipe or use Claude to transform one!")
    console.print("\n[dim]If any tools are missing, run [cyan]mise install[/cyan] manually[/dim]")
