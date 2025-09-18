# Installation and Setup Specification

**Date**: 2025-01-17
**Feature**: Multi-Framework Diagram Pipeline
**Branch**: 001-i-want-to

## Overview

When t2d-kit is installed via uvx, agent files and slash commands must be properly placed for Claude Code and Desktop Commander access.

## File Locations

### Claude Code Agent Files

Default locations for Claude Code resources:

```
# macOS/Linux
~/.claude/
├── agents/            # Subagents (user-level)
│   ├── t2d-transform.md
│   ├── t2d-orchestrate.md
│   ├── t2d-d2-generator.md
│   ├── t2d-mermaid-generator.md
│   ├── t2d-plantuml-generator.md
│   ├── t2d-markdown-maintainer.md
│   ├── t2d-mkdocs-formatter.md
│   └── t2d-marp-slides.md
└── commands/          # Slash commands
    ├── t2d-transform
    └── t2d-create

# Project-level agents (higher priority)
.claude/
└── agents/            # Project-specific agents
    └── (same .md files as above)

# Windows
%APPDATA%\Claude\
└── (same structure)
```


## Installation Process

### 1. Modern Python Package Structure (src layout)

```toml
# pyproject.toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "t2d-kit"
dynamic = ["version"]
requires-python = ">=3.11"
dependencies = [
    "click>=8.1",
    "pydantic>=2.0",
    "fastmcp>=0.2.0",
    "pyyaml>=6.0",
]

[project.scripts]
t2d = "t2d_kit.cli.main:cli"

[tool.hatch.version]
path = "src/t2d_kit/_version.py"

[tool.hatch.build.targets.wheel]
packages = ["src/t2d_kit"]

[tool.hatch.build.targets.wheel.data]
"src/t2d_kit/agents" = "t2d_kit/agents"
```

### 2. Package Initialization Files

```python
# src/t2d_kit/__init__.py
"""t2d-kit: Multi-framework diagram pipeline for Claude Code."""

__version__ = "1.0.0"

# src/t2d_kit/_version.py
"""Single source of truth for version."""
__version__ = "1.0.0"

# src/t2d_kit/cli/__init__.py
"""CLI module for t2d-kit."""
from .main import cli

__all__ = ["cli"]

# src/t2d_kit/mcp/__init__.py
"""FastMCP server for recipe management."""
from .server import mcp

__all__ = ["mcp"]

# src/t2d_kit/agents/__init__.py
"""Claude Code subagents bundled with package."""
# Agent markdown files are resources, not Python modules
```

### 3. Type Checking Support

```python
# src/t2d_kit/py.typed
# This file marks the package as PEP 561 compliant
# for type checking with mypy and other tools
```

### 4. CLI Setup Command with importlib.resources

