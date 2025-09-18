# Enhanced Data Model: Multi-Framework Diagram Pipeline

**Date**: 2025-01-16
**Feature**: Enhanced Pydantic Models with Validation
**Branch**: 001-i-want-to

## Base Model Configuration

### T2DBaseModel with ConfigDict

```python
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from typing import Annotated, Optional, List, Dict, Any, Literal
from datetime import datetime
from enum import Enum
import re
import json
from pathlib import Path

class T2DBaseModel(BaseModel):
    """Base model for all T2D-Kit entities with enhanced validation."""

    model_config = ConfigDict(
        extra='forbid',              # No unexpected fields
        validate_assignment=True,    # Validate on assignment
        str_strip_whitespace=True,   # Auto-strip strings
        frozen=False,               # Allow mutations (most models need this)
        use_enum_values=True,       # Use enum values in JSON
        json_schema_extra={         # Add schema metadata
            "title": "T2D-Kit Models",
            "version": "1.0.0",
            "description": "Enhanced Pydantic models for T2D-Kit diagram pipeline"
        }
    )
```

## Common Type Annotations

```python
# Field type definitions for consistent validation
IdField = Annotated[str, Field(
    pattern=r'^[a-zA-Z0-9_-]+$',
    min_length=1,
    max_length=100,
    description="Alphanumeric identifier with hyphens and underscores"
)]

PathField = Annotated[str, Field(
    min_length=1,
    max_length=500,
    description="File system path"
)]

InstructionsField = Annotated[str, Field(
    min_length=10,
    max_length=10000,
    description="Detailed instructions for generation"
)]

NameField = Annotated[str, Field(
    min_length=1,
    max_length=255,
    description="Human-readable name"
)]

DescriptionField = Annotated[str, Field(
    max_length=500,
    description="Brief description"
)]

ContentField = Annotated[str, Field(
    max_length=1048576,  # 1MB
    description="Content text (max 1MB)"
)]

VersionField = Annotated[str, Field(
    pattern=r'^\d+\.\d+\.\d+$',
    description="Semantic version (e.g., 1.0.0)"
)]

EmailField = Annotated[str, Field(
    pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
    description="Valid email address"
)]

UrlField = Annotated[str, Field(
    pattern=r'^https?://[^\s]+$',
    description="Valid HTTP/HTTPS URL"
)]

PositiveIntField = Annotated[int, Field(
    gt=0,
    description="Positive integer"
)]

NonNegativeIntField = Annotated[int, Field(
    ge=0,
    description="Non-negative integer"
)]

ScoreField = Annotated[float, Field(
    ge=0.0,
    le=1.0,
    description="Score between 0.0 and 1.0"
)]
```

## Enhanced Model Definitions

### UserRecipe with Validation

```python
class UserRecipe(T2DBaseModel):
    """User-maintained recipe with PRD content and high-level instructions."""

    name: NameField
    version: VersionField = "1.0.0"
    prd: 'PRDContent'
    instructions: 'UserInstructions'
    preferences: Optional['Preferences'] = None
    metadata: Optional[Dict[str, Any]] = None

    @field_validator('name')
    @classmethod
    def validate_name_format(cls, v: str) -> str:
        """Ensure name follows project naming conventions."""
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9_-]*$', v):
            raise ValueError('Name must start with letter and contain only alphanumeric, hyphens, underscores')
        return v

    @model_validator(mode='after')
    def validate_recipe_completeness(self) -> 'UserRecipe':
        """Ensure recipe has minimum required content."""
        if not self.instructions.diagrams:
            raise ValueError('Recipe must specify at least one diagram type')
        return self

class PRDContent(T2DBaseModel):
    """Product Requirements Document content or reference."""

    content: Optional[ContentField] = None
    file_path: Optional[PathField] = None
    format: Optional['PRDFormat'] = PRDFormat.MARKDOWN
    sections: Optional[List[str]] = None

    @field_validator('sections')
    @classmethod
    def validate_sections_format(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        """Validate section names."""
        if v is None:
            return v
        for section in v:
            if len(section.strip()) == 0:
                raise ValueError('Section names cannot be empty')
        return [s.strip() for s in v]

    @field_validator('file_path')
    @classmethod
    def validate_file_path_exists(cls, v: Optional[str]) -> Optional[str]:
        """Validate file path format and basic structure."""
        if v is None:
            return v
        if '..' in v:
            raise ValueError('Path traversal not allowed')
        path = Path(v)
        if not path.suffix:
            raise ValueError('File path must have an extension')
        return v

    @model_validator(mode='after')
    def validate_content_source(self) -> 'PRDContent':
        """Ensure exactly one content source is provided."""
        has_content = self.content is not None
        has_file = self.file_path is not None

        if not has_content and not has_file:
            raise ValueError('Must provide either content or file_path')
        if has_content and has_file:
            raise ValueError('Cannot provide both content and file_path')
        return self

class UserInstructions(T2DBaseModel):
    """High-level instructions for what to generate."""

    diagrams: List['DiagramRequest'] = Field(min_length=1)
    documentation: Optional['DocumentationInstructions'] = None
    presentation: Optional['PresentationInstructions'] = None
    focus_areas: Optional[List[str]] = None
    exclude: Optional[List[str]] = None

    @field_validator('diagrams')
    @classmethod
    def validate_diagram_uniqueness(cls, v: List['DiagramRequest']) -> List['DiagramRequest']:
        """Ensure diagram types are not duplicated."""
        seen_types = set()
        for diagram in v:
            key = f"{diagram.type}_{diagram.description or ''}"
            if key in seen_types:
                raise ValueError(f'Duplicate diagram request: {diagram.type}')
            seen_types.add(key)
        return v

class DiagramRequest(T2DBaseModel):
    """User's high-level diagram request."""

    type: str = Field(min_length=1, max_length=100)
    description: Optional[DescriptionField] = None
    framework_preference: Optional[str] = None

    @field_validator('type')
    @classmethod
    def validate_type_format(cls, v: str) -> str:
        """Normalize diagram type format."""
        normalized = v.lower().replace(' ', '_')
        if not re.match(r'^[a-z][a-z0-9_]*$', normalized):
            raise ValueError('Diagram type must be alphanumeric with underscores')
        return normalized

    @field_validator('framework_preference')
    @classmethod
    def validate_framework_preference(cls, v: Optional[str]) -> Optional[str]:
        """Validate framework preference against known frameworks."""
        if v is None:
            return v
        valid_frameworks = {'d2', 'mermaid', 'plantuml', 'graphviz', 'auto'}
        if v.lower() not in valid_frameworks:
            raise ValueError(f'Framework must be one of: {valid_frameworks}')
        return v.lower()
```

### ProcessedRecipe with Cross-Field Validation

