"""T2D-Kit Models Package

This package contains all the Pydantic models for the T2D-Kit diagram pipeline.
All models inherit from T2DBaseModel with enhanced validation.
"""

# Base model and common types
from .base import (
    ContentField,
    ContentType,
    DescriptionField,
    DetailLevel,
    DiagramType,
    DocStyle,
    EmailField,
    FrameworkType,
    GenerationStatus,
    IdField,
    InstructionsField,
    NameField,
    NonNegativeIntField,
    OutputFormat,
    PathField,
    PositiveIntField,
    PRDFormat,
    PresentationStyle,
    ScoreField,
    T2DBaseModel,
    UrlField,
    VersionField,
)

# Content models
from .content import (
    ContentFile,
)

# Framework-specific configuration models
from .d2_options import (
    D2Options,
)

# Diagram models
from .diagram import (
    DiagramSpecification,
)
from .diagram_spec import (
    DiagramSpec,
)
from .marp_config import (
    MarpConfig,
    SlideDirective,
)
from .mermaid_config import (
    MermaidConfig,
)
from .mkdocs_config import (
    MkDocsPageConfig,
)

# Processed recipe models
from .processed_recipe import (
    DiagramReference,
    OutputConfig,
    ProcessedRecipe,
)

# State management models
from .state import (
    AgentCoordinationState,
    ContentGenerationState,
    DiagramGenerationState,
    ProcessingState,
    StateManager,
)

# User recipe models
from .user_recipe import (
    DiagramRequest,
    DocumentationInstructions,
    PRDContent,
    Preferences,
    PresentationInstructions,
    UserInstructions,
    UserRecipe,
)

__all__ = [
    # Base model and types
    "T2DBaseModel",
    "IdField",
    "PathField",
    "InstructionsField",
    "NameField",
    "DescriptionField",
    "ContentField",
    "VersionField",
    "EmailField",
    "UrlField",
    "PositiveIntField",
    "NonNegativeIntField",
    "ScoreField",
    "DiagramType",
    "FrameworkType",
    "OutputFormat",
    "ContentType",
    "GenerationStatus",
    "PRDFormat",
    "DocStyle",
    "DetailLevel",
    "PresentationStyle",
    # User recipe models
    "UserRecipe",
    "PRDContent",
    "UserInstructions",
    "DiagramRequest",
    "DocumentationInstructions",
    "PresentationInstructions",
    "Preferences",
    # Processed recipe models
    "ProcessedRecipe",
    "DiagramReference",
    "OutputConfig",
    # Diagram models
    "DiagramSpecification",
    "DiagramSpec",
    # Content models
    "ContentFile",
    # State management models
    "StateManager",
    "ProcessingState",
    "DiagramGenerationState",
    "ContentGenerationState",
    "AgentCoordinationState",
    # Framework-specific configuration models
    "D2Options",
    "MermaidConfig",
    "MkDocsPageConfig",
    "MarpConfig",
    "SlideDirective",
]

# Version information
__version__ = "1.0.0"