```python
# src/t2d_kit/cli/main.py
import click
from pathlib import Path
import subprocess
from importlib import resources
import shutil

@click.group()
def cli():
    """t2d-kit: Multi-framework diagram pipeline."""
    pass

@cli.command()
@click.option('--init', is_flag=True, help='Create a new recipe.yaml file')
@click.option('--name', help='Project name for new recipe')
@click.option('--force', is_flag=True, help='Overwrite existing files')
def setup(init, name, force):
    """Setup t2d-kit: install agents, commands, and optionally create a recipe."""
    # First, always do the setup steps
    # Detect Claude Code installation
    claude_home = find_claude_home()
    if not claude_home:
        click.echo("⚠️  Claude Code not found. Please install Claude Desktop first.")
        return 1

    # Install agent files using importlib.resources
    install_claude_agents(claude_home, force)

    # Install slash commands (deprecated - use natural language)
    # install_slash_commands(claude_home, force)

    # Setup mise dependencies
    setup_mise_dependencies()

    click.echo("✅ t2d-kit setup complete!")
    click.echo(f"   Claude agents installed to: {claude_home}")
    click.echo("\n📝 Available commands:")
    click.echo("   /t2d-transform - Transform user recipe to processed recipe")
    click.echo("   /t2d-create    - Process recipe and generate outputs")

    # Optionally create a recipe
    if init:
        if not name:
            name = click.prompt("\nProject name", default="My Project")

        import yaml
        from pathlib import Path

        recipe = {
            'recipe': {
                'name': name,
                'version': '1.0.0',
                'prd': {
                    'content': '# Add your PRD content here\n\nDescribe your system requirements...'
                },
                'instructions': {
                    'diagrams': [
                        {'type': 'architecture', 'description': 'System architecture overview'},
                        {'type': 'sequence', 'description': 'Key user flows'},
                        {'type': 'erd', 'description': 'Data model'}
                    ],
                    'documentation': {
                        'style': 'technical',
                        'audience': 'developers',
                        'include_diagrams_inline': True
                    },
                    'presentation': {
                        'audience': 'stakeholders',
                        'max_slides': 20,
                        'style': 'executive'
                    }
                }
            }
        }

        output_file = Path('recipe.yaml')
        if output_file.exists() and not click.confirm(f"\n{output_file} exists. Overwrite?"):
            output_file = Path(click.prompt("Output filename", default="recipe-new.yaml"))

        with open(output_file, 'w') as f:
            yaml.dump(recipe, f, default_flow_style=False, sort_keys=False)

        click.echo(f"\n✅ Created {output_file}")
        click.echo("\nNext steps:")
        click.echo(f"  1. Edit {output_file} to add your PRD content")
        click.echo(f"  2. In Claude Desktop: 'Transform recipe.yaml'")
        click.echo(f"  3. In Claude Desktop: 'Process recipe and preview'")

@cli.command()
@click.argument('working_dir', type=click.Path(exists=True), default='.')
def mcp(working_dir):
    """Start the FastMCP server for Claude Desktop integration.

    Args:
        working_dir: Working directory for recipes (default: current directory)
    """
    from t2d_kit.mcp.server import mcp as fastmcp_server
    import asyncio
    import json

    click.echo(f"Starting t2d-kit FastMCP server in {working_dir}...")
    click.echo("Add this to your Claude Desktop MCP settings:")
    click.echo(json.dumps({
        "mcpServers": {
            "t2d-kit": {
                "command": "t2d",
                "args": ["mcp", working_dir]
            }
        }
    }, indent=2))

    try:
        asyncio.run(main(working_dir))
    except KeyboardInterrupt:
        click.echo("\nMCP server stopped.")

# Note: setup command is defined above with optional --init flag

def find_claude_home():
    """Find Claude Code installation directory."""
    possible_paths = [
        Path.home() / ".claude",
        Path.home() / ".config" / "claude",
        Path(os.environ.get("APPDATA", "")) / "Claude" if os.name == 'nt' else None,
    ]

    for path in possible_paths:
        if path and path.exists():
            return path

    # Check if Claude is in PATH
    try:
        result = subprocess.run(["claude", "--version"], capture_output=True)
        if result.returncode == 0:
            # Claude is installed, use default location
            return Path.home() / ".claude"
    except FileNotFoundError:
        pass

    return None

def install_claude_agents(claude_home, force):
    """Install agent markdown files using modern importlib.resources."""
    from importlib import resources
    import t2d_kit.agents

    target_dir = claude_home / "agents"

    if target_dir.exists() and not force:
        if not click.confirm(f"Agent files already exist at {target_dir}. Overwrite?"):
            return

    # Create directory structure
    target_dir.mkdir(parents=True, exist_ok=True)

    # Agent definitions bundled with package
    agents = [
        "t2d-transform",
        "t2d-orchestrate",
        "t2d-d2-generator",
        "t2d-mermaid-generator",
        "t2d-plantuml-generator",
        "t2d-markdown-maintainer",
        "t2d-mkdocs-formatter",
        "t2d-marp-slides"
    ]

    # Copy agent files from package resources using importlib
    for agent_name in agents:
        try:
            # Read agent file from bundled package data
            agent_files = resources.files(t2d_kit.agents)
            agent_file = agent_files / f"{agent_name}.md"

            if agent_file.is_file():
                agent_content = agent_file.read_text()

                # Write to Claude agents directory
                target_file = target_dir / f"{agent_name}.md"
                target_file.write_text(agent_content)
                click.echo(f"   Installed agent: {agent_name}")
            else:
                click.echo(f"   Warning: Agent {agent_name} not found in package")
        except Exception as e:
            click.echo(f"   Error installing {agent_name}: {e}")

def install_slash_commands(claude_home, force):
    """Install slash command definitions (deprecated - use natural language)."""
    # Note: Slash commands are deprecated in favor of natural language invocation
    # This function is kept for backward compatibility
    target_dir = claude_home / "commands"

    target_dir.mkdir(parents=True, exist_ok=True)

    # Command definitions
    commands = {
        "t2d-transform": {
            "description": "Transform user recipe into processed recipe",
            "script": "desktop-commander claude-code transform",
            "args": ["recipe_file"],
        },
        "t2d-create": {
            "description": "Process recipe and generate outputs",
            "script": "desktop-commander claude-code orchestrate",
            "args": ["recipe_file"],
        }
    }

    for cmd_name, cmd_def in commands.items():
        cmd_file = target_dir / cmd_name
        if cmd_file.exists() and not force:
            if not click.confirm(f"Command /{cmd_name} already exists. Overwrite?"):
                continue

        # Write command definition
        with open(cmd_file, 'w') as f:
            f.write(f"#!/usr/bin/env bash\n")
            f.write(f"# {cmd_def['description']}\n")
            f.write(f"{cmd_def['script']} $@\n")

        # Make executable
        cmd_file.chmod(0o755)
        click.echo(f"   Installed: /{cmd_name}")

def setup_mise_dependencies():
    """Ensure mise and dependencies are installed."""
    # Check for mise
    try:
        subprocess.run(["mise", "--version"], capture_output=True, check=True)
        # Run mise install
        subprocess.run(["mise", "install"], check=True)
        click.echo("   ✓ Dependencies installed via mise")
    except FileNotFoundError:
        click.echo("   ⚠️  mise not found - run 'curl https://mise.run | sh' to install")

@cli.command()
def verify():
    """Verify t2d-kit installation and dependencies."""
    import shutil

    checks = {
        "Claude Code": False,
        "Agent files": False,
        "Slash commands": False,
        "mise": False,
        "D2": False,
        "Mermaid CLI": False,
        "PlantUML": False,
        "MkDocs": False,
        "Marp": False
    }

    # Check Claude Code
    claude_home = find_claude_home()
    if claude_home and claude_home.exists():
        checks["Claude Code"] = True

        # Check agent files
        agent_dir = claude_home / "agents"
        if agent_dir.exists() and list(agent_dir.glob("t2d-*.md")):
            checks["Agent files"] = True

        # Check slash commands
        cmd_dir = claude_home / "commands"
        if cmd_dir.exists() and (cmd_dir / "t2d-transform").exists():
            checks["Slash commands"] = True

    # Check mise
    if shutil.which("mise"):
        checks["mise"] = True

    # Check D2
    if shutil.which("d2"):
        checks["D2"] = True

    # Check Mermaid CLI
    if shutil.which("mmdc"):
        checks["Mermaid CLI"] = True

    # Check PlantUML
    plantuml_jar = Path.home() / ".local/share/plantuml/plantuml.jar"
    if plantuml_jar.exists() or shutil.which("plantuml"):
        checks["PlantUML"] = True

    # Check MkDocs
    if shutil.which("mkdocs"):
        checks["MkDocs"] = True

    # Check Marp
    if shutil.which("marp"):
        checks["Marp"] = True

    # Print results
    click.echo("\n🔍 t2d-kit Installation Check:\n")
    for component, status in checks.items():
        icon = "✓" if status else "✗"
        color = "green" if status else "red"
        click.secho(f"   {icon} {component}", fg=color)

    # Overall status
    all_good = all(checks.values())
    critical_good = checks["Claude Code"] and checks["Agent files"]

    if all_good:
        click.echo("\n✅ All components installed and ready!")
    elif critical_good:
        click.echo("\n⚠️  Core components ready, but some tools missing.")
        click.echo("   Run: t2d setup")
    else:
        click.echo("\n❌ Installation incomplete. Run: t2d setup")

    return 0 if critical_good else 1
```

