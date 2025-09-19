"""T015: Base model and common type annotations for T2D-Kit models."""

from enum import Enum
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class T2DBaseModel(BaseModel):
    """Base model for all T2D-Kit entities with enhanced validation."""

    model_config = ConfigDict(
        extra="forbid",  # No unexpected fields
        validate_assignment=True,  # Validate on assignment
        str_strip_whitespace=True,  # Auto-strip strings
        frozen=False,  # Allow mutations (most models need this)
        use_enum_values=True,  # Use enum values in JSON
        json_schema_extra={  # Add schema metadata
            "title": "T2D-Kit Models",
            "version": "1.0.0",
            "description": "Enhanced Pydantic models for T2D-Kit diagram pipeline",
        },
    )


# Common type annotations for consistent validation
IdField = Annotated[
    str,
    Field(
        pattern=r"^[a-zA-Z0-9_-]+$",
        min_length=1,
        max_length=100,
        description="Alphanumeric identifier with hyphens and underscores",
    ),
]

PathField = Annotated[str, Field(min_length=1, max_length=500, description="File system path")]

InstructionsField = Annotated[
    str, Field(min_length=10, max_length=10000, description="Detailed instructions for generation")
]

NameField = Annotated[str, Field(min_length=1, max_length=255, description="Human-readable name")]

DescriptionField = Annotated[str, Field(max_length=500, description="Brief description")]

ContentField = Annotated[
    str, Field(max_length=1048576, description="Content text (max 1MB)")  # 1MB
]

VersionField = Annotated[
    str, Field(pattern=r"^\d+\.\d+\.\d+$", description="Semantic version (e.g., 1.0.0)")
]

EmailField = Annotated[
    str,
    Field(
        pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
        description="Valid email address",
    ),
]

UrlField = Annotated[str, Field(pattern=r"^https?://[^\s]+$", description="Valid HTTP/HTTPS URL")]

PositiveIntField = Annotated[int, Field(gt=0, description="Positive integer")]

NonNegativeIntField = Annotated[int, Field(ge=0, description="Non-negative integer")]

ScoreField = Annotated[float, Field(ge=0.0, le=1.0, description="Score between 0.0 and 1.0")]


# Common Enums
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


class FrameworkType(str, Enum):
    """Supported diagram rendering frameworks."""

    MERMAID = "mermaid"
    D2 = "d2"
    PLANTUML = "plantuml"
    GRAPHVIZ = "graphviz"
    AUTO = "auto"


class OutputFormat(str, Enum):
    """Supported output formats for diagrams."""

    SVG = "svg"
    PNG = "png"
    PDF = "pdf"
    INLINE = "inline"


class ContentType(str, Enum):
    """Types of content files."""

    DOCUMENTATION = "documentation"
    PRESENTATION = "presentation"


class GenerationStatus(str, Enum):
    """Status of diagram generation."""

    PENDING = "pending"
    GENERATED = "generated"
    FAILED = "failed"


class PRDFormat(str, Enum):
    """Format of PRD content."""

    MARKDOWN = "markdown"
    TEXT = "text"
    HTML = "html"


class DocStyle(str, Enum):
    """Documentation writing style."""

    TECHNICAL = "technical"  # Developer-focused, technical details
    BUSINESS = "business"  # Business-focused, less technical
    TUTORIAL = "tutorial"  # Step-by-step guide format
    REFERENCE = "reference"  # API/reference documentation


class DetailLevel(str, Enum):
    """Level of detail in documentation."""

    HIGH_LEVEL = "high-level"  # Executive summary level
    DETAILED = "detailed"  # Standard documentation
    COMPREHENSIVE = "comprehensive"  # Include all details


class PresentationStyle(str, Enum):
    """Style of presentation."""

    EXECUTIVE = "executive"  # High-level for executives
    TECHNICAL = "technical"  # Technical deep-dive
    SALES = "sales"  # Sales/marketing focus
    WORKSHOP = "workshop"  # Interactive workshop format
