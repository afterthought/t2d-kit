"""T2D Kit MCP Server - Provides schema and documentation resources for Claude Code agents."""

from fastmcp import FastMCP

from t2d_kit.models.user_recipe import UserRecipe
from t2d_kit.models.processed_recipe import ProcessedRecipe
from t2d_kit.utils.schema_formatter import (
    format_schema_markdown,
    format_schema_agent_friendly,
)

# Initialize MCP server
mcp = FastMCP("t2d-kit")


# ============================================================================
# Schema Resources
# ============================================================================


@mcp.resource("recipe://schema/user", mime_type="application/json")
def get_user_recipe_schema() -> dict:
    """Get the complete JSON schema for UserRecipe.

    This resource provides the raw JSON schema for programmatic use.
    For human-readable documentation, use recipe://docs/user-recipe instead.
    """
    return UserRecipe.model_json_schema()


@mcp.resource("recipe://schema/processed", mime_type="application/json")
def get_processed_recipe_schema() -> dict:
    """Get the complete JSON schema for ProcessedRecipe.

    This resource provides the raw JSON schema for programmatic use.
    For human-readable documentation, use recipe://docs/processed-recipe instead.
    """
    return ProcessedRecipe.model_json_schema()


@mcp.resource("recipe://schema/user/agent-friendly", mime_type="text/plain")
def get_user_recipe_schema_agent() -> str:
    """Get agent-friendly UserRecipe schema with concise field descriptions.

    Optimized for Claude Code agents to quickly understand the schema structure.
    """
    schema = UserRecipe.model_json_schema()
    return format_schema_agent_friendly(schema, "UserRecipe")


@mcp.resource("recipe://schema/processed/agent-friendly", mime_type="text/plain")
def get_processed_recipe_schema_agent() -> str:
    """Get agent-friendly ProcessedRecipe schema with concise field descriptions.

    Optimized for Claude Code agents to quickly understand the schema structure.
    """
    schema = ProcessedRecipe.model_json_schema()
    return format_schema_agent_friendly(schema, "ProcessedRecipe")


# ============================================================================
# Documentation Resources
# ============================================================================


@mcp.resource("recipe://docs/user-recipe", mime_type="text/markdown")
def get_user_recipe_docs() -> str:
    """Complete UserRecipe documentation with schema, examples, and usage guidance.

    This is the recommended resource for understanding how to create UserRecipes.
    It combines schema information, field descriptions, validation rules, and
    practical examples in a single comprehensive document.
    """
    schema = UserRecipe.model_json_schema()
    return format_schema_markdown(schema, "UserRecipe")


@mcp.resource("recipe://docs/processed-recipe", mime_type="text/markdown")
def get_processed_recipe_docs() -> str:
    """Complete ProcessedRecipe documentation with schema, examples, and usage guidance.

    This is the recommended resource for understanding ProcessedRecipe structure.
    It combines schema information, field descriptions, validation rules, and
    practical examples in a single comprehensive document.
    """
    schema = ProcessedRecipe.model_json_schema()
    return format_schema_markdown(schema, "ProcessedRecipe")


@mcp.resource("recipe://docs/quick-start", mime_type="text/markdown")
def get_quick_start_guide() -> str:
    """Quick start guide for creating recipes with t2d-kit.

    Provides step-by-step instructions for creating, validating, and transforming recipes.
    """
    return """# T2D Kit Quick Start Guide

## Creating a UserRecipe

1. **Check the schema** to understand structure:
   ```bash
   t2d recipe schema --type user --format agent
   ```

2. **Create your recipe** in `./recipes/<name>.yaml`:
   ```yaml
   name: my-system
   version: 1.0.0
   prd:
     file_path: ./docs/prd.md
     format: markdown
   instructions:
     diagrams:
       - type: architecture
         description: High-level system architecture
       - type: sequence
         description: User authentication flow
   ```

3. **Validate your recipe**:
   ```bash
   t2d recipe validate my-system --type user
   ```

4. **Transform to ProcessedRecipe**:
   ```bash
   t2d transform ./recipes/my-system.yaml
   ```

## Using the CLI

### List all recipes:
```bash
t2d recipe list
```

### Load a recipe:
```bash
t2d recipe load my-system --type user --json
```

### Save a recipe:
```bash
echo '<json-data>' | t2d recipe save my-system --type user --data -
```

### Get schema documentation:
```bash
# Agent-friendly format (concise)
t2d recipe schema --type user --format agent

# Markdown format (detailed)
t2d recipe schema --type user --format markdown

# JSON format (programmatic)
t2d recipe schema --type user --format json
```

## Common Patterns

### Minimal Recipe
```yaml
name: simple-system
prd:
  content: |
    # System Design

    We need to build an API gateway...
instructions:
  diagrams:
    - type: architecture
```

### Recipe with Multiple Diagrams
```yaml
name: complex-system
prd:
  file_path: ./docs/requirements.md
instructions:
  diagrams:
    - type: c4_container
      description: Container-level architecture
      layout_engine: elk
    - type: sequence
      description: Payment processing flow
    - type: erd
      description: Database schema
```

### Recipe with Styling
```yaml
name: styled-system
prd:
  file_path: ./docs/prd.md
instructions:
  diagrams:
    - type: architecture
      theme: 3  # Light theme
      dark_theme: 200  # Dark theme
      sketch: true  # Hand-drawn style
```

## Troubleshooting

### Validation Errors
```bash
# Detailed validation output
t2d recipe validate my-system --type user --json
```

### Check Available Examples
```bash
# See all type definitions in schema
t2d recipe schema --type user --format markdown
```

## Next Steps

1. Explore the full schema: `recipe://docs/user-recipe`
2. Check examples: `recipe://examples/recipes`
3. Read agent documentation in `~/.claude/agents/t2d-*.md`
"""


