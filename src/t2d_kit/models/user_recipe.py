"""T016: UserRecipe model with enhanced validation."""

import re
from datetime import UTC, datetime, timezone
from pathlib import Path
from typing import Any

from pydantic import Field, field_validator, model_validator

from .base import (
    ContentField,
    DescriptionField,
    DetailLevel,
    DocStyle,
    NameField,
    PathField,
    PRDFormat,
    PresentationStyle,
    T2DBaseModel,
    VersionField,
)


class DiagramRequest(T2DBaseModel):
    """User's high-level diagram request."""

    type: str = Field(min_length=1, max_length=100)
    description: DescriptionField | None = None
    framework_preference: str | None = None

    @field_validator("type")
    @classmethod
    def validate_type_format(cls, v: str) -> str:
        """Normalize diagram type format."""
        normalized = v.lower().replace(" ", "_")
        if not re.match(r"^[a-z][a-z0-9_]*$", normalized):
            raise ValueError("Diagram type must be alphanumeric with underscores")
        return normalized

    @field_validator("framework_preference")
    @classmethod
    def validate_framework_preference(cls, v: str | None) -> str | None:
        """Validate framework preference against known frameworks."""
        if v is None:
            return v
        valid_frameworks = {"d2", "mermaid", "plantuml", "graphviz", "auto"}
        if v.lower() not in valid_frameworks:
            raise ValueError(f"Framework must be one of: {valid_frameworks}")
        return v.lower()


class DocumentationInstructions(T2DBaseModel):
    """Guidance for markdown content generation."""

    style: DocStyle | None = DocStyle.TECHNICAL
    audience: str | None = Field(None, max_length=255)
    sections: list[str] | None = None
    detail_level: DetailLevel | None = DetailLevel.DETAILED
    include_code_examples: bool = False
    include_diagrams_inline: bool = True

    @field_validator("sections")
    @classmethod
    def validate_sections_format(cls, v: list[str] | None) -> list[str] | None:
        """Validate section names."""
        if v is None:
            return v
        for section in v:
            if len(section.strip()) == 0:
                raise ValueError("Section names cannot be empty")
        return [s.strip() for s in v]


class PresentationInstructions(T2DBaseModel):
    """Guidance for slide generation."""

    audience: str | None = Field(None, max_length=255)
    max_slides: int | None = Field(None, ge=5, le=100)
    style: PresentationStyle | None = PresentationStyle.TECHNICAL
    include_speaker_notes: bool = True
    emphasis_points: list[str] | None = None
    time_limit: int | None = Field(
        None, gt=0, description="Target presentation duration in minutes"
    )


class UserInstructions(T2DBaseModel):
    """High-level instructions for what to generate."""

    diagrams: list[DiagramRequest] = Field(min_length=1)
    documentation: DocumentationInstructions | None = None
    presentation: PresentationInstructions | None = None
    focus_areas: list[str] | None = None
    exclude: list[str] | None = None

    @field_validator("diagrams")
    @classmethod
    def validate_diagram_uniqueness(cls, v: list[DiagramRequest]) -> list[DiagramRequest]:
        """Ensure diagram types are not duplicated."""
        seen_types = set()
        for diagram in v:
            key = f"{diagram.type}_{diagram.description or ''}"
            if key in seen_types:
                raise ValueError(f"Duplicate diagram request: {diagram.type}")
            seen_types.add(key)
        return v


class PRDContent(T2DBaseModel):
    """Product Requirements Document content or reference."""

    content: ContentField | None = None
    file_path: PathField | None = None
    format: PRDFormat | None = PRDFormat.MARKDOWN
    sections: list[str] | None = None

    @field_validator("sections")
    @classmethod
    def validate_sections_format(cls, v: list[str] | None) -> list[str] | None:
        """Validate section names."""
        if v is None:
            return v
        for section in v:
            if len(section.strip()) == 0:
                raise ValueError("Section names cannot be empty")
        return [s.strip() for s in v]

    @field_validator("file_path")
    @classmethod
    def validate_file_path_exists(cls, v: str | None) -> str | None:
        """Validate file path format and basic structure."""
        if v is None:
            return v
        if ".." in v:
            raise ValueError("Path traversal not allowed")
        path = Path(v)
        if not path.suffix:
            raise ValueError("File path must have an extension")
        return v

    @model_validator(mode="after")
    def validate_content_source(self) -> "PRDContent":
        """Ensure exactly one content source is provided."""
        has_content = self.content is not None
        has_file = self.file_path is not None

        if not has_content and not has_file:
            raise ValueError("Must provide either content or file_path")
        if has_content and has_file:
            raise ValueError("Cannot provide both content and file_path")
        return self


class Preferences(T2DBaseModel):
    """User preferences for generation."""

    default_framework: str | None = None
    diagram_style: str | None = None
    color_scheme: str | None = None
    theme: str | None = None
    custom_templates: dict[str, str] | None = None


