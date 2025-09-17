# MCP Server Specification: Recipe Management

**Date**: 2025-01-17
**Feature**: Multi-Framework Diagram Pipeline
**Branch**: 001-i-want-to

## Overview

The MCP (Model Context Protocol) server provides recipe manipulation capabilities for Claude Desktop, enabling interactive recipe creation, editing, and validation. This is a Python-based MCP server that exposes tools for YAML recipe management.

## Architecture

```
Claude Desktop
    ↓
MCP Protocol (stdio)
    ↓
t2d-kit MCP Server (Python)
    ├── Recipe Tools (read, write, validate)
    ├── Diagram Tools (list types, frameworks)
    └── Generation Tools (preview, test)
```

## Python Implementation

### Pydantic Models for Validation

```python
# mcp/models.py
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any, Literal
from enum import Enum

class DiagramType(str, Enum):
    C4_CONTEXT = "c4_context"
    C4_CONTAINER = "c4_container"
    C4_COMPONENT = "c4_component"
    SEQUENCE = "sequence"
    FLOWCHART = "flowchart"
    ERD = "erd"
    GANTT = "gantt"
    STATE = "state"
    NETWORK = "network"
    ARCHITECTURE = "architecture"
    CLASS = "class"
    CUSTOM = "custom"

class FrameworkType(str, Enum):
    D2 = "d2"
    MERMAID = "mermaid"
    PLANTUML = "plantuml"
    GRAPHVIZ = "graphviz"
    AUTO = "auto"

class ContentType(str, Enum):
    DOCUMENTATION = "documentation"
    PRESENTATION = "presentation"
    MIXED = "mixed"

class ContentFile(BaseModel):
    id: str = Field(..., min_length=1, max_length=100)
    path: str = Field(..., min_length=1)
    type: ContentType
    agent: str = Field(..., description="Claude Code agent responsible for this content")

# User Recipe Models (recipe.yaml)
class PRDContent(BaseModel):
    content: Optional[str] = Field(None, max_length=1000000)  # 1MB limit
    file_path: Optional[str] = None
    format: Literal["markdown", "text", "html"] = Field(default="markdown")
    sections: Optional[List[str]] = None

    @field_validator('content', 'file_path')
    def validate_prd_source(cls, v, values):
        if not v and not values.get('file_path') and not values.get('content'):
            raise ValueError('PRD must have either content or file_path')
        return v

class DiagramRequest(BaseModel):
    type: str = Field(..., min_length=1, description="User's diagram type description")
    description: Optional[str] = Field(None, max_length=500)
    framework_preference: Optional[str] = None

class UserInstructions(BaseModel):
    diagrams: List[DiagramRequest] = Field(..., min_items=1)
    documentation: Optional[Dict[str, Any]] = None
    presentation: Optional[Dict[str, Any]] = None
    focus_areas: Optional[List[str]] = None
    exclude: Optional[List[str]] = None

class UserRecipe(BaseModel):
    """User-maintained recipe with PRD and instructions"""
    name: str = Field(..., min_length=1, max_length=255)
    version: str = Field(default="1.0.0")
    prd: PRDContent
    instructions: UserInstructions
    preferences: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

# Processed Recipe Models (recipe.t2d.yaml)
class DiagramSpecification(BaseModel):
    """Agent-generated detailed diagram specification"""
    id: str = Field(..., min_length=1, max_length=100)
    type: DiagramType
    framework: Optional[FrameworkType] = Field(default=FrameworkType.AUTO)
    title: str = Field(..., min_length=1, max_length=255)
    instructions: str = Field(..., min_length=1, max_length=50000)

    @field_validator('id')
    def validate_id(cls, v):
        # Ensure ID is valid for filenames
        if not v.replace('-', '').replace('_', '').isalnum():
            raise ValueError('ID must contain only alphanumeric characters, hyphens, and underscores')
        return v

class MkDocsConfig(BaseModel):
    config_file: str = Field(default="mkdocs.yml")
    content_refs: List[str] = Field(..., min_items=1)
    nav_structure: Optional[List[Dict[str, str]]] = None
    theme: Optional[str] = Field(default="material")

class MarpKitConfig(BaseModel):
    slide_files: List[str] = Field(..., min_items=1)
    theme: Optional[str] = Field(default="gaia")
    paginate: Optional[bool] = Field(default=True)
    export_pdf: Optional[bool] = Field(default=False)
    export_pptx: Optional[bool] = Field(default=False)

class OutputConfig(BaseModel):
    assets_dir: str = Field(..., min_length=1)
    mkdocs: Optional[MkDocsConfig] = None
    marpkit: Optional[MarpKitConfig] = None

class ProcessedRecipe(BaseModel):
    """Agent-generated recipe with detailed specifications"""
    name: str = Field(..., min_length=1, max_length=255)
    version: str = Field(default="1.0.0")
    source_recipe: str = Field(..., description="Path to original recipe.yaml")
    generated_at: str = Field(..., description="ISO 8601 timestamp")
    content_files: Optional[List[ContentFile]] = None
    diagram_specs: List[DiagramSpecification] = Field(..., min_items=1)
    outputs: OutputConfig
    generation_notes: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None

    @field_validator('diagram_specs')
    def validate_unique_ids(cls, v):
        ids = [spec.id for spec in v]
        if len(ids) != len(set(ids)):
            raise ValueError('Diagram IDs must be unique within a recipe')
        return v

class UserRecipeWrapper(BaseModel):
    """Top-level wrapper for user recipe YAML"""
    recipe: UserRecipe

class ProcessedRecipeWrapper(BaseModel):
    """Top-level wrapper for processed recipe YAML"""
    recipe: ProcessedRecipe
```