```python
class ProcessedRecipe(T2DBaseModel):
    """Agent-generated recipe with detailed specifications."""

    name: NameField
    version: VersionField
    source_recipe: PathField
    generated_at: datetime
    content_files: List['ContentFile'] = Field(min_length=1)
    diagram_specs: List['DiagramSpecification'] = Field(min_length=1)
    diagram_refs: List['DiagramReference'] = Field(min_length=1)
    outputs: 'OutputConfig'
    generation_notes: Optional[List[str]] = None

    @field_validator('generated_at')
    @classmethod
    def validate_generation_time(cls, v: datetime) -> datetime:
        """Ensure generation time is not in the future."""
        if v > datetime.now():
            raise ValueError('Generation time cannot be in the future')
        return v

    @model_validator(mode='after')
    def validate_diagram_consistency(self) -> 'ProcessedRecipe':
        """Ensure diagram specs and refs are consistent."""
        spec_ids = {spec.id for spec in self.diagram_specs}
        ref_ids = {ref.id for ref in self.diagram_refs}

        if spec_ids != ref_ids:
            missing_refs = spec_ids - ref_ids
            extra_refs = ref_ids - spec_ids
            errors = []
            if missing_refs:
                errors.append(f"Missing diagram references: {missing_refs}")
            if extra_refs:
                errors.append(f"Extra diagram references: {extra_refs}")
            raise ValueError("; ".join(errors))

        return self

    @model_validator(mode='after')
    def validate_content_diagram_refs(self) -> 'ProcessedRecipe':
        """Ensure content files reference valid diagrams."""
        valid_diagram_ids = {spec.id for spec in self.diagram_specs}

        for content_file in self.content_files:
            invalid_refs = set(content_file.diagram_refs) - valid_diagram_ids
            if invalid_refs:
                raise ValueError(
                    f"Content file '{content_file.path}' references invalid diagrams: {invalid_refs}"
                )

        return self

class DiagramSpecification(T2DBaseModel):
    """Individual diagram definition with generator agent prompt."""

    id: IdField
    type: 'DiagramType'
    framework: Optional['FrameworkType'] = None
    agent: str = Field(pattern=r'^t2d-[a-z0-9-]+$')
    title: NameField
    instructions: InstructionsField
    output_file: PathField
    output_formats: List['OutputFormat'] = Field(min_length=1)
    options: Optional[Union[MermaidConfig, D2Options, MarpConfig, Dict[str, Any]]] = None

    @field_validator('instructions')
    @classmethod
    def validate_instructions_length(cls, v: str) -> str:
        """Ensure instructions are detailed enough."""
        if len(v.split()) < 5:
            raise ValueError('Instructions must be at least 5 words')
        return v

    @field_validator('output_file')
    @classmethod
    def validate_output_file_extension(cls, v: str) -> str:
        """Ensure output file has appropriate extension."""
        path = Path(v)
        valid_extensions = {'.d2', '.mmd', '.puml', '.gv'}
        if path.suffix not in valid_extensions:
            raise ValueError(f'Output file must have extension: {valid_extensions}')
        return v

    @model_validator(mode='after')
    def validate_framework_compatibility(self) -> 'DiagramSpecification':
        """Ensure framework supports diagram type and output formats."""
        # Framework compatibility matrix
        framework_capabilities = {
            FrameworkType.D2: {
                'types': {DiagramType.C4_CONTEXT, DiagramType.C4_CONTAINER,
                         DiagramType.C4_COMPONENT, DiagramType.ARCHITECTURE, DiagramType.NETWORK},
                'formats': {OutputFormat.SVG, OutputFormat.PNG, OutputFormat.PDF}
            },
            FrameworkType.MERMAID: {
                'types': {DiagramType.SEQUENCE, DiagramType.FLOWCHART, DiagramType.ERD,
                         DiagramType.GANTT, DiagramType.STATE},
                'formats': {OutputFormat.SVG, OutputFormat.PNG, OutputFormat.PDF}
            },
            FrameworkType.PLANTUML: {
                'types': {DiagramType.SEQUENCE, DiagramType.CLASS, DiagramType.STATE,
                         DiagramType.C4_CONTEXT, DiagramType.C4_CONTAINER},
                'formats': {OutputFormat.SVG, OutputFormat.PNG, OutputFormat.PDF}
            }
        }

        if self.framework and self.framework in framework_capabilities:
            capabilities = framework_capabilities[self.framework]

            # Check diagram type compatibility
            if self.type not in capabilities['types']:
                raise ValueError(
                    f"Framework {self.framework.value} does not support diagram type {self.type.value}"
                )

            # Check output format compatibility
            unsupported_formats = set(self.output_formats) - capabilities['formats']
            if unsupported_formats:
                raise ValueError(
                    f"Framework {self.framework.value} does not support formats: {unsupported_formats}"
                )

        return self

    @model_validator(mode='after')
    def validate_framework_options(self) -> 'DiagramSpecification':
        """Validate framework-specific options."""
        if self.framework and self.options:
            if self.framework == FrameworkType.MERMAID:
                if isinstance(self.options, dict):
                    # Convert dict to MermaidConfig for validation
                    try:
                        MermaidConfig.model_validate(self.options)
                    except ValueError as e:
                        raise ValueError(f"Invalid Mermaid configuration: {e}")
                elif not isinstance(self.options, MermaidConfig):
                    raise ValueError("Mermaid framework requires MermaidConfig options")
            elif self.framework == FrameworkType.D2:
                if isinstance(self.options, dict):
                    # Convert dict to D2Options for validation
                    try:
                        D2Options.model_validate(self.options)
                    except ValueError as e:
                        raise ValueError(f"Invalid D2 configuration: {e}")
                elif not isinstance(self.options, D2Options):
                    raise ValueError("D2 framework requires D2Options")
        return self

class ContentFile(T2DBaseModel):
    """Markdown files maintained by Claude Code agents."""

    id: IdField
    path: PathField
    type: 'ContentType'
    agent: str = Field(pattern=r'^t2d-[a-z0-9-]+$')
    base_prompt: InstructionsField
    diagram_refs: List[str] = Field(default_factory=list)
    title: Optional[NameField] = None
    last_updated: datetime

    @field_validator('path')
    @classmethod
    def validate_markdown_extension(cls, v: str) -> str:
        """Ensure content files are markdown."""
        path = Path(v)
        if path.suffix not in {'.md', '.markdown'}:
            raise ValueError('Content files must be markdown (.md or .markdown)')
        return v

    @field_validator('agent')
    @classmethod
    def validate_agent_type(cls, v: str) -> str:
        """Ensure agent is a valid content agent."""
        valid_agents = {
            't2d-markdown-maintainer',
            't2d-mkdocs-formatter',
            't2d-marp-slides'
        }
        if v not in valid_agents:
            raise ValueError(f'Agent must be one of: {valid_agents}')
        return v
```

## Framework-Specific Options

### D2Options with Advanced Configuration

```python
from typing import Literal, List, Optional
import warnings
import os

class D2Options(T2DBaseModel):
    """Advanced D2 diagram configuration options."""

    # Layout engines
    layout_engine: Literal["dagre", "elk", "tala"] = Field(
        default="dagre",
        description="D2 layout engine to use"
    )

    # Themes
    theme: Optional[Literal[
        "neutral-default", "neutral-grey",
        "flagship-terrastruct", "cool-classics",
        "mixed-berry-blue", "grape-soda",
        "aubergine", "colorblind-clear",
        "vanilla-nitro-cola", "orange-creamsicle",
        "shirley-temple", "earth-tones",
        "everglade", "buttered-toast"
    ]] = Field(
        default="neutral-default",
        description="D2 theme to apply"
    )

    # Rendering options
    sketch: bool = Field(
        default=False,
        description="Enable hand-drawn sketch mode"
    )

    pad: int = Field(
        default=100,
        ge=0,
        description="Padding around the diagram in pixels"
    )

    # Animation options
    animate_interval: Optional[int] = Field(
        default=None,
        ge=0,
        description="Animation interval in milliseconds for multi-board diagrams"
    )

    # Size constraints
    width: Optional[int] = Field(
        default=None,
        gt=0,
        description="Target width in pixels"
    )

    height: Optional[int] = Field(
        default=None,
        gt=0,
        description="Target height in pixels"
    )

    # Export options
    scale: float = Field(
        default=1.0,
        gt=0,
        le=4,
        description="Scale factor for output (0.5 = 50%, 2 = 200%)"
    )

    # Advanced layout options
    direction: Literal["up", "down", "right", "left"] = Field(
        default="down",
        description="Primary direction for layout flow"
    )

    # Font configuration
    font_family: Optional[str] = Field(
        default=None,
        description="Override default font family"
    )

    font_size: Optional[int] = Field(
        default=None,
        ge=8,
        le=72,
        description="Base font size in points"
    )

    # Connection styling
    stroke_width: Optional[int] = Field(
        default=None,
        ge=1,
        le=10,
        description="Default stroke width for connections"
    )

    # Multi-board options
    board_index: Optional[int] = Field(
        default=None,
        ge=0,
        description="Specific board index to render from multi-board diagram"
    )

    # Compiler options
    force_appendix: bool = Field(
        default=False,
        description="Force rendering of appendix elements"
    )

    center: bool = Field(
        default=False,
        description="Center the diagram in the viewport"
    )

    @field_validator('layout_engine')
    @classmethod
    def validate_tala_license(cls, v: str) -> str:
        """Warn if Tala is selected without license."""
        if v == "tala":
            # In real implementation, check for TALA_LICENSE_KEY env var
            import os
            if not os.environ.get("TALA_LICENSE_KEY"):
                warnings.warn(
                    "Tala layout engine requires a license key. "
                    "Set TALA_LICENSE_KEY environment variable.",
                    UserWarning
                )
        return v

    def to_cli_args(self) -> List[str]:
        """Convert options to D2 CLI arguments."""
        args = []

        # Add layout engine
        args.extend(["--layout", self.layout_engine])

        # Add theme if specified
        if self.theme:
            args.extend(["--theme", self.theme])

        # Add sketch mode
        if self.sketch:
            args.append("--sketch")

        # Add padding
        args.extend(["--pad", str(self.pad)])

        # Add dimensions if specified
        if self.width:
            args.extend(["--width", str(self.width)])
        if self.height:
            args.extend(["--height", str(self.height)])

        # Add scale
        if self.scale != 1.0:
            args.extend(["--scale", str(self.scale)])

        # Add animation interval for multi-board
        if self.animate_interval:
            args.extend(["--animate-interval", str(self.animate_interval)])

        # Add direction
        args.extend(["--direction", self.direction])

        # Add board index if specified
        if self.board_index is not None:
            args.extend(["--board", str(self.board_index)])

        # Add force appendix
        if self.force_appendix:
            args.append("--force-appendix")

        # Add center
        if self.center:
            args.append("--center")

        return args

    def to_style_string(self) -> str:
        """Generate D2 style configuration string."""
        styles = []

        if self.font_family:
            styles.append(f"font: {self.font_family}")

        if self.font_size:
            styles.append(f"font-size: {self.font_size}")

        if self.stroke_width:
            styles.append(f"stroke-width: {self.stroke_width}")

        if styles:
            return f"style: {{\n  {chr(10).join(styles)}\n}}"
        return ""
```

### D2Options Usage Example

```python
# Example usage in diagram specification
diagram_spec = DiagramSpecification(
    id="architecture",
    type=DiagramType.C4_CONTAINER,
    framework=DiagramFramework.D2,
    title="System Architecture",
    instructions="...",
    options=D2Options(
        layout_engine="elk",
        theme="cool-classics",
        sketch=True,
        width=1920,
        height=1080,
        direction="right"
    )
)

# Generate CLI command
cli_args = diagram_spec.options.to_cli_args()
# Results in: ["--layout", "elk", "--theme", "cool-classics", "--sketch", "--width", "1920", "--height", "1080", "--direction", "right", ...]
```

### MkDocsPageConfig Model

