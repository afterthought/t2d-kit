# MCP Server Specification: Recipe Management

**Date**: 2025-01-17
**Feature**: Multi-Framework Diagram Pipeline
**Branch**: 001-i-want-to

## Overview

The MCP (Model Context Protocol) server provides recipe manipulation capabilities for Claude Desktop, enabling interactive recipe creation, editing, and validation. This is a Python-based MCP server that exposes tools for YAML recipe management.

### Automatic Validation

**Validation happens automatically on every read and write operation:**

1. **When reading recipes** (`read_user_recipe`, `read_processed_recipe`):
   - YAML is parsed and immediately validated with Pydantic
   - Invalid recipes return detailed validation errors
   - Valid recipes return clean, validated data

2. **When writing recipes** (`write_processed_recipe`):
   - Data is validated with Pydantic before writing to disk
   - Invalid data is rejected with field-level error messages
   - Only valid recipes are written to files

3. **No manual validation needed**:
   - Transform agent reads user recipe → automatic validation
   - Transform agent writes processed recipe → automatic validation
   - Orchestrator reads processed recipe → automatic validation

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
        has_content = values.get('content') is not None
        has_file = values.get('file_path') is not None

        if not (has_content or has_file):
            raise ValueError('PRD must have either content or file_path')
        if has_content and has_file:
            raise ValueError('PRD cannot have both content and file_path')
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
    agent: str = Field(..., description="Claude Code agent to invoke (e.g., 't2d-d2-generator')")
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

class MarpConfig(BaseModel):
    slide_files: List[str] = Field(..., min_items=1)
    theme: Optional[str] = Field(default="gaia")
    paginate: Optional[bool] = Field(default=True)
    export_pdf: Optional[bool] = Field(default=False)
    export_pptx: Optional[bool] = Field(default=False)
    export_html: Optional[bool] = Field(default=True)

class OutputConfig(BaseModel):
    assets_dir: str = Field(..., min_length=1)
    mkdocs: Optional[MkDocsConfig] = None
    marp: Optional[MarpConfig] = None

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
        self.server.add_tool(self.test_diagram_generation)
        self.server.add_tool(self.analyze_recipe)
        self.server.add_tool(self.suggest_enhancements)

    def _register_resources(self):
        """Register MCP resources for recipe discovery."""
        self.server.add_resource_list(self.list_recipe_resources)
        self.server.add_resource_read(self.read_recipe_resource)


    @Tool(
        name="read_user_recipe",
        description="Read and validate a user recipe YAML file"
    )
    async def read_user_recipe(self, file_path: str) -> ToolResult:
        """Read a recipe YAML file and validate with Pydantic."""
        try:
            path = Path(file_path)
            if not path.exists():
                return ToolResult(error=f"File not found: {file_path}")

            with open(path, 'r') as f:
                recipe_data = yaml.safe_load(f)

            # Validate with Pydantic model automatically on read
            recipe_wrapper = UserRecipeWrapper(**recipe_data)

            # Return validated data
            return ToolResult(
                content=[TextContent(
                    type="text",
                    text=json.dumps(recipe_wrapper.model_dump(), indent=2)
                )]
            )
        except ValidationError as e:
            return ToolResult(error=f"Recipe validation failed: {e}")
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