### Server Structure with Pydantic Validation

```python
# mcp/server.py
import asyncio
import json
import yaml
from pathlib import Path
from typing import Any, Dict, List, Optional
from pydantic import ValidationError
from mcp.server import Server, Tool
from mcp.types import TextContent, ImageContent, ToolResult
from .models import Recipe, RecipeWrapper, DiagramSpecification, DiagramType, FrameworkType

class T2DKitMCPServer:
    """MCP server for t2d-kit recipe management."""

    def __init__(self):
        self.server = Server("t2d-kit")
        self.recipe_dir = Path.home() / ".t2d-kit" / "recipes"
        self.recipe_dir.mkdir(parents=True, exist_ok=True)
        self._register_tools()
        self._register_resources()

    def _register_tools(self):
        """Register all available MCP tools."""
        self.server.add_tool(self.read_user_recipe)
        self.server.add_tool(self.read_processed_recipe)
        self.server.add_tool(self.write_user_recipe)
        self.server.add_tool(self.write_processed_recipe)
        self.server.add_tool(self.validate_user_recipe)
        self.server.add_tool(self.validate_processed_recipe)
        self.server.add_tool(self.list_diagram_types)
        self.server.add_tool(self.list_frameworks)
        self.server.add_tool(self.suggest_framework)
        self.server.add_tool(self.preview_diagram)
        self.server.add_tool(self.test_diagram_generation)

    def _register_resources(self):
        """Register MCP resources for recipe discovery."""
        self.server.add_resource_list(self.list_recipe_resources)
        self.server.add_resource_read(self.read_recipe_resource)


    @Tool(
        name="read_user_recipe",
        description="Read and parse a user recipe YAML file"
    )
    async def read_user_recipe(self, file_path: str) -> ToolResult:
        """Read a recipe YAML file and return its contents."""
        try:
            path = Path(file_path)
            if not path.exists():
                return ToolResult(error=f"File not found: {file_path}")

            with open(path, 'r') as f:
                recipe_data = yaml.safe_load(f)

            return ToolResult(
                content=[TextContent(
                    type="text",
                    text=json.dumps(recipe_data, indent=2)
                )]
            )
        except yaml.YAMLError as e:
            return ToolResult(error=f"Invalid YAML: {e}")
        except Exception as e:
            return ToolResult(error=f"Error reading file: {e}")

    @Tool(
        name="write_recipe",
        description="Write or update a YAML recipe file"
    )
    async def write_recipe(
        self,
        file_path: str,
        recipe_content: Dict[str, Any]
    ) -> ToolResult:
        """Write recipe data to a YAML file with validation."""
        try:
            # Validate recipe structure using Pydantic
            recipe_wrapper = RecipeWrapper(**recipe_content)

            path = Path(file_path)
            path.parent.mkdir(parents=True, exist_ok=True)

            # Convert Pydantic model back to dict for YAML serialization
            recipe_dict = recipe_wrapper.model_dump(exclude_none=True)

            with open(path, 'w') as f:
                yaml.dump(
                    recipe_dict,
                    f,
                    default_flow_style=False,
                    sort_keys=False
                )

            return ToolResult(
                content=[TextContent(
                    type="text",
                    text=f"Recipe '{recipe_wrapper.recipe.name}' written to {file_path}"
                )]
            )
        except ValidationError as e:
            errors = []
            for error in e.errors():
                field_path = ' -> '.join(str(x) for x in error['loc'])
                errors.append(f"{field_path}: {error['msg']}")
            return ToolResult(error=f"Recipe validation failed:\n" + "\n".join(errors))
        except Exception as e:
            return ToolResult(error=f"Error writing file: {e}")

    @Tool(
        name="validate_recipe",
        description="Validate a recipe structure and report issues"
    )
    async def validate_recipe(
        self,
        recipe_content: Dict[str, Any]
    ) -> ToolResult:
        """Validate recipe structure using Pydantic models."""
        errors = []
        warnings = []

        try:
            # Validate using Pydantic
            recipe_wrapper = RecipeWrapper(**recipe_content)
            recipe = recipe_wrapper.recipe

            # Additional business logic validations
            # Check for warnings (non-critical issues)
            if not recipe.content_files:
                warnings.append("No content files defined - documentation will be minimal")

            if not recipe.outputs.mkdocs and not recipe.outputs.marpkit:
                warnings.append("No output configuration for MkDocs or MarpKit")

            # Check for framework availability
            for spec in recipe.diagram_specs:
                if spec.framework == FrameworkType.AUTO:
                    suggested = self._suggest_framework(spec.type)
                    warnings.append(f"Diagram '{spec.id}' will auto-route to {suggested}")

            # Recipe is valid if Pydantic validation passes
            return ToolResult(
                content=[TextContent(
                    type="text",
                    text=json.dumps({
                        "valid": True,
                        "recipe_name": recipe.name,
                        "diagram_count": len(recipe.diagram_specs),
                        "errors": errors,
                        "warnings": warnings,
                        "summary": {
                            "content_files": len(recipe.content_files or []),
                            "diagrams": len(recipe.diagram_specs),
                            "has_mkdocs": recipe.outputs.mkdocs is not None,
                            "has_marpkit": recipe.outputs.marpkit is not None
                        }
                    }, indent=2)
                )]
            )

        except ValidationError as e:
            # Convert Pydantic validation errors to our format
            for error in e.errors():
                field_path = ' -> '.join(str(x) for x in error['loc'])
                errors.append(f"{field_path}: {error['msg']}")

            return ToolResult(
                content=[TextContent(
                    type="text",
                    text=json.dumps({
                        "valid": False,
                        "errors": errors,
                        "warnings": warnings
                    }, indent=2)
                )]
            )

    def _suggest_framework(self, diagram_type: DiagramType) -> str:
        """Internal helper to suggest framework for diagram type."""
        suggestions = {
            DiagramType.C4_CONTEXT: "d2",
            DiagramType.C4_CONTAINER: "d2",
            DiagramType.C4_COMPONENT: "d2",
            DiagramType.SEQUENCE: "mermaid",
            DiagramType.FLOWCHART: "mermaid",
            DiagramType.ERD: "mermaid",
            DiagramType.GANTT: "mermaid",
            DiagramType.STATE: "mermaid",
            DiagramType.NETWORK: "d2",
            DiagramType.ARCHITECTURE: "d2",
            DiagramType.CLASS: "plantuml"
        }
        return suggestions.get(diagram_type, "mermaid")

    @Tool(
        name="list_diagram_types",
        description="List all supported diagram types"
    )
    async def list_diagram_types(self) -> ToolResult:
        """Return list of supported diagram types with descriptions."""
        diagram_types = {
            "c4_context": "C4 Context diagram for system boundaries",
            "c4_container": "C4 Container diagram for applications/services",
            "c4_component": "C4 Component diagram for code structure",
            "sequence": "Sequence diagram for interaction flows",
            "flowchart": "Flowchart for process flows",
            "erd": "Entity Relationship Diagram for data models",
            "gantt": "Gantt chart for project timelines",
            "state": "State machine diagram",
            "network": "Network topology diagram",
            "architecture": "General architecture diagram",
            "class": "UML class diagram",
            "custom": "Custom diagram with explicit framework"
        }

        return ToolResult(
            content=[TextContent(
                type="text",
                text=json.dumps(diagram_types, indent=2)
            )]
        )

    @Tool(
        name="list_frameworks",
        description="List available diagram frameworks"
    )
    async def list_frameworks(self) -> ToolResult:
        """Return list of available diagram frameworks."""
        frameworks = {
            "d2": {
                "name": "D2",
                "best_for": ["c4_context", "c4_container", "architecture", "network"],
                "requires": "d2 CLI tool"
            },
            "mermaid": {
                "name": "Mermaid",
                "best_for": ["sequence", "flowchart", "erd", "gantt", "state"],
                "requires": "@mermaid-js/mermaid-cli npm package"
            },
            "plantuml": {
                "name": "PlantUML",
                "best_for": ["class", "sequence", "state"],
                "requires": "Java and PlantUML jar"
            }
        }

        return ToolResult(
            content=[TextContent(
                type="text",
                text=json.dumps(frameworks, indent=2)
            )]
        )

    @Tool(
        name="suggest_framework",
        description="Suggest the best framework for a diagram type"
    )
    async def suggest_framework(self, diagram_type: str) -> ToolResult:
        """Suggest optimal framework for given diagram type."""
        try:
            # Validate diagram type using enum
            dt = DiagramType(diagram_type)
            framework = self._suggest_framework(dt)

            # Get framework capabilities
            capabilities = {
                "d2": ["architecture", "c4 diagrams", "network topology", "technical diagrams"],
                "mermaid": ["flowcharts", "sequences", "ERD", "gantt", "state machines"],
                "plantuml": ["UML diagrams", "class diagrams", "detailed specifications"]
            }

            return ToolResult(
                content=[TextContent(
                    type="text",
                    text=json.dumps({
                        "diagram_type": diagram_type,
                        "suggested_framework": framework,
                        "reason": f"Best for {', '.join(capabilities.get(framework, ['general diagrams']))}",
                        "alternatives": [f for f in ["d2", "mermaid", "plantuml"] if f != framework]
                    }, indent=2)
                )]
            )
        except ValueError:
            return ToolResult(
                content=[TextContent(
                    type="text",
                    text=json.dumps({
                        "error": f"Unknown diagram type: {diagram_type}",
                        "valid_types": [dt.value for dt in DiagramType]
                    }, indent=2)
                )]
            )

    @Tool(
        name="preview_diagram",
        description="Generate a visual preview of diagram with live rendering"
    )
    async def preview_diagram(
        self,
        diagram_type: str,
        framework: str,
        instructions: str,
        render: bool = True
    ) -> ToolResult:
        """Generate preview of a diagram, optionally with visual rendering."""
        import tempfile
        import subprocess
        import base64
        from pathlib import Path

        # Generate diagram source code
        if framework == "mermaid":
            if diagram_type == "sequence":
                source = f"""sequenceDiagram
    participant User
    participant System
    {instructions}"""
            elif diagram_type == "erd":
                source = f"""erDiagram
    {instructions}"""
            elif diagram_type == "flowchart":
                source = f"""flowchart TD
    Start --> Process
    {instructions}"""
            else:
                source = f"""graph TD
    {instructions}"""
        elif framework == "d2":
            source = f"""# {diagram_type.upper()} Diagram
{instructions}"""
        else:
            source = instructions

        if not render:
            # Return just the source code
            return ToolResult(
                content=[TextContent(
                    type="text",
                    text=source
                )]
            )

        # Render the diagram to an image
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                tmppath = Path(tmpdir)

                if framework == "mermaid":
                    # Use mermaid CLI to generate SVG
                    input_file = tmppath / "diagram.mmd"
                    output_file = tmppath / "diagram.svg"
                    input_file.write_text(source)

                    result = subprocess.run(
                        ["mmdc", "-i", str(input_file), "-o", str(output_file), "-t", "default"],
                        capture_output=True,
                        text=True
                    )

                    if result.returncode != 0:
                        return ToolResult(error=f"Mermaid rendering failed: {result.stderr}")

                    # Read the SVG and return as HTML for inline display
                    svg_content = output_file.read_text()

                    # Return both the source and rendered HTML
                    return ToolResult(
                        content=[
                            TextContent(
                                type="text",
                                text=f"Source:\n```{framework}\n{source}\n```"
                            ),
                            TextContent(
                                type="text",
                                text=f"<html><body>{svg_content}</body></html>",
                                mime_type="text/html"
                            )
                        ]
                    )

                elif framework == "d2":
                    # Use D2 CLI to generate SVG
                    input_file = tmppath / "diagram.d2"
                    output_file = tmppath / "diagram.svg"
                    input_file.write_text(source)

                    result = subprocess.run(
                        ["d2", str(input_file), str(output_file)],
                        capture_output=True,
                        text=True
                    )

                    if result.returncode != 0:
                        return ToolResult(error=f"D2 rendering failed: {result.stderr}")

                    # Read SVG and encode as base64 for image display
                    svg_content = output_file.read_text()

                    # For D2, we can also generate PNG for better compatibility
                    png_file = tmppath / "diagram.png"
                    subprocess.run(
                        ["d2", str(input_file), str(png_file), "--format", "png"],
                        capture_output=True
                    )

                    if png_file.exists():
                        # Return PNG as base64-encoded image
                        png_data = png_file.read_bytes()
                        png_base64 = base64.b64encode(png_data).decode('utf-8')

                        return ToolResult(
                            content=[
                                TextContent(
                                    type="text",
                                    text=f"Source:\n```d2\n{source}\n```"
                                ),
                                ImageContent(
                                    type="image",
                                    data=png_base64,
                                    mime_type="image/png"
                                )
                            ]
                        )
                    else:
                        # Fallback to SVG as HTML
                        return ToolResult(
                            content=[
                                TextContent(
                                    type="text",
                                    text=f"Source:\n```d2\n{source}\n```"
                                ),
                                TextContent(
                                    type="text",
                                    text=f"<html><body>{svg_content}</body></html>",
                                    mime_type="text/html"
                                )
                            ]
                        )

        except Exception as e:
            return ToolResult(error=f"Error rendering preview: {e}")

    @Tool(
        name="test_diagram_generation",
        description="Test if diagram generation would work"
    )
    async def test_diagram_generation(
        self,
        diagram_spec: Dict[str, Any]
    ) -> ToolResult:
        """Test diagram generation without actually creating files."""
        try:
            # Validate diagram spec using Pydantic
            spec = DiagramSpecification(**diagram_spec)

            # Determine framework
            if spec.framework == FrameworkType.AUTO:
                framework = self._suggest_framework(spec.type)
            else:
                framework = spec.framework.value

            diagram_type = spec.type.value

            # Check tool availability
            checks = []
            import subprocess

            if framework == 'd2':
                # Check for d2 CLI
                try:
                    result = subprocess.run(['d2', '--version'], capture_output=True, text=True)
                    checks.append({
                        "tool": "d2",
                        "available": result.returncode == 0,
                        "version": result.stdout.strip() if result.returncode == 0 else None
                    })
                except FileNotFoundError:
                    checks.append({"tool": "d2", "available": False, "error": "d2 not found - run 'mise install'"})

            elif framework == 'mermaid':
                # Check for mmdc CLI
                try:
                    result = subprocess.run(['mmdc', '--version'], capture_output=True, text=True)
                    checks.append({
                        "tool": "mmdc",
                        "available": result.returncode == 0,
                        "version": result.stdout.strip() if result.returncode == 0 else None
                    })
                except FileNotFoundError:
                    checks.append({"tool": "mmdc", "available": False, "error": "mmdc not found - run 'mise install'"})

            elif framework == 'plantuml':
                # Check for Java and PlantUML jar
                try:
                    java_result = subprocess.run(['java', '-version'], capture_output=True, text=True)
                    java_available = java_result.returncode == 0
                    checks.append({
                        "tool": "java",
                        "available": java_available,
                        "version": java_result.stderr.split('\n')[0] if java_available else None
                    })

                    # Check for PlantUML jar
                    plantuml_path = Path.home() / ".local/share/plantuml/plantuml.jar"
                    checks.append({
                        "tool": "plantuml.jar",
                        "available": plantuml_path.exists(),
                        "path": str(plantuml_path) if plantuml_path.exists() else None,
                        "error": None if plantuml_path.exists() else "run 'mise run setup-plantuml'"
                    })
                except FileNotFoundError:
                    checks.append({"tool": "java", "available": False, "error": "Java not found - run 'mise install'"})

            return ToolResult(
                content=[TextContent(
                    type="text",
                    text=json.dumps({
                        "diagram_id": spec.id,
                        "diagram_type": diagram_type,
                        "framework": framework,
                        "tool_checks": checks,
                        "ready": all(c.get('available', False) for c in checks),
                        "validation": "passed"
                    }, indent=2)
                )]
            )

        except ValidationError as e:
            errors = []
            for error in e.errors():
                field_path = ' -> '.join(str(x) for x in error['loc'])
                errors.append(f"{field_path}: {error['msg']}")

            return ToolResult(
                content=[TextContent(
                    type="text",
                    text=json.dumps({
                        "validation": "failed",
                        "errors": errors
                    }, indent=2)
                )]
            )

    # MCP Resources Implementation
    async def list_recipe_resources(self) -> List[Dict[str, Any]]:
        """List available recipes as MCP resources."""
        resources = []

        # List user recipes (*.yaml)
        for recipe_file in self.recipe_dir.glob("*.yaml"):
            if not recipe_file.name.endswith('.t2d.yaml'):
                try:
                    with open(recipe_file, 'r') as f:
                        data = yaml.safe_load(f)
                        recipe_name = data.get('recipe', {}).get('name', recipe_file.stem)

                    resources.append({
                        "uri": f"recipe://user/{recipe_file.name}",
                        "name": recipe_name,
                        "mimeType": "application/x-yaml",
                        "description": f"User recipe: {recipe_name}",
                        "metadata": {
                            "type": "user_recipe",
                            "path": str(recipe_file),
                            "modified": recipe_file.stat().st_mtime
                        }
                    })
                except Exception as e:
                    # Skip invalid files
                    continue

        # List processed recipes (*.t2d.yaml)
        for recipe_file in self.recipe_dir.glob("*.t2d.yaml"):
            try:
                with open(recipe_file, 'r') as f:
                    data = yaml.safe_load(f)
                    recipe_name = data.get('recipe', {}).get('name', recipe_file.stem)
                    source = data.get('recipe', {}).get('source_recipe', '')

                resources.append({
                    "uri": f"recipe://processed/{recipe_file.name}",
                    "name": f"{recipe_name} (Processed)",
                    "mimeType": "application/x-yaml",
                    "description": f"Processed recipe from {source}",
                    "metadata": {
                        "type": "processed_recipe",
                        "path": str(recipe_file),
                        "source_recipe": source,
                        "generated_at": data.get('recipe', {}).get('generated_at', ''),
                        "modified": recipe_file.stat().st_mtime
                    }
                })
            except Exception as e:
                continue

        # Also list example recipes from package
        examples_dir = Path(__file__).parent.parent / "examples"
        if examples_dir.exists():
            for example_file in examples_dir.glob("*.yaml"):
                resources.append({
                    "uri": f"recipe://example/{example_file.name}",
                    "name": f"Example: {example_file.stem}",
                    "mimeType": "application/x-yaml",
                    "description": f"Example recipe: {example_file.name}",
                    "metadata": {
                        "type": "example",
                        "path": str(example_file),
                        "readonly": True
                    }
                })

        return resources

    async def read_recipe_resource(self, uri: str) -> Dict[str, Any]:
        """Read a recipe resource by URI."""
        # Parse URI: recipe://type/filename
        parts = uri.replace("recipe://", "").split("/", 1)
        if len(parts) != 2:
            raise ValueError(f"Invalid recipe URI: {uri}")

        recipe_type, filename = parts

        if recipe_type == "user" or recipe_type == "processed":
            file_path = self.recipe_dir / filename
        elif recipe_type == "example":
            file_path = Path(__file__).parent.parent / "examples" / filename
        else:
            raise ValueError(f"Unknown recipe type: {recipe_type}")

        if not file_path.exists():
            raise FileNotFoundError(f"Recipe not found: {file_path}")

        # Read and return the recipe
        with open(file_path, 'r') as f:
            content = f.read()

        return {
            "uri": uri,
            "mimeType": "application/x-yaml",
            "text": content,
            "metadata": {
                "path": str(file_path),
                "size": len(content),
                "lines": content.count('\n') + 1
            }
        }

    async def run(self):
        """Run the MCP server."""
        await self.server.run()


# Entry point for MCP server
async def main():
    server = T2DKitMCPServer()
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())
```