```python
class MkDocsPageConfig(T2DBaseModel):
    """Configuration for generating MkDocs-compatible pages to integrate into existing sites."""

    # Output configuration
    output_dir: Path = Field(
        default=Path("docs"),
        description="Directory where markdown pages will be generated"
    )

    pages_subdir: Optional[Path] = Field(
        default=None,
        description="Subdirectory within output_dir for these pages (e.g., 'api', 'architecture')"
    )

    # Page metadata (for frontmatter)
    page_template: Optional[str] = Field(
        default=None,
        description="Template name if the site uses custom templates"
    )

    page_category: Optional[str] = Field(
        default=None,
        description="Category or section these pages belong to"
    )

    page_tags: Optional[List[str]] = Field(
        default=None,
        description="Tags to apply to generated pages"
    )

    page_authors: Optional[List[str]] = Field(
        default=None,
        description="Authors to credit in page metadata"
    )

    # Navigation hints
    nav_parent: Optional[str] = Field(
        default=None,
        description="Parent section in nav where these pages should appear"
    )

    nav_position: Optional[int] = Field(
        default=None,
        description="Position/weight in navigation ordering"
    )

    nav_title_prefix: Optional[str] = Field(
        default=None,
        description="Prefix to add to page titles in navigation"
    )

    # Diagram integration
    diagrams_dir: str = Field(
        default="diagrams",
        description="Relative path from page location to diagrams directory"
    )

    diagram_format: Literal["svg", "png", "both"] = Field(
        default="svg",
        description="Preferred diagram format for embedding"
    )

    diagram_classes: Optional[List[str]] = Field(
        default=None,
        description="CSS classes to apply to diagram images"
    )

    # Material theme features
    use_admonitions: bool = Field(
        default=True,
        description="Use Material admonition syntax for callouts"
    )

    use_content_tabs: bool = Field(
        default=False,
        description="Use Material content tabs for multi-version content"
    )

    use_annotations: bool = Field(
        default=False,
        description="Use Material annotations feature"
    )

    use_grids: bool = Field(
        default=False,
        description="Use Material grids for layout"
    )

    # Code block configuration
    code_highlight: bool = Field(
        default=True,
        description="Enable syntax highlighting in code blocks"
    )

    code_line_numbers: bool = Field(
        default=False,
        description="Show line numbers in code blocks"
    )

    code_copy_button: bool = Field(
        default=True,
        description="Add copy button to code blocks"
    )

    # Page generation options
    include_toc: bool = Field(
        default=True,
        description="Include table of contents in pages"
    )

    toc_depth: int = Field(
        default=3,
        ge=1,
        le=6,
        description="Maximum heading level for TOC"
    )

    include_edit_link: bool = Field(
        default=False,
        description="Include edit link (requires repo_url in main mkdocs.yml)"
    )

    include_created_date: bool = Field(
        default=False,
        description="Include creation date in page metadata"
    )

    include_updated_date: bool = Field(
        default=True,
        description="Include last updated date in page metadata"
    )

    # Index page generation
    generate_index: bool = Field(
        default=True,
        description="Generate an index page for the documentation set"
    )

    index_title: str = Field(
        default="Documentation",
        description="Title for the index page"
    )

    index_description: Optional[str] = Field(
        default=None,
        description="Description for the index page"
    )

    # Cross-references
    cross_reference_base: Optional[str] = Field(
        default=None,
        description="Base path for cross-references between generated pages"
    )

    enable_relative_links: bool = Field(
        default=True,
        description="Use relative links between generated pages"
    )

    # Integration hints
    mkdocs_yml_path: Optional[Path] = Field(
        default=None,
        description="Path to existing mkdocs.yml to read configuration from"
    )

    inherit_theme_config: bool = Field(
        default=True,
        description="Inherit theme configuration from main site"
    )

    custom_css_classes: Optional[Dict[str, str]] = Field(
        default=None,
        description="Custom CSS classes to apply to elements"
    )

    def generate_frontmatter(self,
                           title: str,
                           description: Optional[str] = None,
                           extra_metadata: Optional[Dict[str, Any]] = None) -> str:
        """Generate frontmatter for a page."""
        fm = ["---"]
        fm.append(f"title: {title}")

        if description:
            fm.append(f"description: {description}")

        if self.page_template:
            fm.append(f"template: {self.page_template}")

        if self.page_category:
            fm.append(f"category: {self.page_category}")

        if self.page_tags:
            fm.append(f"tags: {', '.join(self.page_tags)}")

        if self.page_authors:
            fm.append(f"authors: {', '.join(self.page_authors)}")

        if self.nav_position is not None:
            fm.append(f"nav_order: {self.nav_position}")

        if self.include_created_date:
            fm.append(f"created: {datetime.utcnow().isoformat()}")

        if self.include_updated_date:
            fm.append(f"updated: {datetime.utcnow().isoformat()}")

        # Add any extra metadata
        if extra_metadata:
            for key, value in extra_metadata.items():
                if isinstance(value, list):
                    fm.append(f"{key}: {', '.join(str(v) for v in value)}")
                else:
                    fm.append(f"{key}: {value}")

        fm.append("---")
        fm.append("")

        return "\n".join(fm)

    def get_diagram_reference(self, diagram_path: Path, alt_text: str) -> str:
        """Generate markdown for embedding a diagram."""
        rel_path = f"{self.diagrams_dir}/{diagram_path.name}"

        classes = ""
        if self.diagram_classes:
            classes = f"{{: .{' .'.join(self.diagram_classes)} }}"

        # Material for MkDocs supports figure syntax
        if self.use_annotations:
            return f"<figure markdown>\n  ![{alt_text}]({rel_path})\n  <figcaption>{alt_text}</figcaption>\n</figure>"
        else:
            return f"![{alt_text}]({rel_path}){classes}"

    def get_admonition(self,
                      type: str,
                      title: Optional[str] = None,
                      content: str = "") -> str:
        """Generate Material admonition syntax."""
        if not self.use_admonitions:
            return f"**{title or type.upper()}**: {content}"

        if title:
            return f'!!! {type} "{title}"\n    {content}'
        else:
            return f'!!! {type}\n    {content}'

    def get_content_tab(self, tabs: Dict[str, str]) -> str:
        """Generate Material content tabs syntax."""
        if not self.use_content_tabs:
            # Fallback to sections
            sections = []
            for tab_name, tab_content in tabs.items():
                sections.append(f"### {tab_name}\n\n{tab_content}")
            return "\n\n".join(sections)

        tab_blocks = []
        for tab_name, tab_content in tabs.items():
            tab_blocks.append(f'=== "{tab_name}"\n\n    {tab_content}')

        return "\n\n".join(tab_blocks)

    def get_output_path(self, filename: str) -> Path:
        """Get the full output path for a file."""
        if self.pages_subdir:
            return self.output_dir / self.pages_subdir / filename
        return self.output_dir / filename

    def create_nav_entry(self, pages: List[str]) -> Dict[str, Any]:
        """Create navigation entry for mkdocs.yml."""
        nav_entry = {}

        if self.nav_parent:
            # Nested under parent
            nav_entry[self.nav_parent] = []
            for page in pages:
                page_title = page.replace('.md', '').replace('-', ' ').title()
                if self.nav_title_prefix:
                    page_title = f"{self.nav_title_prefix} {page_title}"

                if self.pages_subdir:
                    nav_entry[self.nav_parent].append({
                        page_title: f"{self.pages_subdir}/{page}"
                    })
                else:
                    nav_entry[self.nav_parent].append({
                        page_title: page
                    })
        else:
            # Top level
            for page in pages:
                page_title = page.replace('.md', '').replace('-', ' ').title()
                if self.nav_title_prefix:
                    page_title = f"{self.nav_title_prefix} {page_title}"

                if self.pages_subdir:
                    nav_entry[page_title] = f"{self.pages_subdir}/{page}"
                else:
                    nav_entry[page_title] = page

        return nav_entry
```

### MkDocsPageConfig Usage Example

```python
# Example: Generating pages for an existing MkDocs site
mkdocs_config = MkDocsPageConfig(
    output_dir=Path("existing-site/docs"),
    pages_subdir=Path("api/generated"),
    nav_parent="API Documentation",
    nav_title_prefix="Auto",
    page_category="api",
    page_tags=["generated", "api", "reference"],
    use_admonitions=True,
    use_content_tabs=True,
    diagram_format="svg",
    diagram_classes=["diagram", "center"]
)

# Generate a page with frontmatter
page_content = mkdocs_config.generate_frontmatter(
    title="System Architecture",
    description="Generated architecture documentation",
    extra_metadata={"revision": "1.0"}
)

# Add content with Material features
page_content += "# System Architecture\n\n"

# Add an admonition
page_content += mkdocs_config.get_admonition(
    "info",
    "Generated Documentation",
    "This page was auto-generated from the PRD"
)

# Embed a diagram
page_content += mkdocs_config.get_diagram_reference(
    Path("architecture.svg"),
    "System Architecture Diagram"
)

# Create content tabs for different views
tabs_content = mkdocs_config.get_content_tab({
    "Overview": "High-level system architecture...",
    "Components": "Detailed component descriptions...",
    "Deployment": "Deployment architecture..."
})
page_content += tabs_content

# Save to the right location
output_path = mkdocs_config.get_output_path("architecture.md")
output_path.write_text(page_content)

# Generate nav entry for mkdocs.yml (to be manually added or programmatically merged)
nav_update = mkdocs_config.create_nav_entry(["architecture.md", "database.md", "api.md"])
# Results in:
# {"API Documentation": [
#     {"Auto Architecture": "api/generated/architecture.md"},
#     {"Auto Database": "api/generated/database.md"},
#     {"Auto Api": "api/generated/api.md"}
# ]}
```

### MermaidConfig Model

