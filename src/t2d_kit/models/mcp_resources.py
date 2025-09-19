"""Pydantic models for MCP resources."""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator, model_validator


class DiagramTypeInfo(BaseModel):
    """Information about a diagram type."""

    type_id: str = Field(..., description="Unique identifier for the diagram type")
    name: str = Field(..., description="Human-readable name")
    framework: str = Field(..., description="Recommended framework (mermaid, d2, plantuml)")
    description: str = Field(..., description="What this diagram type is used for")
    example_usage: str = Field(..., description="Example description for this type")
    supported_frameworks: list[str] = Field(..., description="All frameworks that support this type")

    @field_validator("framework")
    @classmethod
    def validate_framework(cls, v):
        """Validate framework is supported."""
        valid_frameworks = ["mermaid", "d2", "plantuml"]
        if v not in valid_frameworks:
            raise ValueError(f"Framework must be one of {valid_frameworks}")
        return v

    @field_validator("supported_frameworks")
    @classmethod
    def validate_supported_frameworks(cls, v):
        """Validate all supported frameworks."""
        valid_frameworks = ["mermaid", "d2", "plantuml"]
        for framework in v:
            if framework not in valid_frameworks:
                raise ValueError(f"All frameworks must be one of {valid_frameworks}")
        return v


class DiagramTypesResource(BaseModel):
    """Resource containing all available diagram types."""

    diagram_types: list[DiagramTypeInfo]
    total_count: int
    categories: dict[str, list[str]] = Field(..., description="Types grouped by category")

    @model_validator(mode="after")
    def validate_count(self):
        """Ensure count matches diagram_types length."""
        actual_count = len(self.diagram_types)
        if self.total_count != actual_count:
            raise ValueError(f"total_count ({self.total_count}) must match diagram_types length ({actual_count})")
        return self


class RecipeSummary(BaseModel):
    """Summary information for a recipe."""

    name: str = Field(..., description="Recipe name")
    file_path: str = Field(..., description="Path to recipe file")
    created_at: str = Field(..., description="ISO timestamp of creation")
    modified_at: str = Field(..., description="ISO timestamp of last modification")
    size_bytes: int = Field(..., ge=0, description="File size in bytes")
    diagram_count: int = Field(..., ge=0, description="Number of diagrams defined")
    has_prd: bool = Field(..., description="Whether PRD content is included")
    validation_status: str = Field(..., description="valid, invalid, or unknown")

    @field_validator("validation_status")
    @classmethod
    def validate_status(cls, v):
        """Validate status value."""
        valid_statuses = ["valid", "invalid", "unknown"]
        if v not in valid_statuses:
            raise ValueError(f"validation_status must be one of {valid_statuses}")
        return v

    @field_validator("created_at", "modified_at")
    @classmethod
    def validate_timestamp(cls, v):
        """Validate ISO timestamp format."""
        try:
            datetime.fromisoformat(v.replace("Z", "+00:00"))
        except (ValueError, AttributeError) as e:
            raise ValueError(f"Invalid ISO timestamp: {v}") from e
        return v


class RecipeListResource(BaseModel):
    """Resource containing list of recipes."""

    recipes: list[RecipeSummary]
    total_count: int
    directory: str = Field(..., description="Recipe directory path")

    @model_validator(mode="after")
    def validate_count(self):
        """Ensure count matches recipes length."""
        actual_count = len(self.recipes)
        if self.total_count != actual_count:
            raise ValueError(f"total_count ({self.total_count}) must match recipes length ({actual_count})")
        return self


class RecipeDetailResource(BaseModel):
    """Resource containing full recipe details."""

    name: str
    content: dict[str, Any] = Field(..., description="Parsed YAML content")
    raw_yaml: str = Field(..., description="Raw YAML text")
    validation_result: dict[str, Any] | None = None
    file_path: str
    metadata: RecipeSummary


class ProcessedRecipeSummary(BaseModel):
    """Summary information for a processed recipe."""

    name: str = Field(..., description="Recipe name")
    file_path: str = Field(..., description="Path to processed recipe file")
    source_recipe: str = Field(..., description="Source user recipe name")
    generated_at: str = Field(..., description="ISO timestamp of generation")
    modified_at: str = Field(..., description="ISO timestamp of last modification")
    size_bytes: int = Field(..., ge=0, description="File size in bytes")
    diagram_count: int = Field(..., ge=0, description="Number of diagrams specified")
    content_file_count: int = Field(..., ge=0, description="Number of content files")
    validation_status: str = Field(..., description="valid, invalid, or unknown")

    @field_validator("validation_status")
    @classmethod
    def validate_status(cls, v):
        """Validate status value."""
        valid_statuses = ["valid", "invalid", "unknown"]
        if v not in valid_statuses:
            raise ValueError(f"validation_status must be one of {valid_statuses}")
        return v

    @field_validator("generated_at", "modified_at")
    @classmethod
    def validate_timestamp(cls, v):
        """Validate ISO timestamp format."""
        try:
            datetime.fromisoformat(v.replace("Z", "+00:00"))
        except (ValueError, AttributeError) as e:
            raise ValueError(f"Invalid ISO timestamp: {v}") from e
        return v


class ProcessedRecipeListResource(BaseModel):
    """Resource containing list of processed recipes."""

    recipes: list[ProcessedRecipeSummary]
    total_count: int
    directory: str = Field(..., description="Processed recipe directory path")

    @model_validator(mode="after")
    def validate_count(self):
        """Ensure count matches recipes length."""
        actual_count = len(self.recipes)
        if self.total_count != actual_count:
            raise ValueError(f"total_count ({self.total_count}) must match recipes length ({actual_count})")
        return self


class ProcessedRecipeDetailResource(BaseModel):
    """Resource containing full processed recipe details."""

    name: str
    content: dict[str, Any] = Field(..., description="Parsed YAML content")
    raw_yaml: str = Field(..., description="Raw YAML text")
    validation_result: dict[str, Any] | None = None
    file_path: str
    metadata: ProcessedRecipeSummary


class SchemaField(BaseModel):
    """Schema field definition."""

    name: str
    type: str
    required: bool
    description: str
    default: Any | None = None
    constraints: dict[str, Any] | None = None
    example: Any | None = None


class RecipeSchemaResource(BaseModel):
    """Resource containing recipe schema information."""

    version: str = Field(..., pattern=r"^\d+\.\d+\.\d+$", description="Schema version")
    fields: list[SchemaField]
    examples: dict[str, Any] = Field(..., description="Example recipes")
    validation_rules: list[str] = Field(..., description="Validation rule descriptions")