### MCP Server Configuration

```json
{
  "name": "t2d-kit",
  "version": "1.0.0",
  "description": "Recipe management for t2d-kit diagram pipeline",
  "tools": [
    {
      "name": "read_recipe",
      "description": "Read and parse a YAML recipe file",
      "parameters": {
        "type": "object",
        "properties": {
          "file_path": {
            "type": "string",
            "description": "Path to the recipe YAML file"
          }
        },
        "required": ["file_path"]
      }
    },
    {
      "name": "write_recipe",
      "description": "Write or update a YAML recipe file",
      "parameters": {
        "type": "object",
        "properties": {
          "file_path": {
            "type": "string",
            "description": "Path where recipe should be saved"
          },
          "recipe_content": {
            "type": "object",
            "description": "Recipe data structure"
          }
        },
        "required": ["file_path", "recipe_content"]
      }
    },
    {
      "name": "validate_recipe",
      "description": "Validate recipe structure and report issues",
      "parameters": {
        "type": "object",
        "properties": {
          "recipe_content": {
            "type": "object",
            "description": "Recipe data to validate"
          }
        },
        "required": ["recipe_content"]
      }
    },
    {
      "name": "list_diagram_types",
      "description": "List all supported diagram types"
    },
    {
      "name": "list_frameworks",
      "description": "List available diagram frameworks"
    },
    {
      "name": "suggest_framework",
      "description": "Suggest the best framework for a diagram type",
      "parameters": {
        "type": "object",
        "properties": {
          "diagram_type": {
            "type": "string",
            "description": "Type of diagram"
          }
        },
        "required": ["diagram_type"]
      }
    },
    {
      "name": "preview_diagram",
      "description": "Generate preview of diagram instructions",
      "parameters": {
        "type": "object",
        "properties": {
          "diagram_type": {
            "type": "string"
          },
          "framework": {
            "type": "string"
          },
          "instructions": {
            "type": "string"
          }
        },
        "required": ["diagram_type", "framework", "instructions"]
      }
    },
    {
      "name": "test_diagram_generation",
      "description": "Test if diagram generation would work",
      "parameters": {
        "type": "object",
        "properties": {
          "diagram_spec": {
            "type": "object",
            "description": "Diagram specification to test"
          }
        },
        "required": ["diagram_spec"]
      }
    }
  ]
}
```