# Note: Preview functionality is handled by the orchestrator agent
    # when requested via user prompt (e.g., "process and preview")
    # The orchestrator starts preview servers with watch mode for live development

    @Tool(
        name="analyze_recipe",
        description="Analyze a recipe and provide insights about its structure and content"
    )
    async def analyze_recipe(self, file_path: str) -> ToolResult:
        """Analyze a recipe and provide insights."""
        try:
            # Read the recipe
            read_result = await self.read_user_recipe(file_path)
            if read_result.error:
                return read_result

            # Parse the validated recipe data
            import json
            recipe_data = json.loads(read_result.content[0].text)
            recipe = recipe_data['recipe']

            # Analyze the recipe
            analysis = {
                "recipe_name": recipe['name'],
                "version": recipe.get('version', '1.0.0'),
                "prd_provided": bool(recipe.get('prd', {}).get('content') or recipe.get('prd', {}).get('file_path')),
                "diagram_count": len(recipe.get('instructions', {}).get('diagrams', [])),
                "has_documentation": bool(recipe.get('instructions', {}).get('documentation')),
                "has_presentation": bool(recipe.get('instructions', {}).get('presentation')),
                "focus_areas": recipe.get('instructions', {}).get('focus_areas', []),
                "diagram_types": [],
                "framework_preferences": [],
                "insights": [],
                "opportunities": []
            }

            # Analyze diagrams
            for diagram in recipe.get('instructions', {}).get('diagrams', []):
                analysis["diagram_types"].append(diagram.get('type', 'unspecified'))
                if diagram.get('framework_preference'):
                    analysis["framework_preferences"].append(diagram['framework_preference'])

            # Generate insights
            if not analysis["has_documentation"] and not analysis["has_presentation"]:
                analysis["insights"].append("No output format specified - consider adding documentation or presentation instructions")

            if analysis["diagram_count"] == 0:
                analysis["insights"].append("No diagrams specified - add diagram requests to generate visuals")
            elif analysis["diagram_count"] > 10:
                analysis["insights"].append(f"Large number of diagrams ({analysis['diagram_count']}) - consider focusing on key visuals")

            if not analysis["prd_provided"]:
                analysis["insights"].append("No PRD content provided - add PRD content for better context-aware diagram generation")

            if not analysis["framework_preferences"]:
                analysis["insights"].append("No framework preferences specified - system will auto-select optimal frameworks")

            # Identify opportunities
            if not analysis["has_documentation"]:
                analysis["opportunities"].append("Add MkDocs documentation output for comprehensive technical docs")

            if not analysis["has_presentation"]:
                analysis["opportunities"].append("Add MarpKit presentation output for stakeholder presentations")

            # Check for missing common diagram types
            common_types = ["architecture", "sequence", "erd", "flowchart"]
            specified_types = [d.lower() for d in analysis["diagram_types"]]
            missing_common = [t for t in common_types if t not in specified_types]

            if missing_common:
                analysis["opportunities"].append(f"Consider adding these common diagram types: {', '.join(missing_common)}")

            return ToolResult(
                content=[TextContent(
                    type="text",
                    text=json.dumps(analysis, indent=2)
                )]
            )

        except Exception as e:
            return ToolResult(error=f"Error analyzing recipe: {e}")

    @Tool(
        name="suggest_enhancements",
        description="Suggest enhancements for a recipe including export formats and additional features"
    )
    async def suggest_enhancements(self, file_path: str) -> ToolResult:
        """Suggest enhancements for recipe including PDF, PowerPoint, and other options."""
        try:
            # First analyze the recipe
            analysis_result = await self.analyze_recipe(file_path)
            if analysis_result.error:
                return analysis_result

            import json
            analysis = json.loads(analysis_result.content[0].text)

            suggestions = {
                "recipe_name": analysis["recipe_name"],
                "current_state": {
                    "diagrams": analysis["diagram_count"],
                    "has_documentation": analysis["has_documentation"],
                    "has_presentation": analysis["has_presentation"]
                },
                "suggested_enhancements": [],
                "example_additions": {}
            }

            # Suggest export formats
            if analysis["has_presentation"] and not analysis.get("has_pdf_export"):
                suggestions["suggested_enhancements"].append({
                    "type": "export_format",
                    "name": "PDF Export for Presentations",
                    "description": "Export Marp presentations as PDF for easy sharing",
                    "impact": "High - Enables offline viewing and printing"
                })
                suggestions["example_additions"]["pdf_export"] = {
                    "instructions": {
                        "presentation": {
                            "marpkit": {
                                "export_pdf": True,
                                "pdf_options": {
                                    "format": "A4",
                                    "landscape": True
                                }
                            }
                        }
                    }
                }

            if analysis["has_presentation"] and not analysis.get("has_pptx_export"):
                suggestions["suggested_enhancements"].append({
                    "type": "export_format",
                    "name": "PowerPoint Export",
                    "description": "Export presentations as PPTX for editing in PowerPoint",
                    "impact": "High - Enables stakeholder customization"
                })
                suggestions["example_additions"]["pptx_export"] = {
                    "instructions": {
                        "presentation": {
                            "marpkit": {
                                "export_pptx": True
                            }
                        }
                    }
                }

            # Suggest diagram enhancements
            if analysis["diagram_count"] > 0:
                if "gantt" not in [d.lower() for d in analysis["diagram_types"]]:
                    suggestions["suggested_enhancements"].append({
                        "type": "diagram",
                        "name": "Project Timeline (Gantt Chart)",
                        "description": "Add a Gantt chart to show project phases and milestones",
                        "impact": "Medium - Provides timeline visibility"
                    })
                    suggestions["example_additions"]["gantt_diagram"] = {
                        "instructions": {
                            "diagrams": [{
                                "type": "gantt",
                                "description": "Project implementation timeline with key milestones"
                            }]
                        }
                    }

                if "erd" not in [d.lower() for d in analysis["diagram_types"]] and analysis["prd_provided"]:
                    suggestions["suggested_enhancements"].append({
                        "type": "diagram",
                        "name": "Data Model (ERD)",
                        "description": "Add an Entity Relationship Diagram for data structure",
                        "impact": "Medium - Clarifies data relationships"
                    })
                    suggestions["example_additions"]["erd_diagram"] = {
                        "instructions": {
                            "diagrams": [{
                                "type": "erd",
                                "description": "System data model showing entities and relationships"
                            }]
                        }
                    }

            # Suggest documentation enhancements
            if not analysis["has_documentation"]:
                suggestions["suggested_enhancements"].append({
                    "type": "output",
                    "name": "MkDocs Documentation Site",
                    "description": "Generate a full documentation site with navigation",
                    "impact": "High - Creates searchable, organized documentation"
                })
                suggestions["example_additions"]["mkdocs"] = {
                    "instructions": {
                        "documentation": {
                            "mkdocs": {
                                "theme": "material",
                                "nav": [
                                    {"Home": "index.md"},
                                    {"Architecture": "architecture.md"},
                                    {"API": "api.md"}
                                ]
                            }
                        }
                    }
                }

            # Suggest focus areas if not present
            if not analysis.get("focus_areas"):
                suggestions["suggested_enhancements"].append({
                    "type": "content",
                    "name": "Focus Areas",
                    "description": "Define specific areas to emphasize in documentation",
                    "impact": "Medium - Ensures key concepts are highlighted"
                })
                suggestions["example_additions"]["focus_areas"] = {
                    "instructions": {
                        "focus_areas": [
                            "Security considerations",
                            "Performance optimization",
                            "Scalability approach",
                            "Integration points"
                        ]
                    }
                }

            # Add usage examples
            suggestions["how_to_apply"] = "To apply these suggestions, update your recipe.yaml file with the relevant sections from 'example_additions'. You can copy and merge the suggested YAML structures into your existing recipe."

            return ToolResult(
                content=[TextContent(
                    type="text",
                    text=json.dumps(suggestions, indent=2)
                )]
            )

        except Exception as e:
            return ToolResult(error=f"Error generating suggestions: {e}")

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