## UV Lock File for Reproducible Builds

```toml
# uv.lock is automatically generated by UV
# This ensures reproducible installations across environments
# DO NOT edit manually - use 'uv lock' to update

[[package]]
name = "t2d-kit"
version = "1.0.0"
dependencies = [
    "click>=8.1",
    "pydantic>=2.0",
    "fastmcp>=0.2.0",
    "pyyaml>=6.0"
]

[tool.uv]
dev-dependencies = [
    "pytest>=8.0",
    "pytest-asyncio>=0.21",
    "mypy>=1.7",
    "ruff>=0.1.0",
    "black>=23.0"
]
```

## Testing Configuration

```python
# tests/conftest.py
"""Pytest configuration for t2d-kit tests."""
import pytest
from pathlib import Path
from t2d_kit.mcp.models import UserRecipe, ProcessedRecipe

@pytest.fixture
def sample_user_recipe():
    """Provide a sample user recipe for testing."""
    return UserRecipe(
        name="test-project",
        prd={"content": "Test PRD content"},
        instructions={
            "diagrams": [
                {"type": "architecture", "description": "System overview"}
            ]
        }
    )

@pytest.fixture
def temp_recipe_dir(tmp_path):
    """Provide a temporary directory for recipe files."""
    recipe_dir = tmp_path / "recipes"
    recipe_dir.mkdir()
    return recipe_dir
```