```python
from typing import Union

class MermaidConfig(T2DBaseModel):
    """Advanced Mermaid diagram configuration options."""

    # Theme configuration
    theme: Literal[
        "default", "dark", "forest", "neutral",
        "base", "minimal", "neo", "future", "vintage"
    ] = Field(
        default="default",
        description="Mermaid theme to apply"
    )

    # Custom theme variables
    theme_variables: Optional[Dict[str, str]] = Field(
        default=None,
        description="Custom theme CSS variables",
        example={
            "primaryColor": "#ff0000",
            "primaryTextColor": "#fff",
            "primaryBorderColor": "#ff0000",
            "lineColor": "#ffcc00",
            "secondaryColor": "#006400",
            "tertiaryColor": "#fff"
        }
    )

    # Layout configuration
    look_and_feel: Literal["classic", "handDrawn"] = Field(
        default="classic",
        description="Visual style of the diagram"
    )

    # Security level
    security_level: Literal["strict", "loose", "antiscript"] = Field(
        default="strict",
        description="Security level for rendering"
    )

    # Diagram-specific settings
    flowchart_config: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Flowchart-specific configuration",
        example={
            "curve": "linear",  # or "basis", "cardinal", "step"
            "padding": 10,
            "nodeSpacing": 50,
            "rankSpacing": 50,
            "diagramPadding": 8,
            "useMaxWidth": True,
            "htmlLabels": True
        }
    )

    sequence_config: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Sequence diagram configuration",
        example={
            "diagramMarginX": 50,
            "diagramMarginY": 10,
            "actorMargin": 50,
            "width": 150,
            "height": 65,
            "boxMargin": 10,
            "boxTextMargin": 5,
            "noteMargin": 10,
            "messageMargin": 35,
            "mirrorActors": True,
            "bottomMarginAdj": 1,
            "useMaxWidth": True,
            "rightAngles": False,
            "showSequenceNumbers": False
        }
    )

    gantt_config: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Gantt chart configuration",
        example={
            "numberSectionStyles": 4,
            "axisFormat": "%Y-%m-%d",
            "topAxis": False,
            "displayMode": "compact",  # or "normal"
            "gridLineStartPadding": 350,
            "fontSize": 11,
            "fontFamily": '"Open-Sans", sans-serif',
            "sectionFontSize": 11,
            "numberSectionStyles": 4,
            "leftPadding": 75
        }
    )

    er_config: Optional[Dict[str, Any]] = Field(
        default=None,
        description="ER diagram configuration",
        example={
            "diagramPadding": 20,
            "layoutDirection": "TB",  # or "LR", "RL", "BT"
            "minEntityWidth": 100,
            "minEntityHeight": 75,
            "entityPadding": 15,
            "stroke": "gray",
            "fill": "honeydew",
            "fontSize": 12,
            "useMaxWidth": True
        }
    )

    pie_config: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Pie chart configuration",
        example={
            "useMaxWidth": True,
            "textPosition": 0.75,
            "legendPosition": "right"  # or "bottom", "left", "top"
        }
    )

    state_config: Optional[Dict[str, Any]] = Field(
        default=None,
        description="State diagram configuration",
        example={
            "dividerMargin": 10,
            "sizeUnit": 5,
            "padding": 5,
            "textHeight": 10,
            "titleShift": -15,
            "noteMargin": 10,
            "forkWidth": 70,
            "forkHeight": 7,
            "miniPadding": 2,
            "fontSizeFactor": 5.02,
            "fontSize": 24,
            "labelHeight": 16,
            "edgeLengthFactor": "20",
            "compositTitleSize": 35,
            "radius": 5,
            "useMaxWidth": True
        }
    )

    # Rendering options
    width: Optional[int] = Field(
        default=None,
        gt=0,
        description="Diagram width in pixels"
    )

    height: Optional[int] = Field(
        default=None,
        gt=0,
        description="Diagram height in pixels"
    )

    background_color: Optional[str] = Field(
        default="white",
        description="Background color (CSS color value)"
    )

    # Output options
    puppeteer_config: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Puppeteer configuration for rendering",
        example={
            "headless": True,
            "args": ["--no-sandbox", "--disable-setuid-sandbox"]
        }
    )

    # Font configuration
    font_family: Optional[str] = Field(
        default=None,
        description="Override default font family"
    )

    # Accessibility
    wrap: bool = Field(
        default=False,
        description="Enable text wrapping in nodes"
    )

    @model_validator(mode='after')
    def apply_diagram_defaults(self) -> 'MermaidConfig':
        """Apply sensible defaults based on look_and_feel."""
        if self.look_and_feel == "handDrawn":
            if not self.theme_variables:
                self.theme_variables = {}
            # Apply hand-drawn style variables
            self.theme_variables.update({
                "fontFamily": "Kalam, cursive",
                "primaryBorderColor": "#666",
                "primaryColor": "#f9f9f9"
            })
        return self

    def to_config_json(self) -> str:
        """Generate mermaid configuration JSON."""
        config = {
            "theme": self.theme,
            "securityLevel": self.security_level,
            "look": self.look_and_feel
        }

        # Add theme variables
        if self.theme_variables:
            config["themeVariables"] = self.theme_variables

        # Add diagram-specific configs
        if self.flowchart_config:
            config["flowchart"] = self.flowchart_config
        if self.sequence_config:
            config["sequence"] = self.sequence_config
        if self.gantt_config:
            config["gantt"] = self.gantt_config
        if self.er_config:
            config["er"] = self.er_config
        if self.pie_config:
            config["pie"] = self.pie_config
        if self.state_config:
            config["state"] = self.state_config

        # Add font family
        if self.font_family:
            config["fontFamily"] = self.font_family

        # Add wrap
        config["wrap"] = self.wrap

        return json.dumps(config, indent=2)

    def to_cli_args(self) -> List[str]:
        """Convert to mermaid CLI (mmdc) arguments."""
        args = []

        # Create config file content
        config_content = self.to_config_json()

        # In real implementation, write to temp file
        # For now, return args that would be used
        args.extend(["--configFile", "<generated-config.json>"])

        # Add dimensions
        if self.width:
            args.extend(["--width", str(self.width)])
        if self.height:
            args.extend(["--height", str(self.height)])

        # Add background color
        if self.background_color:
            args.extend(["--backgroundColor", self.background_color])

        # Add puppeteer config if specified
        if self.puppeteer_config:
            args.extend(["--puppeteerConfigFile", "<puppeteer-config.json>"])

        return args
```

### Framework Options Usage Examples

```python
# Example usage with Mermaid diagram specification
diagram_spec = DiagramSpecification(
    id="user-flow",
    type=DiagramType.SEQUENCE,
    framework=DiagramFramework.MERMAID,
    agent="t2d-mermaid-generator",
    title="User Authentication Flow",
    instructions="Create a sequence diagram showing user login flow with authentication service, user database, and session management",
    output_file="docs/assets/user-flow.mmd",
    output_formats=[OutputFormat.SVG, OutputFormat.PNG],
    options=MermaidConfig(
        theme="forest",
        look_and_feel="handDrawn",
        sequence_config={
            "mirrorActors": True,
            "showSequenceNumbers": True,
            "rightAngles": True
        },
        width=1600,
        height=900
    )
)

# Generate configuration
config_json = diagram_spec.options.to_config_json()
cli_args = diagram_spec.options.to_cli_args()

# Example with theme customization
custom_theme_spec = DiagramSpecification(
    id="system-arch",
    type=DiagramType.FLOWCHART,
    framework=DiagramFramework.MERMAID,
    agent="t2d-mermaid-generator",
    title="System Architecture",
    instructions="Create a flowchart showing microservices architecture with API gateway, service mesh, and databases",
    output_file="docs/assets/architecture.mmd",
    output_formats=[OutputFormat.SVG],
    options=MermaidConfig(
        theme="dark",
        theme_variables={
            "primaryColor": "#ff6b6b",
            "primaryTextColor": "#ffffff",
            "primaryBorderColor": "#ff6b6b",
            "lineColor": "#4ecdc4",
            "secondaryColor": "#45b7d1",
            "tertiaryColor": "#96ceb4"
        },
        flowchart_config={
            "curve": "basis",
            "padding": 15,
            "nodeSpacing": 60,
            "rankSpacing": 80,
            "useMaxWidth": True,
            "htmlLabels": True
        },
        background_color="transparent",
        wrap=True
    )
)

# Example with Gantt chart configuration
gantt_spec = DiagramSpecification(
    id="project-timeline",
    type=DiagramType.GANTT,
    framework=DiagramFramework.MERMAID,
    agent="t2d-mermaid-generator",
    title="Project Development Timeline",
    instructions="Create a Gantt chart showing development phases, milestones, and dependencies",
    output_file="docs/assets/timeline.mmd",
    output_formats=[OutputFormat.SVG, OutputFormat.PNG],
    options=MermaidConfig(
        theme="neutral",
        gantt_config={
            "axisFormat": "%m/%d",
            "displayMode": "compact",
            "fontSize": 12,
            "fontFamily": '"Roboto", sans-serif',
            "leftPadding": 120
        },
        width=1400,
        height=600
    )
)

# Example with D2 diagram specification for comparison
d2_spec = DiagramSpecification(
    id="architecture-d2",
    type=DiagramType.C4_CONTAINER,
    framework=DiagramFramework.D2,
    agent="t2d-d2-generator",
    title="System Architecture (D2)",
    instructions="Create a C4 container diagram showing microservices architecture",
    output_file="docs/assets/architecture.d2",
    output_formats=[OutputFormat.SVG],
    options=D2Options(
        layout_engine="elk",
        theme="cool-classics",
        sketch=True,
        width=1920,
        height=1080,
        direction="right"
    )
)
```

### MarpConfig Model