class UserRecipe(T2DBaseModel):
    """User-maintained recipe with PRD content and high-level instructions."""

    name: NameField
    version: VersionField = "1.0.0"
    prd: PRDContent
    instructions: UserInstructions
    preferences: Preferences | None = None
    metadata: dict[str, Any] | None = None

    @field_validator("name")
    @classmethod
    def validate_name_format(cls, v: str) -> str:
        """Ensure name follows project naming conventions."""
        if not re.match(r"^[a-zA-Z][a-zA-Z0-9_-]*$", v):
            raise ValueError(
                "Name must start with letter and contain only alphanumeric, hyphens, underscores"
            )
        return v

    @model_validator(mode="after")
    def validate_recipe_completeness(self) -> "UserRecipe":
        """Ensure recipe has minimum required content."""
        if not self.instructions.diagrams:
            raise ValueError("Recipe must specify at least one diagram type")
        return self


# MCP Tool Parameter Models
from typing import Annotated, Dict, List, Optional


class CreateRecipeParams(T2DBaseModel):
    """Parameters for create_user_recipe MCP tool."""

    name: Annotated[str, Field(
        pattern=r"^[a-zA-Z][a-zA-Z0-9_-]*$",
        min_length=1,
        max_length=100,
        description="Recipe name (used as filename)"
    )]
    prd_content: Annotated[str | None, Field(
        None,
        max_length=1048576,
        description="PRD content to embed in recipe (max 1MB)"
    )]
    prd_file_path: Annotated[str | None, Field(
        None,
        description="Path to external PRD file (alternative to prd_content)"
    )]
    diagrams: Annotated[list[DiagramRequest], Field(
        min_length=1,
        description="List of diagram specifications"
    )]
    documentation_config: Annotated[DocumentationInstructions | None, Field(
        None,
        description="Optional documentation generation settings"
    )]
    output_dir: Annotated[str, Field(
        "./recipes",
        description="Directory to save the recipe file"
    )]

    @model_validator(mode="after")
    def validate_prd_source(self) -> "CreateRecipeParams":
        """Ensure exactly one PRD source."""
        if not self.prd_content and not self.prd_file_path:
            raise ValueError("Must provide either prd_content or prd_file_path")
        if self.prd_content and self.prd_file_path:
            raise ValueError("Cannot provide both prd_content and prd_file_path")
        return self


class EditRecipeParams(T2DBaseModel):
    """Parameters for edit_user_recipe MCP tool."""

    name: Annotated[str, Field(description="Recipe name to edit")]
    prd_content: Annotated[str | None, Field(None, description="New PRD content")]
    prd_file_path: Annotated[str | None, Field(None, description="New PRD file path")]
    diagrams: Annotated[list[DiagramRequest] | None, Field(None, description="New diagram specifications")]
    documentation_config: Annotated[DocumentationInstructions | None, Field(None, description="New documentation settings")]
    validate_before_save: Annotated[bool, Field(True, description="Validate recipe before saving")]


class ValidateRecipeParams(T2DBaseModel):
    """Parameters for validate_user_recipe MCP tool."""

    name: Annotated[str | None, Field(None, description="Recipe name to validate from filesystem")]
    content: Annotated[UserRecipe | None, Field(None, description="Recipe content to validate directly")]

    @model_validator(mode="after")
    def validate_params(self) -> "ValidateRecipeParams":
        """Ensure at least one is provided."""
        if not self.name and not self.content:
            raise ValueError("Must provide either name or content to validate")
        return self


class DeleteRecipeParams(T2DBaseModel):
    """Parameters for delete_user_recipe MCP tool."""

    name: Annotated[str, Field(description="Recipe name to delete")]
    confirm: Annotated[bool, Field(
        False,
        description="Confirmation flag (must be true to delete)"
    )]


# Response Models for MCP

class MCPValidationError(T2DBaseModel):
    """Validation error detail for MCP responses."""

    field: str = Field(..., description="Field path that failed validation")
    message: str = Field(..., description="Error message")
    error_type: str = Field(..., description="Error category")
    suggestion: str | None = Field(None, description="How to fix the error")


class MCPValidationResult(T2DBaseModel):
    """Result of recipe validation for MCP."""

    valid: bool
    errors: list[MCPValidationError] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    validated_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat().replace("+00:00", "Z"))
    duration_ms: float = Field(..., ge=0, description="Validation duration in milliseconds")


class CreateRecipeResponse(T2DBaseModel):
    """Response after creating a recipe."""

    success: bool
    recipe_name: str
    file_path: str
    validation_result: MCPValidationResult
    message: str


class EditRecipeResponse(T2DBaseModel):
    """Response after editing a recipe."""

    success: bool
    recipe_name: str
    file_path: str
    changes_applied: dict[str, Any]
    validation_result: MCPValidationResult | None = None
    message: str


class DeleteRecipeResponse(T2DBaseModel):
    """Response after deleting a recipe."""

    success: bool
    recipe_name: str
    file_path: str
    message: str
