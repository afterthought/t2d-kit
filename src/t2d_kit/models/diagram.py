"""T018: DiagramSpecification model with framework validation."""

from pathlib import Path
from typing import Any, Union

from pydantic import Field, field_validator, model_validator

from .base import (
    DiagramType,
    FrameworkType,
    InstructionsField,
    NameField,
    OutputFormat,
    PathField,
    T2DBaseModel,
)


class DiagramSpecification(T2DBaseModel):
    """Individual diagram definition with generator agent prompt."""

    id: str = Field(pattern=r"^[a-zA-Z0-9_-]+$", min_length=1, max_length=100)
    type: DiagramType
    framework: FrameworkType | None = None
    agent: str = Field(pattern=r"^t2d-[a-z0-9-]+$")
    title: NameField
    instructions: InstructionsField
    output_file: PathField
    output_formats: list[OutputFormat] = Field(min_length=1)
    options: Union[dict[str, Any], "MermaidConfig", "D2Options", "MarpConfig"] | None = None

    @field_validator("instructions")
    @classmethod
    def validate_instructions_length(cls, v: str) -> str:
        """Ensure instructions are detailed enough."""
        if len(v.split()) < 5:
            raise ValueError("Instructions must be at least 5 words")
        return v

    @field_validator("output_file")
    @classmethod
    def validate_output_file_extension(cls, v: str) -> str:
        """Ensure output file has appropriate extension."""
        path = Path(v)
        valid_extensions = {".d2", ".mmd", ".puml", ".gv", ".md"}
        if path.suffix not in valid_extensions:
            raise ValueError(f"Output file must have extension: {valid_extensions}")
        return v

    @model_validator(mode="after")
    def validate_framework_compatibility(self) -> "DiagramSpecification":
        """Ensure framework supports diagram type and output formats."""
        if not self.framework:
            # Auto-select framework based on diagram type
            self.framework = self._get_default_framework_for_type(self.type)
            return self

        # Framework compatibility matrix
        framework_capabilities: dict[FrameworkType, dict[str, set[Any]]] = {
            FrameworkType.D2: {
                "types": {
                    DiagramType.C4_CONTEXT,
                    DiagramType.C4_CONTAINER,
                    DiagramType.C4_COMPONENT,
                    DiagramType.ARCHITECTURE,
                    DiagramType.FLOWCHART,
                },
                "formats": {OutputFormat.SVG, OutputFormat.PNG, OutputFormat.PDF},
            },
            FrameworkType.MERMAID: {
                "types": {
                    DiagramType.SEQUENCE,
                    DiagramType.FLOWCHART,
                    DiagramType.ERD,
                    DiagramType.GANTT,
                    DiagramType.STATE,
                    DiagramType.CLASS,
                    DiagramType.PIE,
                    DiagramType.JOURNEY,
                    DiagramType.QUADRANT,
                    DiagramType.REQUIREMENT,
                    DiagramType.GITGRAPH,
                    DiagramType.MINDMAP,
                    DiagramType.TIMELINE,
                    DiagramType.SANKEY,
                    DiagramType.XY_CHART,
                    DiagramType.BLOCK,
                    DiagramType.PACKET,
                    DiagramType.ARCHITECTURE,
                    DiagramType.KANBAN,
                    DiagramType.C4_CONTEXT,
                    DiagramType.C4_CONTAINER,
                },
                "formats": {OutputFormat.SVG, OutputFormat.PNG, OutputFormat.PDF},
            },
            FrameworkType.PLANTUML: {
                "types": {
                    DiagramType.SEQUENCE,
                    DiagramType.CLASS,
                    DiagramType.STATE,
                    DiagramType.C4_CONTEXT,
                    DiagramType.C4_CONTAINER,
                    DiagramType.PLANTUML_USECASE,
                    DiagramType.PLANTUML_ACTIVITY,
                    DiagramType.PLANTUML_COMPONENT,
                    DiagramType.PLANTUML_DEPLOYMENT,
                    DiagramType.PLANTUML_OBJECT,
                    DiagramType.PLANTUML_PACKAGE,
                    DiagramType.PLANTUML_WIREFRAME,
                    DiagramType.PLANTUML_NETWORK,
                },
                "formats": {OutputFormat.SVG, OutputFormat.PNG, OutputFormat.PDF},
            },
        }

        if self.framework in framework_capabilities:
            capabilities = framework_capabilities[self.framework]

            # Check diagram type compatibility
            if self.type not in capabilities["types"]:
                raise ValueError(
                    f"Framework {self.framework.value} does not support diagram type {self.type.value}"
                )

            # Check output format compatibility
            unsupported_formats = set(self.output_formats) - capabilities["formats"]
            if unsupported_formats:
                raise ValueError(
                    f"Framework {self.framework.value} does not support formats: {unsupported_formats}"
                )

        return self

    def _get_default_framework_for_type(self, diagram_type: DiagramType) -> FrameworkType:
        """Get default framework for diagram type."""
        type_mapping = {
            # C4 diagrams - prefer D2
            DiagramType.C4_CONTEXT: FrameworkType.D2,
            DiagramType.C4_CONTAINER: FrameworkType.D2,
            DiagramType.C4_COMPONENT: FrameworkType.D2,
            DiagramType.C4_DEPLOYMENT: FrameworkType.D2,
            DiagramType.C4_LANDSCAPE: FrameworkType.D2,
            # Architecture diagrams - prefer D2
            DiagramType.ARCHITECTURE: FrameworkType.D2,
            # Mermaid-native types
            DiagramType.FLOWCHART: FrameworkType.MERMAID,
            DiagramType.SEQUENCE: FrameworkType.MERMAID,
            DiagramType.ERD: FrameworkType.MERMAID,
            DiagramType.GANTT: FrameworkType.MERMAID,
            DiagramType.STATE: FrameworkType.MERMAID,
            DiagramType.CLASS: FrameworkType.MERMAID,
            DiagramType.PIE: FrameworkType.MERMAID,
            DiagramType.JOURNEY: FrameworkType.MERMAID,
            DiagramType.QUADRANT: FrameworkType.MERMAID,
            DiagramType.REQUIREMENT: FrameworkType.MERMAID,
            DiagramType.GITGRAPH: FrameworkType.MERMAID,
            DiagramType.MINDMAP: FrameworkType.MERMAID,
            DiagramType.TIMELINE: FrameworkType.MERMAID,
            DiagramType.SANKEY: FrameworkType.MERMAID,
            DiagramType.XY_CHART: FrameworkType.MERMAID,
            DiagramType.BLOCK: FrameworkType.MERMAID,
            DiagramType.PACKET: FrameworkType.MERMAID,
            DiagramType.KANBAN: FrameworkType.MERMAID,
        }

        # PlantUML types
        plantuml_types = {
            DiagramType.PLANTUML_USECASE,
            DiagramType.PLANTUML_ACTIVITY,
            DiagramType.PLANTUML_COMPONENT,
            DiagramType.PLANTUML_DEPLOYMENT,
            DiagramType.PLANTUML_OBJECT,
            DiagramType.PLANTUML_PACKAGE,
            DiagramType.PLANTUML_PROFILE,
            DiagramType.PLANTUML_COMPOSITE,
            DiagramType.PLANTUML_COMMUNICATION,
            DiagramType.PLANTUML_INTERACTION,
            DiagramType.PLANTUML_TIMING,
            DiagramType.PLANTUML_ARCHIMATE,
            DiagramType.PLANTUML_SPECIFICATION,
            DiagramType.PLANTUML_DITAA,
            DiagramType.PLANTUML_DOT,
            DiagramType.PLANTUML_SALT,
            DiagramType.PLANTUML_JSON,
            DiagramType.PLANTUML_YAML,
            DiagramType.PLANTUML_NETWORK,
            DiagramType.PLANTUML_WIREFRAME,
        }

        if diagram_type in plantuml_types:
            return FrameworkType.PLANTUML

        return type_mapping.get(diagram_type, FrameworkType.MERMAID)


# Import configs here to avoid circular imports
from .d2_options import D2Options
from .marp_config import MarpConfig
from .mermaid_config import MermaidConfig

# Update forward references
DiagramSpecification.model_rebuild()