# ============================================================================
# Example Resources
# ============================================================================


@mcp.resource("recipe://examples/recipes", mime_type="text/markdown")
def get_recipe_examples() -> str:
    """Collection of complete UserRecipe examples covering common use cases."""
    examples = {
        "minimal": {
            "name": "minimal-example",
            "version": "1.0.0",
            "prd": {
                "content": "# API Gateway\n\nWe need a simple API gateway for routing requests.",
                "format": "markdown",
            },
            "instructions": {"diagrams": [{"type": "architecture"}]},
        },
        "multi_diagram": {
            "name": "payment-system",
            "version": "1.0.0",
            "prd": {"file_path": "./docs/payment-prd.md", "format": "markdown"},
            "instructions": {
                "diagrams": [
                    {
                        "type": "architecture",
                        "description": "High-level payment system architecture",
                    },
                    {
                        "type": "sequence",
                        "description": "Payment processing flow from request to confirmation",
                    },
                    {"type": "erd", "description": "Payment database schema"},
                ]
            },
        },
        "with_styling": {
            "name": "styled-system",
            "version": "1.0.0",
            "prd": {"file_path": "./docs/requirements.md", "format": "markdown"},
            "instructions": {
                "diagrams": [
                    {
                        "type": "c4_container",
                        "description": "Microservices architecture",
                        "layout_engine": "elk",
                        "theme": 100,
                        "dark_theme": 200,
                    },
                    {"type": "sequence", "description": "Auth flow", "sketch": True},
                ]
            },
            "preferences": {
                "default_framework": "d2",
                "diagram_style": "modern",
                "color_scheme": "pastel",
            },
        },
        "with_docs": {
            "name": "documented-system",
            "version": "1.0.0",
            "prd": {"file_path": "./docs/system-design.md", "format": "markdown"},
            "instructions": {
                "diagrams": [{"type": "architecture"}, {"type": "sequence"}],
                "documentation": {
                    "style": "technical",
                    "audience": "engineering team",
                    "detail_level": "comprehensive",
                    "include_code_examples": True,
                    "include_diagrams_inline": True,
                },
            },
        },
        "with_presentation": {
            "name": "presentation-ready",
            "version": "1.0.0",
            "prd": {"file_path": "./docs/proposal.md", "format": "markdown"},
            "instructions": {
                "diagrams": [
                    {"type": "architecture"},
                    {"type": "flowchart"},
                    {"type": "c4_container"},
                ],
                "presentation": {
                    "audience": "executive stakeholders",
                    "max_slides": 20,
                    "style": "business",
                    "include_speaker_notes": True,
                    "time_limit": 30,
                },
            },
        },
    }

    lines = ["# UserRecipe Examples", ""]

    for name, example in examples.items():
        lines.extend([f"## {name.replace('_', ' ').title()}", "", "```yaml"])

        # Convert to YAML-like format manually for readability
        import yaml

        lines.append(yaml.dump(example, default_flow_style=False, sort_keys=False))
        lines.extend(["```", ""])

    return "\n".join(lines)


@mcp.resource("recipe://examples/diagram-types", mime_type="text/markdown")
def get_diagram_type_examples() -> str:
    """Examples of different diagram types and their configurations."""
    return """# Diagram Type Examples

## Architecture Diagrams

### Basic Architecture
```yaml
type: architecture
description: High-level system architecture
```

### Styled Architecture
```yaml
type: architecture
description: System architecture with custom styling
layout_engine: elk
theme: 3
dark_theme: 200
sketch: false
```

## Sequence Diagrams

### Basic Sequence
```yaml
type: sequence
description: User authentication flow
```

### Sketch-style Sequence
```yaml
type: sequence
description: Payment processing flow
sketch: true
```

## C4 Diagrams

### Container Diagram
```yaml
type: c4_container
description: Microservices container architecture
layout_engine: elk
theme: 100
```

### Context Diagram
```yaml
type: c4_context
description: System context and external dependencies
```

## Data Diagrams

### ERD (Entity Relationship)
```yaml
type: erd
description: Database schema for user management
```

### SQL Schema
```yaml
type: sql_schema
description: Detailed SQL table definitions
```

## Process Diagrams

### Flowchart
```yaml
type: flowchart
description: Order processing workflow
```

### State Diagram
```yaml
type: state
description: Order lifecycle states
```

## Class Diagrams

### UML Class Diagram
```yaml
type: class_diagram
description: Core domain models
```

## Supported Layout Engines (D2 only)

- `dagre` (default) - Fast, hierarchical layouts
- `elk` - Advanced layouts with better spacing
- `tala` - Experimental layout engine

## Supported Themes (D2 only)

### Light Themes
- 0: Neutral (default)
- 1-8: Various color schemes
- 100-105: Specialized themes
- 200: Terminal
- 300-301: Special themes

### Dark Themes
- Use `dark_theme` field for dark mode
- Supports same theme IDs as light themes
"""


# ============================================================================
# Main Entry Point
# ============================================================================


def main():
    """Run the T2D Kit MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()