```python
class MarpConfig(T2DBaseModel):
    """Advanced Marp presentation configuration with directives and exports."""

    # Theme configuration
    theme: Literal[
        "default", "gaia", "uncover",
        # Custom themes can be added
    ] = Field(
        default="default",
        description="Marp theme to apply"
    )

    custom_theme_path: Optional[Path] = Field(
        default=None,
        description="Path to custom CSS theme file"
    )

    # Global directives
    marp: bool = Field(
        default=True,
        description="Enable Marp rendering"
    )

    size: Literal["4:3", "16:9", "4K", "A4", "Letter"] = Field(
        default="16:9",
        description="Slide size/aspect ratio"
    )

    paginate: bool = Field(
        default=True,
        description="Show page numbers"
    )

    header: Optional[str] = Field(
        default=None,
        description="Global header text for all slides"
    )

    footer: Optional[str] = Field(
        default=None,
        description="Global footer text for all slides"
    )

    # Style configuration
    style: Optional[str] = Field(
        default=None,
        description="Custom CSS styles",
        example="""
        section {
            background-color: #f0f0f0;
            font-family: 'Helvetica Neue', Arial, sans-serif;
        }
        h1 {
            color: #333;
            border-bottom: 3px solid #007acc;
        }
        """
    )

    background_color: Optional[str] = Field(
        default=None,
        description="Default background color"
    )

    background_image: Optional[str] = Field(
        default=None,
        description="URL or path to background image"
    )

    background_size: Literal["cover", "contain", "auto", "fit"] = Field(
        default="cover",
        description="Background image sizing"
    )

    # Typography
    font_family: Optional[str] = Field(
        default=None,
        description="Primary font family"
    )

    font_size: Optional[str] = Field(
        default=None,
        description="Base font size (e.g., '28px', '2em')"
    )

    # Color scheme
    color: Optional[str] = Field(
        default=None,
        description="Default text color"
    )

    # Slide-specific directives
    class_: Optional[str] = Field(
        default=None,
        alias="class",
        description="CSS class to apply to slides"
    )

    # Transition effects (for HTML export)
    transition: Optional[Literal[
        "none", "fade", "slide", "convex",
        "concave", "zoom", "linear"
    ]] = Field(
        default=None,
        description="Slide transition effect for HTML export"
    )

    transition_speed: Literal["slow", "default", "fast"] = Field(
        default="default",
        description="Transition speed"
    )

    # Export configurations
    html_options: Optional[Dict[str, Any]] = Field(
        default=None,
        description="HTML export options",
        example={
            "printable": True,
            "progress": True,
            "controls": True,
            "controlsLayout": "bottom-right",
            "controlsTutorial": True,
            "hash": True,
            "respondToHashChanges": True
        }
    )

    pdf_options: Optional[Dict[str, Any]] = Field(
        default=None,
        description="PDF export options",
        example={
            "format": "A4",
            "landscape": True,
            "printBackground": True,
            "displayHeaderFooter": True,
            "margin": {
                "top": "1cm",
                "right": "1cm",
                "bottom": "1cm",
                "left": "1cm"
            }
        }
    )

    pptx_options: Optional[Dict[str, Any]] = Field(
        default=None,
        description="PowerPoint export options",
        example={
            "output_width": 1920,
            "output_height": 1080
        }
    )

    # Advanced features
    math: Literal["katex", "mathjax", None] = Field(
        default="katex",
        description="Math rendering engine"
    )

    emoji_shortcode: bool = Field(
        default=True,
        description="Enable emoji shortcodes like :smile:"
    )

    html: bool = Field(
        default=True,
        description="Allow raw HTML in markdown"
    )

    # Auto-play configuration (for HTML)
    auto_play: Optional[int] = Field(
        default=None,
        ge=0,
        description="Auto-advance slides after N seconds (0 = disabled)"
    )

    loop: bool = Field(
        default=False,
        description="Loop presentation when auto-playing"
    )

    # Speaker notes
    notes: bool = Field(
        default=True,
        description="Enable speaker notes"
    )

    @field_validator('custom_theme_path')
    @classmethod
    def validate_theme_exists(cls, v: Optional[Path]) -> Optional[Path]:
        """Check if custom theme file exists."""
        if v and not v.exists():
            raise ValueError(f"Custom theme file not found: {v}")
        return v

    def to_frontmatter(self) -> str:
        """Generate Marp frontmatter for markdown file."""
        fm = ["---"]

        # Core directives
        fm.append(f"marp: {str(self.marp).lower()}")
        fm.append(f"theme: {self.theme}")
        fm.append(f"size: {self.size}")
        fm.append(f"paginate: {str(self.paginate).lower()}")

        # Optional directives
        if self.header:
            fm.append(f"header: '{self.header}'")
        if self.footer:
            fm.append(f"footer: '{self.footer}'")
        if self.background_color:
            fm.append(f"backgroundColor: {self.background_color}")
        if self.background_image:
            fm.append(f"backgroundImage: url('{self.background_image}')")
        if self.background_size:
            fm.append(f"backgroundSize: {self.background_size}")
        if self.color:
            fm.append(f"color: {self.color}")
        if self.class_:
            fm.append(f"class: {self.class_}")
        if self.math:
            fm.append(f"math: {self.math}")

        # Style block
        if self.style or self.font_family or self.font_size:
            fm.append("style: |")
            if self.font_family or self.font_size:
                fm.append("  section {")
                if self.font_family:
                    fm.append(f"    font-family: {self.font_family};")
                if self.font_size:
                    fm.append(f"    font-size: {self.font_size};")
                fm.append("  }")
            if self.style:
                for line in self.style.strip().split('\n'):
                    fm.append(f"  {line}")

        fm.append("---")
        fm.append("")  # Empty line after frontmatter

        return "\n".join(fm)

    def to_cli_args(self) -> List[str]:
        """Convert to Marp CLI arguments."""
        args = []

        # Theme
        if self.custom_theme_path:
            args.extend(["--theme", str(self.custom_theme_path)])
        elif self.theme != "default":
            args.extend(["--theme", self.theme])

        # HTML options
        if self.html:
            args.append("--html")

        # Math
        if self.math:
            args.extend(["--math", self.math])

        # PDF options
        if self.pdf_options:
            if self.pdf_options.get("format"):
                args.extend(["--pdf-format", self.pdf_options["format"]])
            if self.pdf_options.get("landscape"):
                args.append("--pdf-landscape")

        # Allow local files
        args.append("--allow-local-files")

        return args

    def to_engine_config(self) -> Dict[str, Any]:
        """Generate Marp engine configuration."""
        config = {
            "html": self.html,
            "emoji": {
                "shortcode": self.emoji_shortcode
            }
        }

        if self.math:
            config["math"] = self.math

        if self.html_options:
            config["options"] = self.html_options

        return config

class SlideDirective(T2DBaseModel):
    """Individual slide directives for fine control."""

    # Layout directives
    class_: Optional[Literal[
        "lead", "invert", "fit", "centered"
    ]] = Field(default=None, alias="class")

    # Background directives (per slide)
    bg: Optional[str] = Field(
        default=None,
        description="Background color or image URL"
    )

    bg_color: Optional[str] = Field(
        default=None,
        description="Background color"
    )

    bg_image: Optional[str] = Field(
        default=None,
        description="Background image URL"
    )

    bg_size: Optional[str] = Field(
        default=None,
        description="Background size"
    )

    # Pagination
    paginate_skip: bool = Field(
        default=False,
        description="Skip page number on this slide"
    )

    # Header/Footer overrides
    header: Optional[str] = None
    footer: Optional[str] = None

    def to_markdown_comment(self) -> str:
        """Convert to HTML comment for slide."""
        directives = []

        if self.class_:
            directives.append(f"_class: {self.class_}")
        if self.bg:
            directives.append(f"bg: {self.bg}")
        if self.bg_color:
            directives.append(f"backgroundColor: {self.bg_color}")
        if self.bg_image:
            directives.append(f"backgroundImage: url('{self.bg_image}')")
        if self.bg_size:
            directives.append(f"backgroundSize: {self.bg_size}")
        if self.paginate_skip:
            directives.append("_paginate: false")
        if self.header is not None:
            directives.append(f"_header: '{self.header}'")
        if self.footer is not None:
            directives.append(f"_footer: '{self.footer}'")

        if directives:
            return f"<!-- {' '.join(directives)} -->"
        return ""
```

### Validation Examples

```python
# Example validation scenarios

def test_user_recipe_validation():
    """Examples of UserRecipe validation in action."""

    # Valid recipe
    valid_recipe = UserRecipe(
        name="ecommerce-system",
        version="1.0.0",
        prd=PRDContent(
            content="# E-Commerce System\n\nA modern e-commerce platform..."
        ),
        instructions=UserInstructions(
            diagrams=[
                DiagramRequest(
                    type="system architecture",
                    description="High-level system overview",
                    framework_preference="d2"
                )
            ]
        )
    )

    # Invalid: empty diagrams list
    try:
        invalid_recipe = UserRecipe(
            name="test",
            prd=PRDContent(content="content"),
            instructions=UserInstructions(diagrams=[])
        )
    except ValueError as e:
        print(f"Validation error: {e}")
        # Output: Validation error: Recipe must specify at least one diagram type

    # Invalid: both content and file_path provided
    try:
        invalid_prd = PRDContent(
            content="Some content",
            file_path="./prd.md"
        )
    except ValueError as e:
        print(f"Validation error: {e}")
        # Output: Validation error: Cannot provide both content and file_path

def test_diagram_specification_validation():
    """Examples of DiagramSpecification validation."""

    # Valid specification
    valid_spec = DiagramSpecification(
        id="system-arch",
        type=DiagramType.C4_CONTAINER,
        framework=FrameworkType.D2,
        agent="t2d-d2-generator",
        title="System Architecture",
        instructions="Create a C4 container diagram showing microservices architecture with API gateway, user service, order service, and payment service.",
        output_file="docs/assets/system.d2",
        output_formats=[OutputFormat.SVG, OutputFormat.PNG]
    )

    # Invalid: framework doesn't support diagram type
    try:
        invalid_spec = DiagramSpecification(
            id="sequence-diagram",
            type=DiagramType.SEQUENCE,
            framework=FrameworkType.D2,  # D2 doesn't support sequence diagrams well
            agent="t2d-d2-generator",
            title="User Flow",
            instructions="Create a sequence diagram",
            output_file="flow.d2",
            output_formats=[OutputFormat.SVG]
        )
    except ValueError as e:
        print(f"Validation error: {e}")
        # Output: Framework d2 does not support diagram type sequence

def test_processed_recipe_validation():
    """Examples of ProcessedRecipe cross-field validation."""

    diagram_spec = DiagramSpecification(
        id="arch-diagram",
        type=DiagramType.C4_CONTAINER,
        agent="t2d-d2-generator",
        title="Architecture",
        instructions="Create system architecture diagram",
        output_file="arch.d2",
        output_formats=[OutputFormat.SVG]
    )

    diagram_ref = DiagramReference(
        id="arch-diagram",
        title="Architecture",
        type=DiagramType.C4_CONTAINER,
        expected_path="docs/assets/arch.svg",
        status=GenerationStatus.PENDING
    )

    content_file = ContentFile(
        id="overview",
        path="content/overview.md",
        type=ContentType.DOCUMENTATION,
        agent="t2d-markdown-maintainer",
        base_prompt="Create technical documentation",
        diagram_refs=["arch-diagram"],
        last_updated=datetime.now()
    )

    # Valid processed recipe
    valid_processed = ProcessedRecipe(
        name="test-system",
        version="1.0.0",
        source_recipe="recipe.yaml",
        generated_at=datetime.now(),
        content_files=[content_file],
        diagram_specs=[diagram_spec],
        diagram_refs=[diagram_ref],
        outputs=OutputConfig(assets_dir="docs/assets")
    )

    # Invalid: content file references non-existent diagram
    try:
        invalid_content = ContentFile(
            id="overview",
            path="content/overview.md",
            type=ContentType.DOCUMENTATION,
            agent="t2d-markdown-maintainer",
            base_prompt="Create documentation",
            diagram_refs=["non-existent-diagram"],
            last_updated=datetime.now()
        )

        invalid_processed = ProcessedRecipe(
            name="test-system",
            version="1.0.0",
            source_recipe="recipe.yaml",
            generated_at=datetime.now(),
            content_files=[invalid_content],
            diagram_specs=[diagram_spec],
            diagram_refs=[diagram_ref],
            outputs=OutputConfig(assets_dir="docs/assets")
        )
    except ValueError as e:
        print(f"Validation error: {e}")
        # Output: Content file 'content/overview.md' references invalid diagrams: {'non-existent-diagram'}
```

