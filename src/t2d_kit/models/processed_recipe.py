"""T017: ProcessedRecipe model with cross-field validation."""

from datetime import UTC, datetime, timezone
from typing import Any

from pydantic import Field, field_validator, model_validator

from .base import (
    DiagramType,
    NameField,
    OutputFormat,
    PathField,
    T2DBaseModel,
    VersionField,
)


class DiagramReference(T2DBaseModel):
    """Metadata about diagrams that will be available to content agents."""

    id: str = Field(min_length=1, max_length=100)
    title: NameField
    type: DiagramType
    expected_path: PathField
    actual_paths: dict[OutputFormat, str] | None = None
    description: str | None = Field(None, max_length=500)
    status: str = "pending"  # pending, generated, failed

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        """Validate generation status."""
        valid_statuses = {"pending", "generated", "failed"}
        if v not in valid_statuses:
            raise ValueError(f"Status must be one of: {valid_statuses}")
        return v


class OutputConfig(T2DBaseModel):
    """Configuration for output generation."""

    assets_dir: PathField = "docs/assets"
    mkdocs: dict[str, Any] | None = None
    marp: dict[str, Any] | None = None


class ProcessedRecipe(T2DBaseModel):
    """Agent-generated recipe with detailed specifications."""

    name: NameField
    version: VersionField
    source_recipe: PathField
    generated_at: datetime | str
    content_files: list["ContentFile"] = Field(min_length=1)
    diagram_specs: list["DiagramSpecification"] = Field(min_length=1)
    diagram_refs: list[DiagramReference] = Field(min_length=1)
    outputs: OutputConfig
    generation_notes: list[str] | None = None

    @field_validator("generated_at")
    @classmethod
    def validate_generation_time(cls, v: datetime | str) -> datetime:
        """Ensure generation time is not in the future."""
        # Convert string to datetime if needed
        if isinstance(v, str):
            from datetime import timezone as tz
            try:
                # Handle ISO format with Z suffix
                if v.endswith("Z"):
                    v = v[:-1] + "+00:00"
                v = datetime.fromisoformat(v)
            except (ValueError, TypeError) as e:
                raise ValueError(f"Invalid datetime format: {v}") from e

        # Ensure both datetimes have timezone info for comparison
        if v.tzinfo is None:
            # If input is naive, assume UTC
            v = v.replace(tzinfo=UTC)

        # Compare with current time in the same timezone
        now = datetime.now(v.tzinfo)
        if v > now:
            raise ValueError("Generation time cannot be in the future")
        return v

    @model_validator(mode="after")
    def validate_diagram_consistency(self) -> "ProcessedRecipe":
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

    @model_validator(mode="after")
    def validate_content_diagram_refs(self) -> "ProcessedRecipe":
        """Ensure content files reference valid diagrams."""
        valid_diagram_ids = {spec.id for spec in self.diagram_specs}

        for content_file in self.content_files:
            invalid_refs = set(content_file.diagram_refs) - valid_diagram_ids
            if invalid_refs:
                raise ValueError(
                    f"Content file '{content_file.path}' references invalid diagrams: {invalid_refs}"
                )

        return self


# Import here to avoid circular imports
from .content import ContentFile
from .diagram import DiagramSpecification

# Update forward references
ProcessedRecipe.model_rebuild()


# MCP Tool Parameter Models for Processed Recipes
from typing import Annotated, List, Optional


class ProcessedRecipeContent(ProcessedRecipe):
    """Complete processed recipe structure for MCP tools.

    This is an alias for ProcessedRecipe to match the MCP contracts.
    """
    pass


class WriteProcessedRecipeParams(T2DBaseModel):
    """Parameters for write_processed_recipe MCP tool."""

    recipe_path: Annotated[str, Field(
        description="Path to save the processed recipe (usually recipe.t2d.yaml)"
    )]
    content: Annotated[ProcessedRecipeContent, Field(
        description="Complete processed recipe content"
    )]
    should_validate: Annotated[bool, Field(
        True,
        description="Validate before writing"
    )]


class UpdateProcessedRecipeParams(T2DBaseModel):
    """Parameters for update_processed_recipe MCP tool."""

    recipe_path: Annotated[str, Field(
        description="Path to the processed recipe file to update"
    )]
    diagram_specs: Annotated[list["DiagramSpecification"] | None, Field(
        None,
        description="Updated diagram specifications"
    )]
    content_files: Annotated[list["ContentFile"] | None, Field(
        None,
        description="Updated content file specifications"
    )]
    diagram_refs: Annotated[list[DiagramReference] | None, Field(
        None,
        description="Updated diagram references"
    )]
    outputs: Annotated[OutputConfig | None, Field(
        None,
        description="Updated output configuration"
    )]
    generation_notes: Annotated[list[str] | None, Field(
        None,
        description="Additional generation notes"
    )]
    should_validate: Annotated[bool, Field(
        True,
        description="Validate after update"
    )]


class ValidateProcessedRecipeParams(T2DBaseModel):
    """Parameters for validate_processed_recipe MCP tool."""

    recipe_path: Annotated[str | None, Field(
        None,
        description="Path to processed recipe file to validate"
    )]
    content: Annotated[ProcessedRecipeContent | None, Field(
        None,
        description="Processed recipe content to validate directly"
    )]

    @model_validator(mode="after")
    def validate_params(self) -> "ValidateProcessedRecipeParams":
        """Ensure at least one is provided."""
        if not self.recipe_path and not self.content:
            raise ValueError("Must provide either recipe_path or content to validate")
        return self


class WriteProcessedRecipeResponse(T2DBaseModel):
    """Response after writing a processed recipe."""

    success: bool
    recipe_path: str
    validation_result: Any  # Will use MCPValidationResult from user_recipe
    message: str


class UpdateProcessedRecipeResponse(T2DBaseModel):
    """Response after updating a processed recipe."""

    success: bool
    recipe_path: str
    sections_updated: list[str]
    validation_result: Any | None = None  # Will use MCPValidationResult
    message: str