## Integration with CLI

The minimal Python CLI wrapper invokes the MCP server when needed:

```python
# cli/main.py
import click
import subprocess
import os
from pathlib import Path

@click.group()
def cli():
    """t2d-kit: Multi-framework diagram pipeline."""
    ensure_dependencies()

@cli.command()
def mcp_install():
    """Install MCP server for Claude Desktop integration."""
    # Install MCP dependencies
    subprocess.run(["pip", "install", "mcp"], check=True)

    # Register with Claude Desktop
    config_path = Path.home() / ".config" / "claude" / "mcp-servers.json"
    # ... add t2d-kit server configuration ...

    click.echo("MCP server installed. Restart Claude Desktop to activate.")

@cli.command()
def mcp_serve():
    """Run MCP server (called by Claude Desktop)."""
    from mcp.server import run_server
    run_server("t2d_kit.mcp.server:T2DKitMCPServer")
```

## Rich Content Rendering

The MCP server supports returning rich content that Claude Desktop can render:

### Image Content
The `preview_diagram` tool returns base64-encoded PNG images that Claude Desktop displays inline:

```python
ImageContent(
    type="image",
    data=png_base64,  # Base64-encoded PNG data
    mime_type="image/png"
)
```

### HTML Content
For SVG diagrams, the tool returns HTML content that Claude Desktop renders:

```python
TextContent(
    type="text",
    text=f"<html><body>{svg_content}</body></html>",
    mime_type="text/html"
)
```

### Content Types Supported
According to MCP specification, tools can return:
- **Text Content**: Plain text or code
- **Image Content**: Base64-encoded images (PNG, JPEG, etc.)
- **HTML Content**: Rendered as rich content when mime_type is "text/html"
- **Structured Content**: JSON objects for programmatic use

## Usage in Claude Desktop

Once configured, Claude can use these tools with visual feedback:

```
User: "Create a recipe for my system architecture"

Claude: I'll help you create a recipe. Let me start by showing you available diagram types.

[Uses list_diagram_types tool]

Now let's create a C4 context diagram. Let me show you a preview:

[Uses preview_diagram tool - displays rendered diagram inline]

[Visual diagram appears in Claude Desktop]

The diagram looks good! Let me save this to your recipe file.

[Uses write_recipe tool to create recipe.yml]

[Uses validate_recipe tool]

✓ Recipe is valid and saved to recipe.yml
You can now process it using: `t2d create recipe.yml`
```

## Benefits

1. **Interactive Development**: Create and edit recipes in Claude Desktop
2. **Validation**: Real-time feedback on recipe structure
3. **Preview**: See diagram code before generation
4. **Tool Checking**: Verify dependencies are available
5. **Framework Suggestions**: Get optimal framework recommendations

## Dependencies

```toml
# pyproject.toml additions
[project.optional-dependencies]
mcp = [
    "mcp>=0.1.0",
    "pyyaml>=6.0",
]

[project.scripts]
t2d-mcp = "t2d_kit.mcp.server:main"
```

---
*MCP server specification defined: 2025-01-17*