### Advanced Validation Features

```python
class AdvancedValidationMixin(T2DBaseModel):
    """Mixin providing advanced validation utilities."""

    @classmethod
    def validate_file_size(cls, file_path: str, max_size_mb: int = 10) -> bool:
        """Validate file size doesn't exceed limit."""
        try:
            size = Path(file_path).stat().st_size
            max_bytes = max_size_mb * 1024 * 1024
            return size <= max_bytes
        except FileNotFoundError:
            return True  # Allow non-existent files (will be created)

    @classmethod
    def validate_directory_writable(cls, dir_path: str) -> bool:
        """Validate directory is writable."""
        path = Path(dir_path)
        try:
            path.mkdir(parents=True, exist_ok=True)
            test_file = path / ".write_test"
            test_file.touch()
            test_file.unlink()
            return True
        except (PermissionError, OSError):
            return False

    def get_validation_summary(self) -> Dict[str, Any]:
        """Get summary of model validation state."""
        try:
            self.model_validate(self.model_dump())
            return {
                "valid": True,
                "errors": [],
                "model_type": self.__class__.__name__
            }
        except ValueError as e:
            return {
                "valid": False,
                "errors": [str(e)],
                "model_type": self.__class__.__name__
            }

# Enhanced models inherit validation mixin
class EnhancedUserRecipe(UserRecipe, AdvancedValidationMixin):
    """UserRecipe with advanced validation features."""

    @model_validator(mode='after')
    def validate_advanced_constraints(self) -> 'EnhancedUserRecipe':
        """Additional validation beyond basic Pydantic."""
        # Validate PRD file size if file_path provided
        if self.prd.file_path:
            if not self.validate_file_size(self.prd.file_path, max_size_mb=1):
                raise ValueError('PRD file exceeds 1MB size limit')

        # Validate content length if embedded
        if self.prd.content and len(self.prd.content) > 1048576:  # 1MB
            raise ValueError('Embedded PRD content exceeds 1MB limit')

        return self

class ValidationReport(T2DBaseModel):
    """Comprehensive validation report for recipes."""

    recipe_name: str
    valid: bool
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    validated_at: datetime = Field(default_factory=datetime.now)
    validation_version: str = "1.0.0"

    def add_error(self, error: str) -> None:
        """Add validation error."""
        self.errors.append(error)
        self.valid = False

    def add_warning(self, warning: str) -> None:
        """Add validation warning."""
        self.warnings.append(warning)

    def is_valid(self) -> bool:
        """Check if validation passed."""
        return self.valid and len(self.errors) == 0
```

## Configuration and Usage

### Model Configuration Summary

```python
# All models inherit from T2DBaseModel with:
# - extra='forbid': Reject unexpected fields
# - validate_assignment=True: Validate on field updates
# - str_strip_whitespace=True: Auto-trim string fields
# - frozen=False: Allow field mutations
# - use_enum_values=True: Serialize enum values properly

# Field validation examples:
# - @field_validator for single field validation
# - @model_validator(mode='after') for cross-field validation
# - Annotated types for reusable field constraints
# - Custom validation methods for complex business rules

# Type annotations provide:
# - Pattern validation (regex)
# - Length constraints (min/max)
# - Range validation (gt, ge, lt, le)
# - Format validation (email, URL)
# - Cross-reference validation (foreign keys)
```

### Best Practices

1. **Use Annotated Types**: Define reusable field types with consistent validation
2. **Field-Level Validation**: Use `@field_validator` for single field constraints
3. **Model-Level Validation**: Use `@model_validator` for cross-field business rules
4. **Error Messages**: Provide clear, actionable error messages
5. **Performance**: Keep validation logic efficient for large datasets
6. **Documentation**: Document validation rules in field descriptions

### Integration with T2D-Kit

```python
# MCP server integration
def validate_recipe_file(file_path: str) -> ValidationReport:
    """Validate recipe file using enhanced models."""
    try:
        with open(file_path) as f:
            data = yaml.safe_load(f)

        # Use enhanced model for validation
        recipe = EnhancedUserRecipe.model_validate(data)

        report = ValidationReport(
            recipe_name=recipe.name,
            valid=True
        )

        # Additional business rule validations
        if len(recipe.instructions.diagrams) > 50:
            report.add_warning("Large number of diagrams may impact performance")

        return report

    except ValueError as e:
        return ValidationReport(
            recipe_name="unknown",
            valid=False,
            errors=[str(e)]
        )

# CLI integration
def enhanced_validation_command(recipe_path: str) -> None:
    """CLI command for enhanced recipe validation."""
    report = validate_recipe_file(recipe_path)

    if report.is_valid():
        print(f"✅ Recipe '{report.recipe_name}' is valid")
        if report.warnings:
            print("⚠️  Warnings:")
            for warning in report.warnings:
                print(f"  - {warning}")
    else:
        print(f"❌ Recipe validation failed:")
        for error in report.errors:
            print(f"  - {error}")
```

## File-Based State Management

Since we're using a simplified architecture without an orchestrator, implement file-based state management for coordination between agents:

### State Directory Structure
```python
class StateManager(T2DBaseModel):
    """Manages file-based state for agent coordination."""

    state_dir: Path = Field(
        default=Path(".t2d-state"),
        description="Directory for state files"
    )

    @field_validator('state_dir')
    @classmethod
    def ensure_state_dir(cls, v: Path) -> Path:
        """Create state directory if it doesn't exist."""
        v.mkdir(exist_ok=True)
        return v

    def write_state(self, key: str, data: dict) -> None:
        """Write state data to file."""
        state_file = self.state_dir / f"{key}.json"
        state_file.write_text(json.dumps(data, indent=2))

    def read_state(self, key: str) -> Optional[dict]:
        """Read state data from file."""
        state_file = self.state_dir / f"{key}.json"
        if state_file.exists():
            return json.loads(state_file.read_text())
        return None

    def list_states(self) -> List[str]:
        """List all available state keys."""
        return [f.stem for f in self.state_dir.glob("*.json")]
```

### Processing State Model
```python
class ProcessingState(T2DBaseModel):
    """Tracks the state of recipe processing."""

    recipe_path: Path
    started_at: datetime
    completed_at: Optional[datetime] = None

    # Track what's been processed
    diagrams_completed: List[str] = Field(default_factory=list)
    content_files_created: List[Path] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)

    # Current phase
    phase: Literal["transforming", "generating", "documenting", "complete", "error"] = "transforming"

    def add_completed_diagram(self, diagram_id: str) -> None:
        """Mark a diagram as completed."""
        if diagram_id not in self.diagrams_completed:
            self.diagrams_completed.append(diagram_id)

    def add_content_file(self, file_path: Path) -> None:
        """Track a created content file."""
        if file_path not in self.content_files_created:
            self.content_files_created.append(file_path)

    def add_error(self, error: str) -> None:
        """Record an error."""
        self.errors.append(error)
        self.phase = "error"

    def complete(self) -> None:
        """Mark processing as complete."""
        self.completed_at = datetime.utcnow()
        self.phase = "complete"
```

### Agent Coordination Models
```python
class DiagramGenerationState(T2DBaseModel):
    """State for diagram generation agents."""

    diagram_id: str
    framework: DiagramFramework
    status: Literal["pending", "generating", "complete", "failed"] = "pending"
    output_files: List[Path] = Field(default_factory=list)
    error_message: Optional[str] = None

    def mark_complete(self, files: List[Path]) -> None:
        """Mark generation as complete with output files."""
        self.status = "complete"
        self.output_files = files

    def mark_failed(self, error: str) -> None:
        """Mark generation as failed."""
        self.status = "failed"
        self.error_message = error

class ContentGenerationState(T2DBaseModel):
    """State for content generation agents."""

    content_type: Literal["documentation", "presentation"]
    status: Literal["waiting", "gathering", "generating", "complete", "failed"] = "waiting"
    diagrams_found: List[Path] = Field(default_factory=list)
    output_path: Optional[Path] = None
    error_message: Optional[str] = None

    def add_diagram(self, path: Path) -> None:
        """Add a discovered diagram."""
        if path not in self.diagrams_found:
            self.diagrams_found.append(path)
```

### State File Examples

Example `.t2d-state/processing.json`:
```json
{
  "recipe_path": "recipe.t2d.yaml",
  "started_at": "2025-01-17T10:00:00Z",
  "completed_at": null,
  "diagrams_completed": ["architecture-c4", "database-erd"],
  "content_files_created": ["docs/architecture.md", "docs/database.md"],
  "errors": [],
  "phase": "generating"
}
```