## Package Structure (src layout)

```
t2d-kit/
├── src/
│   └── t2d_kit/
│       ├── __init__.py
│       ├── py.typed             # Type checking marker
│       ├── _version.py          # Version management
│       ├── cli/
│       │   ├── __init__.py
│       │   └── main.py          # CLI entry point
│       ├── mcp/
│       │   ├── __init__.py
│       │   ├── server.py        # FastMCP server
│       │   ├── models.py        # Pydantic models
│       │   └── __main__.py      # Server entry
│       └── agents/              # Bundled agent files
│           ├── __init__.py
│           ├── t2d-transform.md
│           ├── t2d-orchestrate.md
│           ├── t2d-d2-generator.md
│           ├── t2d-mermaid-generator.md
│           ├── t2d-plantuml-generator.md
│           ├── t2d-markdown-maintainer.md
│           ├── t2d-mkdocs-formatter.md
│           └── t2d-marp-slides.md
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── unit/
│   ├── integration/
│   └── fixtures/
├── docs/
├── examples/
│   ├── recipe.yaml
│   └── recipe.t2d.yaml
├── pyproject.toml
├── uv.lock
├── .mise.toml
└── README.md
```

## User Installation Flow

### 1. Install via uvx
```bash
# Install t2d-kit globally
uvx install t2d-kit

# This installs:
# - t2d CLI command
# - MCP server
# - Agent files (bundled)
```

### 2. Run Setup
```bash
# Setup Claude Code integration
t2d setup

# Output:
# ✅ t2d-kit setup complete!
#    Claude agents installed to: ~/.claude
#
# 📝 Available commands:
#    /t2d-transform - Transform user recipe
#    /t2d-create    - Process recipe
```

### 3. Install Dependencies
```bash
# Install diagram tools via mise
t2d setup-tools

# Or manually:
mise install
```

## Agent File Templates

### Example: agents/t2d-d2-generator.md
```markdown
---
name: t2d-d2-generator
description: D2 diagram generator for t2d-kit. Use proactively when processing D2 diagram specifications.
tools: Read, Write
---

You are a D2 diagram generator agent for t2d-kit.

Given diagram specifications, generate D2 code that:
1. Follows D2 best practices
2. Uses appropriate shapes and connections
3. Includes clear labels
4. Optimizes for readability

Process:
1. Receive diagram specification with instructions prompt
2. Interpret the natural language instructions
3. Generate D2 code based on instructions
4. Save to the specified .d2 file using Write tool
5. Report completion

NOTE: You only generate the .d2 source file. The orchestrator will run the d2 CLI command to create the SVG/PNG outputs.

Ensure the generated D2 code is valid syntax.
```

