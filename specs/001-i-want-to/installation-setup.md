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

### Desktop Commander Usage

Desktop Commander is the execution environment for running Claude CLI commands. No configuration needed - it simply executes:
- Claude Code agent commands
- MCP server interactions
- CLI tool invocations

Example usage:
```bash
# Desktop Commander runs Claude CLI to execute agents
desktop-commander claude-code "Use the t2d-transform agent on recipe.yaml"
```

## Installation Process

### 1. Python Package Structure

```python
# pyproject.toml
[project]
name = "t2d-kit"
version = "1.0.0"

[project.scripts]
t2d = "t2d_kit.cli:main"

[tool.setuptools.package-data]
t2d_kit = [
    "agents/**/*.txt",
    "agents/**/*.yaml",
    "commands/**/*",
    "templates/**/*",
]
```

### 2. CLI Setup Command

```python
# cli/main.py
import click
import shutil
import os
from pathlib import Path
import subprocess

@click.group()
def cli():
    """t2d-kit: Multi-framework diagram pipeline."""
    pass

@cli.command()
@click.argument('working_dir', type=click.Path(exists=True), default='.')
def mcp(working_dir):
    """Start the MCP server for Claude Desktop integration.

    Args:
        working_dir: Working directory for recipes (default: current directory)
    """
    from t2d_kit.mcp.server import main
    import asyncio

    click.echo(f"Starting t2d-kit MCP server in {working_dir}...")
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

@cli.command()
@click.option('--force', is_flag=True, help='Overwrite existing files')
def setup(force):
    """Install Claude Code agents and slash commands."""

    # Detect Claude Code installation
    claude_home = find_claude_home()
    if not claude_home:
        click.echo("⚠️  Claude Code not found. Please install Claude Desktop first.")
        return 1

    # Install agent files
    install_claude_agents(claude_home, force)

    # Install slash commands
    install_slash_commands(claude_home, force)

    # Setup mise dependencies
    setup_mise_dependencies()

    click.echo("✅ t2d-kit setup complete!")
    click.echo(f"   Claude agents installed to: {claude_home}")
    click.echo("\n📝 Available commands:")
    click.echo("   /t2d-transform - Transform user recipe to processed recipe")
    click.echo("   /t2d-create    - Process recipe and generate outputs")

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
    """Install agent markdown files."""
    source_dir = Path(__file__).parent.parent / "agents"
    target_dir = claude_home / "agents"

    if target_dir.exists() and not force:
        if not click.confirm(f"Agent files already exist at {target_dir}. Overwrite?"):
            return

    # Create directory structure
    target_dir.mkdir(parents=True, exist_ok=True)

    # Agent definitions to install
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

    # Copy agent files
    for agent_name in agents:
        source_file = source_dir / f"{agent_name}.md"
        target_file = target_dir / f"{agent_name}.md"

        if source_file.exists():
            shutil.copy2(source_file, target_file)
            click.echo(f"   Installed agent: {agent_name}")

def install_slash_commands(claude_home, force):
    """Install slash command definitions."""
    source_dir = Path(__file__).parent.parent / "commands"
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
```

## Package Structure

```
t2d-kit/
├── pyproject.toml
├── setup.py
├── t2d_kit/
│   ├── __init__.py
│   ├── cli.py
│   ├── mcp/
│   │   ├── server.py
│   │   └── models.py
│   ├── agents/           # Bundled agent files (Markdown with YAML frontmatter)
│   │   ├── t2d-transform.md
│   │   ├── t2d-orchestrate.md
│   │   ├── t2d-d2-generator.md
│   │   ├── t2d-mermaid-generator.md
│   │   ├── t2d-plantuml-generator.md
│   │   ├── t2d-markdown-maintainer.md
│   │   ├── t2d-mkdocs-formatter.md
│   │   └── t2d-marp-slides.md
│   └── commands/         # Slash command scripts
│       ├── t2d-transform
│       └── t2d-create
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
tools: Read, Write, Edit, Bash
---

You are a D2 diagram generator agent for t2d-kit.

Given diagram specifications, generate D2 code that:
1. Follows D2 best practices
2. Uses appropriate shapes and connections
3. Includes clear labels
4. Optimizes for readability

Process:
1. Read the diagram specification
2. Generate D2 code based on instructions
3. Save to the specified .d2 file
4. Run d2 command to generate SVG/PNG
5. Report success or errors

Use the d2 CLI tool for rendering:
- `d2 input.d2 output.svg` for SVG output
- `d2 input.d2 output.png --format png` for PNG output

Ensure the generated D2 code is valid and renders correctly.
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
2. Extract and analyze PRD content thoroughly
3. Map user diagram requests to specific diagram types
4. Generate detailed diagram specifications with complete DSL
5. Create content file definitions for documentation/presentation
6. Write processed recipe using MCP write_processed_recipe tool

Analysis approach:
- Identify all system components from PRD
- Extract relationships and data flows
- Map natural language to specific diagram types
- Generate complete, executable instructions

Output should include:
- Detailed diagram specifications
- Content file definitions
- Output configuration for MkDocs/MarpKit
- Generation notes explaining decisions
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