Example `.t2d-state/diagram-architecture-c4.json`:
```json
{
  "diagram_id": "architecture-c4",
  "framework": "d2",
  "status": "complete",
  "output_files": ["diagrams/architecture-c4.d2", "diagrams/architecture-c4.svg"],
  "error_message": null
}
```

This file-based approach allows agents to:
- Work independently without direct communication
- Check progress by reading state files
- Coordinate through simple filesystem operations
- Recover from failures by examining state
- Run in parallel without conflicts

Make sure to add the necessary imports at the top of the file (json, datetime, etc.).

## Expanded Diagram Type System

### Comprehensive DiagramType Enum

```python
class DiagramType(str, Enum):
    """Comprehensive diagram types supporting all major frameworks."""

    # Core Mermaid types
    FLOWCHART = "flowchart"
    SEQUENCE = "sequence"
    CLASS = "class"
    STATE = "state"
    ERD = "erd"
    JOURNEY = "journey"
    GANTT = "gantt"
    PIE = "pie"
    QUADRANT = "quadrant"
    REQUIREMENT = "requirement"
    GITGRAPH = "gitgraph"
    MINDMAP = "mindmap"
    TIMELINE = "timeline"
    SANKEY = "sankey"
    XY_CHART = "xy_chart"
    BLOCK = "block"
    PACKET = "packet"
    ARCHITECTURE = "architecture"
    KANBAN = "kanban"

    # C4 diagrams (can be done in Mermaid or D2)
    C4_CONTEXT = "c4_context"
    C4_CONTAINER = "c4_container"
    C4_COMPONENT = "c4_component"
    C4_DEPLOYMENT = "c4_deployment"
    C4_LANDSCAPE = "c4_landscape"

    # PlantUML specific
    PLANTUML_USECASE = "plantuml_usecase"
    PLANTUML_ACTIVITY = "plantuml_activity"
    PLANTUML_COMPONENT = "plantuml_component"
    PLANTUML_DEPLOYMENT = "plantuml_deployment"
    PLANTUML_OBJECT = "plantuml_object"
    PLANTUML_PACKAGE = "plantuml_package"
    PLANTUML_PROFILE = "plantuml_profile"
    PLANTUML_COMPOSITE = "plantuml_composite"
    PLANTUML_COMMUNICATION = "plantuml_communication"
    PLANTUML_INTERACTION = "plantuml_interaction"
    PLANTUML_TIMING = "plantuml_timing"
    PLANTUML_ARCHIMATE = "plantuml_archimate"
    PLANTUML_SPECIFICATION = "plantuml_specification"
    PLANTUML_DITAA = "plantuml_ditaa"
    PLANTUML_DOT = "plantuml_dot"
    PLANTUML_SALT = "plantuml_salt"
    PLANTUML_JSON = "plantuml_json"
    PLANTUML_YAML = "plantuml_yaml"
    PLANTUML_NETWORK = "plantuml_network"
    PLANTUML_WIREFRAME = "plantuml_wireframe"

    # Generic/Unknown
    UNKNOWN = "unknown"


class DiagramFramework(str, Enum):
    """Supported diagram rendering frameworks."""
    MERMAID = "mermaid"
    D2 = "d2"
    PLANTUML = "plantuml"
    GRAPHVIZ = "graphviz"
    AUTO = "auto"
```

### Diagram Type Framework Mapping

```python
DIAGRAM_TYPE_MAPPING = {
    # Mermaid-native types
    DiagramType.FLOWCHART: DiagramFramework.MERMAID,
    DiagramType.SEQUENCE: DiagramFramework.MERMAID,
    DiagramType.CLASS: DiagramFramework.MERMAID,
    DiagramType.STATE: DiagramFramework.MERMAID,
    DiagramType.ERD: DiagramFramework.MERMAID,
    DiagramType.JOURNEY: DiagramFramework.MERMAID,
    DiagramType.GANTT: DiagramFramework.MERMAID,
    DiagramType.PIE: DiagramFramework.MERMAID,
    DiagramType.QUADRANT: DiagramFramework.MERMAID,
    DiagramType.REQUIREMENT: DiagramFramework.MERMAID,
    DiagramType.GITGRAPH: DiagramFramework.MERMAID,
    DiagramType.MINDMAP: DiagramFramework.MERMAID,
    DiagramType.TIMELINE: DiagramFramework.MERMAID,
    DiagramType.SANKEY: DiagramFramework.MERMAID,
    DiagramType.XY_CHART: DiagramFramework.MERMAID,
    DiagramType.BLOCK: DiagramFramework.MERMAID,
    DiagramType.PACKET: DiagramFramework.MERMAID,
    DiagramType.ARCHITECTURE: DiagramFramework.MERMAID,
    DiagramType.KANBAN: DiagramFramework.MERMAID,

    # C4 diagrams - prefer D2 for better layout
    DiagramType.C4_CONTEXT: DiagramFramework.D2,
    DiagramType.C4_CONTAINER: DiagramFramework.D2,
    DiagramType.C4_COMPONENT: DiagramFramework.D2,
    DiagramType.C4_DEPLOYMENT: DiagramFramework.D2,
    DiagramType.C4_LANDSCAPE: DiagramFramework.D2,

    # PlantUML-specific types
    DiagramType.PLANTUML_USECASE: DiagramFramework.PLANTUML,
    DiagramType.PLANTUML_ACTIVITY: DiagramFramework.PLANTUML,
    DiagramType.PLANTUML_COMPONENT: DiagramFramework.PLANTUML,
    DiagramType.PLANTUML_DEPLOYMENT: DiagramFramework.PLANTUML,
    DiagramType.PLANTUML_OBJECT: DiagramFramework.PLANTUML,
    DiagramType.PLANTUML_PACKAGE: DiagramFramework.PLANTUML,
    DiagramType.PLANTUML_PROFILE: DiagramFramework.PLANTUML,
    DiagramType.PLANTUML_COMPOSITE: DiagramFramework.PLANTUML,
    DiagramType.PLANTUML_COMMUNICATION: DiagramFramework.PLANTUML,
    DiagramType.PLANTUML_INTERACTION: DiagramFramework.PLANTUML,
    DiagramType.PLANTUML_TIMING: DiagramFramework.PLANTUML,
    DiagramType.PLANTUML_ARCHIMATE: DiagramFramework.PLANTUML,
    DiagramType.PLANTUML_SPECIFICATION: DiagramFramework.PLANTUML,
    DiagramType.PLANTUML_DITAA: DiagramFramework.PLANTUML,
    DiagramType.PLANTUML_DOT: DiagramFramework.PLANTUML,
    DiagramType.PLANTUML_SALT: DiagramFramework.PLANTUML,
    DiagramType.PLANTUML_JSON: DiagramFramework.PLANTUML,
    DiagramType.PLANTUML_YAML: DiagramFramework.PLANTUML,
    DiagramType.PLANTUML_NETWORK: DiagramFramework.PLANTUML,
    DiagramType.PLANTUML_WIREFRAME: DiagramFramework.PLANTUML,

    # Default fallback
    DiagramType.UNKNOWN: DiagramFramework.MERMAID,
}
```

### Natural Language to Diagram Type Inference