### Example: agents/t2d-transform.md
```markdown
---
name: t2d-transform
description: Recipe transformer for t2d-kit. Transforms user recipes (recipe.yaml) into detailed processed recipes (recipe.t2d.yaml). Use proactively for recipe transformation.
tools: Read, Write, mcp__t2d-kit__read_user_recipe, mcp__t2d-kit__write_processed_recipe
---

You are the t2d-kit recipe transformer.

Task: Transform a user recipe (recipe.yaml) into a processed recipe (recipe.t2d.yaml)

Steps:
1. Read user recipe using MCP read_user_recipe tool
2. If PRD is file_path, read it using Read tool
3. Extract and analyze PRD content thoroughly
4. Map user diagram requests to specific diagram types and assign agents
5. Create DiagramSpecification objects with agent assignments
6. Create DiagramReference objects with expected paths
7. Create ContentFile objects with base_prompt and diagram_refs
8. Write processed recipe using MCP write_processed_recipe tool

Output should include:
- Detailed diagram specifications with agent field
- DiagramReference objects with expected paths
- Content file definitions with base_prompt (no diagram list)
- Output configuration for MkDocs/Marp
- Generation notes explaining decisions
```

### Example: agents/t2d-orchestrate.md
```markdown
---
name: t2d-orchestrate
description: Recipe orchestrator for t2d-kit. Processes recipe.t2d.yaml and coordinates all generation.
tools: Read, Write, Bash, Task, mcp__t2d-kit__read_processed_recipe
---

You are the t2d-kit orchestrator that processes recipes and coordinates diagram generation.

Process:
1. Read recipe.t2d.yaml using MCP tool
2. For each diagram specification:
   - Invoke the specified agent (from agent field)
   - Pass the instructions prompt
3. After all source files generated, build diagrams:
   - Run d2 CLI for .d2 files
   - Run mmdc CLI for .mmd files
   - Run plantuml for .puml files
4. Update DiagramReference objects with actual paths
5. For each content file:
   - Combine base_prompt with diagram references
   - Invoke content agent with combined prompt
6. Generate final outputs:
   - Run mkdocs build for documentation
   - Run marp for presentations

PREVIEW MODE:
If the user requests preview (e.g., "process and preview", "show me a preview"):
1. After generating content, start appropriate preview servers:
   - For documentation: `mkdocs serve --dev-addr 0.0.0.0:8000 &`
   - For presentations: `marp --watch content/slides.md --server &`
   - For diagrams: `d2 --watch *.d2 --host 0.0.0.0:8001 &` (if requested)
2. Report URLs to user:
   - Documentation: http://localhost:8000
   - Presentation: http://localhost:8080
   - Note: Files will auto-reload on changes

Use Bash tool for all CLI commands.
Run preview servers in background with & for non-blocking execution.
```

### Example: agents/t2d-markdown-maintainer.md
```markdown
---
name: t2d-markdown-maintainer
description: Markdown content maintainer for t2d-kit documentation.
tools: Read, Write
---

You maintain markdown documentation files.

When invoked, you receive:
- Base instructions for content creation
- List of available diagrams with paths

Create comprehensive markdown documentation that:
1. Follows the specified style and audience
2. Embeds diagrams using markdown image syntax
3. Includes appropriate sections
4. Maintains consistent formatting

Save files using Write tool.
```

## Post-Install Verification

### Check Installation
```bash
# Verify installation
t2d verify

# Checks:
# ✓ Claude Code found
# ✓ Agent files installed
# ✓ Slash commands available
# ✓ mise installed
# ✓ D2 available
# ✓ Mermaid CLI available
# ✓ MCP server functional
```

### Test Commands
```bash
# Test transformation
echo "recipe: {name: test}" > test.yaml
/t2d-transform test.yaml

# Should create test.t2d.yaml
```

## Updating Agents

### Manual Update
```bash
# Re-run setup to update agents
t2d setup --force
```

### Version Management
```python
# Track agent version in package
AGENT_VERSION = "1.0.0"

def check_agent_updates():
    """Check if agents need updating."""
    installed_version = read_installed_version()
    if installed_version < AGENT_VERSION:
        click.echo(f"Agent update available: {AGENT_VERSION}")
        click.echo("Run 't2d setup --force' to update")
```

## Distribution Considerations

### Package Size
- Agent files are text, minimal size impact
- Bundle only essential prompts
- Optional agents can be downloaded

### Platform Support
- Cross-platform paths (Windows/macOS/Linux)
- Detect Claude installation correctly
- Handle missing Desktop Commander gracefully

### Security
- Validate agent files before installation
- Don't overwrite user customizations without consent
- Use secure file permissions

---
*Installation setup defined: 2025-01-17*