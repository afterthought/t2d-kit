# t2d-kit API Reference

Transform requirements into beautiful diagrams and documentation with intelligent self-organizing agents.

## Table of Contents

- [MCP Tools](#mcp-tools)
- [CLI Commands](#cli-commands)
- [Model API](#model-api)
- [Agent Invocation Patterns](#agent-invocation-patterns)
- [Examples](#examples)

## MCP Tools

The t2d-kit MCP server provides tools for recipe management and processing. These tools enable Claude Code agents to read, write, and validate recipe files seamlessly.

### read_user_recipe

Reads and validates a user recipe YAML file.

**Signature:**
```python
async def read_user_recipe(file_path: str) -> Dict[str, Any]
```

**Parameters:**
- `file_path` (str): Path to the recipe.yaml file

**Returns:**
- Dict containing the validated user recipe data, or error details if validation fails

**Example:**
```python
# Read a user recipe
result = await read_user_recipe("./recipe.yaml")
if "error" not in result:
    print(f"Recipe loaded: {result['name']}")
    print(f"Diagrams requested: {len(result['instructions']['diagrams'])}")
```

**Raises:**
- `FileNotFoundError`: If the recipe file doesn't exist
- `ValidationError`: If the recipe data is invalid

### write_processed_recipe

Writes a processed recipe to a YAML file after validation.

**Signature:**
```python
async def write_processed_recipe(
    file_path: str,
    processed_data: Dict[str, Any]
) -> Dict[str, Any]
```

**Parameters:**
- `file_path` (str): Path where recipe.t2d.yaml will be written
- `processed_data` (Dict): The processed recipe data to write

**Returns:**
- Dict with success status and file path, or error details if validation fails

**Example:**
```python
# Write a processed recipe
processed_recipe = {
    "name": "User Management System",
    "version": "1.0.0",
    "source_recipe": "./recipe.yaml",
    "generated_at": datetime.now(),
    "diagram_specs": [...],
    "content_files": [...],
    "outputs": {...}
}

result = await write_processed_recipe("./recipe.t2d.yaml", processed_recipe)
if result.get("success"):
    print(f"Processed recipe written to: {result['file_path']}")
```

### read_processed_recipe

Reads a processed recipe from a YAML file.

**Signature:**
```python
async def read_processed_recipe(file_path: str) -> Dict[str, Any]
```

**Parameters:**
- `file_path` (str): Path to the recipe.t2d.yaml file

**Returns:**
- Dict containing the processed recipe data

**Example:**
```python
# Read a processed recipe
recipe = await read_processed_recipe("./recipe.t2d.yaml")
print(f"Generated at: {recipe['generated_at']}")
print(f"Diagram specs: {len(recipe['diagram_specs'])}")
```

### validate_recipe

Validates a recipe without reading/writing files.

**Signature:**
```python
async def validate_recipe(
    recipe_data: Dict[str, Any],
    recipe_type: str = "user"
) -> Dict[str, Any]
```

**Parameters:**
- `recipe_data` (Dict): The recipe data to validate
- `recipe_type` (str): Either "user" or "processed"

**Returns:**
- Dict with validation status and any errors

**Example:**
```python
# Validate recipe data
recipe_data = {...}
result = await validate_recipe(recipe_data, "user")
if result["valid"]:
    print("Recipe is valid!")
else:
    print(f"Validation errors: {result['errors']}")
```

### watch_recipe_changes

Watches for changes to recipe files in a directory.

**Signature:**
```python
async def watch_recipe_changes(directory: str = ".") -> Dict[str, Any]
```

**Parameters:**
- `directory` (str): Directory to watch for recipe files

**Returns:**
- Dict with list of recipe files found and their metadata

**Example:**
```python
# Watch for recipe changes
result = await watch_recipe_changes("./projects")
print(f"Found {result['recipe_count']} recipe files")
for recipe in result['recipes']:
    print(f"  {recipe['path']} - Modified: {recipe['modified']}")
```

## CLI Commands

The t2d CLI provides commands for setup, server management, and verification.

### setup

Sets up t2d-kit agents and dependencies.

**Usage:**
```bash
t2d setup [OPTIONS]
```

**Options:**
- `--agent-dir PATH`: Directory where Claude Code agents will be installed (default: ~/.claude/agents)
- `--force`: Overwrite existing agent files

**What it does:**
1. Installs Claude Code agents to ~/.claude/agents
2. Verifies mise dependencies
3. Sets up the environment for diagram generation

**Example:**
```bash
# Basic setup
t2d setup

# Custom agent directory with force overwrite
t2d setup --agent-dir ./my-agents --force
```

### mcp

Starts the MCP server for recipe management.

**Usage:**
```bash
t2d mcp [WORKING_DIR] [OPTIONS]
```

**Arguments:**
- `WORKING_DIR`: Working directory for the MCP server (default: current directory)

**Options:**
- `--port INTEGER`: Port to run the MCP server on (0 for stdio mode, default: 0)

**Example:**
```bash
# Start MCP server in stdio mode (for Claude Desktop)
t2d mcp

# Start MCP server in a specific directory
t2d mcp ./my-project

# Note: Network mode not yet supported by FastMCP
```

### verify

Verifies t2d-kit installation and dependencies.

**Usage:**
```bash
t2d verify [OPTIONS]
```

**Options:**
- `--verbose`: Show detailed verification information

**What it checks:**
- Claude Code agent installation
- Required tools (mise, Python, Node, Go, Java)
- Diagram tools (D2, Mermaid CLI, PlantUML)
- MCP server functionality

**Example:**
```bash
# Basic verification
t2d verify

# Detailed verification with table output
t2d verify --verbose
```

## Model API

T2d-kit uses Pydantic models for type-safe recipe management and validation.

### UserRecipe

User-maintained recipe with PRD content and high-level instructions.

**Fields:**
- `name` (str): Project name following naming conventions
- `version` (str): Semantic version (default: "1.0.0")
- `prd` (PRDContent): Product Requirements Document content
- `instructions` (UserInstructions): High-level generation instructions
- `preferences` (Optional[Preferences]): User preferences for generation
- `metadata` (Optional[Dict]): Additional metadata

**Example:**
```python
from t2d_kit.models import UserRecipe, PRDContent, UserInstructions

user_recipe = UserRecipe(
    name="user-management-system",
    version="1.0.0",
    prd=PRDContent(
        content="A web application for managing users...",
        format="markdown"
    ),
    instructions=UserInstructions(
        diagrams=[
            DiagramRequest(
                type="architecture",
                description="System architecture overview"
            ),
            DiagramRequest(
                type="entity_relationship",
                description="Database schema"
            )
        ],
        documentation=DocumentationInstructions(
            style="technical",
            audience="developers"
        )
    )
)
```

### ProcessedRecipe

Agent-generated recipe with detailed specifications.

**Fields:**
- `name` (str): Project name
- `version` (str): Semantic version
- `source_recipe` (str): Path to source user recipe
- `generated_at` (datetime): Generation timestamp
- `content_files` (List[ContentFile]): List of content files to generate
- `diagram_specs` (List[DiagramSpecification]): Detailed diagram specifications
- `diagram_refs` (List[DiagramReference]): Diagram metadata for content agents
- `outputs` (OutputConfig): Output configuration
- `generation_notes` (Optional[List[str]]): Notes from the generation process

**Example:**
```python
from t2d_kit.models import ProcessedRecipe, DiagramSpecification
from datetime import datetime

processed_recipe = ProcessedRecipe(
    name="user-management-system",
    version="1.0.0",
    source_recipe="./recipe.yaml",
    generated_at=datetime.now(),
    diagram_specs=[
        DiagramSpecification(
            id="arch-overview",
            title="Architecture Overview",
            type="architecture",
            framework="d2",
            instructions="Generate a high-level architecture diagram...",
            expected_path="docs/assets/architecture.d2"
        )
    ],
    diagram_refs=[
        DiagramReference(
            id="arch-overview",
            title="Architecture Overview",
            type="architecture",
            expected_path="docs/assets/architecture.d2"
        )
    ],
    content_files=[...],
    outputs=OutputConfig(assets_dir="docs/assets")
)
```

### DiagramSpecification

Detailed specification for diagram generation.

**Fields:**
- `id` (str): Unique identifier
- `title` (str): Human-readable title
- `type` (DiagramType): Type of diagram (architecture, sequence, etc.)
- `framework` (FrameworkType): Framework to use (d2, mermaid, plantuml)
- `instructions` (str): Detailed generation instructions
- `expected_path` (str): Where the diagram file should be created
- `dependencies` (Optional[List[str]]): Other diagrams this depends on
- `priority` (int): Generation priority (1-10)

### ContentFile

Specification for content file generation.

**Fields:**
- `path` (str): Output file path
- `type` (ContentType): Type of content (markdown, presentation)
- `title` (str): Content title
- `template` (Optional[str]): Template to use
- `sections` (List[str]): Sections to include
- `diagram_refs` (List[str]): Referenced diagram IDs
- `instructions` (str): Generation instructions

## Agent Invocation Patterns

T2d-kit uses intelligent self-organizing agents that activate based on proactive patterns.

### Transform Agent

**Agent:** `t2d-transform`
**Purpose:** Converts user recipes into processed recipes

**Activation Patterns:**
- User says "transform recipe.yaml"
- User mentions converting or processing a recipe file
- User asks to generate a processed recipe

**Tools:** Read, Write, MCP read_user_recipe, MCP write_processed_recipe

**Workflow:**
1. Read user recipe using MCP tool
2. Analyze PRD content and extract components
3. Map diagram requests to specific types
4. Generate detailed diagram specifications
5. Create content file specifications
6. Write processed recipe using MCP tool

### Diagram Generator Agents

**Agents:** `t2d-d2-generator`, `t2d-mermaid-generator`, `t2d-plantuml-generator`
**Purpose:** Generate specific types of diagrams

**Activation Patterns:**
- User requests diagram generation
- Processed recipe contains diagram specifications
- User mentions specific diagram frameworks

**Workflow:**
1. Read processed recipe
2. Find matching diagram specifications
3. Generate diagram source code
4. Validate syntax
5. Save to expected path

### Content Generator Agents

**Agents:** `t2d-docs-generator`, `t2d-slides-generator`
**Purpose:** Generate documentation and presentations

**Activation Patterns:**
- User requests documentation generation
- User mentions creating presentations
- Processed recipe contains content specifications

**Workflow:**
1. Read processed recipe and diagram references
2. Generate content based on specifications
3. Include diagram references and assets
4. Format according to templates

## Examples

### Complete Workflow Example

1. **Create User Recipe (recipe.yaml):**
```yaml
recipe:
  name: "e-commerce-platform"
  prd:
    content: |
      # E-Commerce Platform
      A modern web application for online shopping...
  instructions:
    diagrams:
      - type: "architecture"
        description: "System architecture overview"
      - type: "sequence"
        description: "User checkout flow"
    documentation:
      style: "technical"
      audience: "developers"
```

2. **Transform Recipe:**
```bash
# In Claude Code, the transform agent activates automatically
"Transform this recipe into a processed recipe"
```

3. **Generate Diagrams:**
```bash
# Diagram agents activate based on processed recipe
"Generate the architecture diagram using D2"
```

4. **Generate Documentation:**
```bash
# Documentation agent activates
"Create technical documentation with the generated diagrams"
```

### Direct MCP Usage

```python
# Using MCP tools directly
import asyncio
from t2d_kit.mcp.server import read_user_recipe, write_processed_recipe

async def process_recipe():
    # Read user recipe
    user_recipe = await read_user_recipe("./recipe.yaml")

    # Transform to processed recipe (would be done by transform agent)
    processed_data = transform_recipe(user_recipe)

    # Write processed recipe
    result = await write_processed_recipe("./recipe.t2d.yaml", processed_data)
    print(f"Processed recipe saved: {result['success']}")

asyncio.run(process_recipe())
```

### Agent Coordination Example

The agents coordinate automatically through the processed recipe:

1. **Transform Agent** creates `recipe.t2d.yaml` with specifications
2. **Diagram Agents** read specifications and generate diagrams
3. **Content Agents** read both specifications and diagram references
4. **State Management** tracks progress and dependencies

This coordination happens automatically when agents are properly installed and the MCP server is running.

### Claude Desktop Integration

Add to your Claude Desktop config:

```json
{
  "mcpServers": {
    "t2d-kit": {
      "command": "t2d",
      "args": ["mcp", "."]
    }
  }
}
```

Then in Claude Desktop:
- "I have a PRD, please transform it into diagrams and documentation"
- "Generate an architecture diagram for this system"
- "Create technical documentation with embedded diagrams"

The agents will activate proactively based on your requests and coordinate the entire pipeline automatically.