```python
def infer_diagram_type(description: str) -> DiagramType:
    """Infer diagram type from natural language description."""
    description_lower = description.lower()

    # Check for specific keywords
    keyword_mapping = {
        # Mermaid types
        ("flow", "flowchart", "process flow", "workflow"): DiagramType.FLOWCHART,
        ("sequence", "interaction", "message flow"): DiagramType.SEQUENCE,
        ("class", "object model", "class diagram"): DiagramType.CLASS,
        ("state", "state machine", "fsm", "finite state"): DiagramType.STATE,
        ("erd", "entity relationship", "database", "schema", "table"): DiagramType.ERD,
        ("journey", "user journey", "customer journey"): DiagramType.JOURNEY,
        ("gantt", "timeline", "project plan", "schedule"): DiagramType.GANTT,
        ("pie", "pie chart", "distribution"): DiagramType.PIE,
        ("quadrant", "matrix", "2x2"): DiagramType.QUADRANT,
        ("requirement", "requirements", "req"): DiagramType.REQUIREMENT,
        ("git", "gitgraph", "branch", "commit history"): DiagramType.GITGRAPH,
        ("mindmap", "mind map", "brainstorm"): DiagramType.MINDMAP,
        ("timeline", "chronology", "history"): DiagramType.TIMELINE,
        ("sankey", "flow diagram"): DiagramType.SANKEY,
        ("xy", "chart", "graph", "plot"): DiagramType.XY_CHART,
        ("block", "block diagram"): DiagramType.BLOCK,
        ("packet", "network packet"): DiagramType.PACKET,
        ("architecture", "system design"): DiagramType.ARCHITECTURE,
        ("kanban", "board", "task board"): DiagramType.KANBAN,

        # C4 types
        ("c4 context", "system context"): DiagramType.C4_CONTEXT,
        ("c4 container", "container diagram"): DiagramType.C4_CONTAINER,
        ("c4 component", "component diagram"): DiagramType.C4_COMPONENT,
        ("c4 deployment", "deployment"): DiagramType.C4_DEPLOYMENT,
        ("c4 landscape", "landscape"): DiagramType.C4_LANDSCAPE,

        # PlantUML types
        ("use case", "usecase", "actor"): DiagramType.PLANTUML_USECASE,
        ("activity", "activity diagram"): DiagramType.PLANTUML_ACTIVITY,
        ("wireframe", "ui mockup"): DiagramType.PLANTUML_WIREFRAME,
        ("network", "network diagram"): DiagramType.PLANTUML_NETWORK,
    }

    for keywords, diagram_type in keyword_mapping.items():
        if any(keyword in description_lower for keyword in keywords):
            return diagram_type

    return DiagramType.UNKNOWN


def get_framework_for_type(diagram_type: DiagramType,
                          preference: Optional[DiagramFramework] = None) -> DiagramFramework:
    """Get the appropriate framework for a diagram type, with optional user preference."""
    if preference and preference != DiagramFramework.AUTO:
        # Validate that the preference can handle the diagram type
        if can_framework_handle_type(preference, diagram_type):
            return preference
        else:
            # Log warning and fall back to default
            print(f"Warning: {preference} cannot handle {diagram_type}, using default")

    return DIAGRAM_TYPE_MAPPING.get(diagram_type, DiagramFramework.MERMAID)


def can_framework_handle_type(framework: DiagramFramework, diagram_type: DiagramType) -> bool:
    """Check if a framework can handle a specific diagram type."""
    framework_capabilities = {
        DiagramFramework.MERMAID: {
            DiagramType.FLOWCHART, DiagramType.SEQUENCE, DiagramType.CLASS,
            DiagramType.STATE, DiagramType.ERD, DiagramType.JOURNEY,
            DiagramType.GANTT, DiagramType.PIE, DiagramType.QUADRANT,
            DiagramType.REQUIREMENT, DiagramType.GITGRAPH, DiagramType.MINDMAP,
            DiagramType.TIMELINE, DiagramType.SANKEY, DiagramType.XY_CHART,
            DiagramType.BLOCK, DiagramType.PACKET, DiagramType.ARCHITECTURE,
            DiagramType.KANBAN, DiagramType.C4_CONTEXT, DiagramType.C4_CONTAINER
        },
        DiagramFramework.D2: {
            DiagramType.ARCHITECTURE, DiagramType.C4_CONTEXT, DiagramType.C4_CONTAINER,
            DiagramType.C4_COMPONENT, DiagramType.C4_DEPLOYMENT, DiagramType.C4_LANDSCAPE,
            DiagramType.FLOWCHART, DiagramType.SEQUENCE
        },
        DiagramFramework.PLANTUML: {
            DiagramType.SEQUENCE, DiagramType.CLASS, DiagramType.STATE,
            DiagramType.C4_CONTEXT, DiagramType.C4_CONTAINER, DiagramType.C4_COMPONENT,
            DiagramType.PLANTUML_USECASE, DiagramType.PLANTUML_ACTIVITY,
            DiagramType.PLANTUML_COMPONENT, DiagramType.PLANTUML_DEPLOYMENT,
            DiagramType.PLANTUML_OBJECT, DiagramType.PLANTUML_PACKAGE,
            DiagramType.PLANTUML_PROFILE, DiagramType.PLANTUML_COMPOSITE,
            DiagramType.PLANTUML_COMMUNICATION, DiagramType.PLANTUML_INTERACTION,
            DiagramType.PLANTUML_TIMING, DiagramType.PLANTUML_ARCHIMATE,
            DiagramType.PLANTUML_SPECIFICATION, DiagramType.PLANTUML_DITAA,
            DiagramType.PLANTUML_DOT, DiagramType.PLANTUML_SALT,
            DiagramType.PLANTUML_JSON, DiagramType.PLANTUML_YAML,
            DiagramType.PLANTUML_NETWORK, DiagramType.PLANTUML_WIREFRAME
        },
        DiagramFramework.GRAPHVIZ: {
            DiagramType.FLOWCHART, DiagramType.ARCHITECTURE
        }
    }

    return diagram_type in framework_capabilities.get(framework, set())


def get_diagram_type_examples() -> Dict[DiagramType, str]:
    """Get example descriptions for each diagram type."""
    return {
        # Mermaid examples
        DiagramType.FLOWCHART: "Process flow for user registration with decision points",
        DiagramType.SEQUENCE: "API interaction sequence between frontend, backend, and database",
        DiagramType.CLASS: "Object-oriented model of the core domain entities",
        DiagramType.STATE: "User authentication state machine with transitions",
        DiagramType.ERD: "Database schema showing table relationships and constraints",
        DiagramType.JOURNEY: "Customer journey from discovery to purchase completion",
        DiagramType.GANTT: "Project timeline with milestones and dependencies",
        DiagramType.PIE: "Distribution of system resource usage by component",
        DiagramType.QUADRANT: "Technology evaluation matrix by complexity vs value",
        DiagramType.REQUIREMENT: "Requirements traceability from business needs to implementation",
        DiagramType.GITGRAPH: "Git branching strategy and merge workflow",
        DiagramType.MINDMAP: "Architecture decision brainstorming and considerations",
        DiagramType.TIMELINE: "System evolution milestones and major releases",
        DiagramType.SANKEY: "Data flow through system components with volumes",
        DiagramType.XY_CHART: "Performance metrics over time with trend analysis",
        DiagramType.BLOCK: "High-level system block diagram with interfaces",
        DiagramType.PACKET: "Network packet structure and protocol analysis",
        DiagramType.ARCHITECTURE: "Microservices architecture with communication patterns",
        DiagramType.KANBAN: "Development workflow board with status tracking",

        # C4 examples
        DiagramType.C4_CONTEXT: "System context showing external users and systems",
        DiagramType.C4_CONTAINER: "Container view of microservices and databases",
        DiagramType.C4_COMPONENT: "Component breakdown within a specific service",
        DiagramType.C4_DEPLOYMENT: "Production deployment topology and infrastructure",
        DiagramType.C4_LANDSCAPE: "Enterprise architecture landscape view",

        # PlantUML examples
        DiagramType.PLANTUML_USECASE: "Actor interactions with system use cases",
        DiagramType.PLANTUML_ACTIVITY: "Business process workflow with swim lanes",
        DiagramType.PLANTUML_WIREFRAME: "User interface mockup with interaction elements",
        DiagramType.PLANTUML_NETWORK: "Network topology with devices and connections"
    }
```

### Enhanced DiagramSpecification Model

```python
class EnhancedDiagramSpecification(DiagramSpecification):
    """Enhanced diagram specification with intelligent framework selection."""

    @model_validator(mode='after')
    def validate_and_set_framework(self) -> 'EnhancedDiagramSpecification':
        """Automatically set framework based on diagram type if not specified."""
        if not self.framework:
            self.framework = get_framework_for_type(self.type)
        else:
            # Validate user-specified framework can handle the diagram type
            if not can_framework_handle_type(self.framework, self.type):
                raise ValueError(
                    f"Framework {self.framework.value} cannot handle diagram type {self.type.value}. "
                    f"Recommended framework: {get_framework_for_type(self.type).value}"
                )
        return self

    @classmethod
    def from_description(cls, description: str, **kwargs) -> 'EnhancedDiagramSpecification':
        """Create diagram specification from natural language description."""
        inferred_type = infer_diagram_type(description)
        recommended_framework = get_framework_for_type(inferred_type)

        return cls(
            type=inferred_type,
            framework=recommended_framework,
            title=description.title(),
            instructions=f"Create a {inferred_type.value} diagram based on: {description}",
            **kwargs
        )

    def get_framework_specific_options(self) -> Dict[str, Any]:
        """Get framework-specific rendering options."""
        framework_options = {
            DiagramFramework.MERMAID: {
                "theme": "default",
                "fontFamily": "arial",
                "fontSize": 16,
                "primaryColor": "#ff6b6b",
                "primaryTextColor": "#333"
            },
            DiagramFramework.D2: {
                "theme": "neutral-default",
                "layout": "dagre",
                "sketch": False,
                "pad": 100
            },
            DiagramFramework.PLANTUML: {
                "skin": "rose",
                "monochrome": False,
                "handwritten": False,
                "scale": 1.0
            }
        }

        return framework_options.get(self.framework, {})

    def get_suggested_output_formats(self) -> List[OutputFormat]:
        """Get recommended output formats for this diagram type."""
        # High-detail diagrams benefit from vector formats
        vector_preferred = {
            DiagramType.ARCHITECTURE, DiagramType.C4_CONTEXT,
            DiagramType.C4_CONTAINER, DiagramType.C4_COMPONENT,
            DiagramType.ERD, DiagramType.CLASS
        }

        # Interactive diagrams work well as SVG
        interactive_types = {
            DiagramType.MINDMAP, DiagramType.KANBAN,
            DiagramType.JOURNEY, DiagramType.SANKEY
        }

        if self.type in vector_preferred:
            return [OutputFormat.SVG, OutputFormat.PDF]
        elif self.type in interactive_types:
            return [OutputFormat.SVG]
        else:
            return [OutputFormat.SVG, OutputFormat.PNG]
```

### Usage Examples

```python
# Example 1: Automatic type inference
spec1 = EnhancedDiagramSpecification.from_description(
    "User registration process flow with validation steps",
    id="user-registration",
    output_file="diagrams/user-registration.mmd"
)
# Results in: type=FLOWCHART, framework=MERMAID

# Example 2: C4 architecture diagram
spec2 = EnhancedDiagramSpecification(
    id="system-context",
    type=DiagramType.C4_CONTEXT,
    title="E-commerce System Context",
    instructions="Show the e-commerce system with external users and integrations",
    output_file="diagrams/context.d2",
    output_formats=[OutputFormat.SVG, OutputFormat.PDF]
)
# Automatically sets framework=D2

# Example 3: PlantUML use case diagram
spec3 = EnhancedDiagramSpecification(
    id="user-workflows",
    type=DiagramType.PLANTUML_USECASE,
    framework=DiagramFramework.PLANTUML,
    title="User Workflow Use Cases",
    instructions="Model the key user interactions with the system",
    output_file="diagrams/use-cases.puml",
    output_formats=[OutputFormat.SVG, OutputFormat.PNG]
)

# Example 4: Framework validation
try:
    invalid_spec = EnhancedDiagramSpecification(
        id="invalid",
        type=DiagramType.GANTT,  # Gantt charts only supported by Mermaid
        framework=DiagramFramework.D2,  # D2 doesn't support Gantt
        title="Project Timeline",
        instructions="Show project milestones",
        output_file="timeline.d2"
    )
except ValueError as e:
    print(f"Validation error: {e}")
    # Output: Framework d2 cannot handle diagram type gantt. Recommended framework: mermaid
```

---
*Enhanced data model with Pydantic validation: 2025-01-16*