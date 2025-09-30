"""T019: ContentFile model for markdown content management."""

from datetime import datetime
from pathlib import Path

from pydantic import Field, field_validator

from .base import ContentType, InstructionsField, NameField, PathField, T2DBaseModel


class ContentFile(T2DBaseModel):
    """Markdown files maintained by Claude Code agents."""

    id: str = Field(pattern=r"^[a-zA-Z0-9_-]+$", min_length=1, max_length=100)
    path: PathField
    type: ContentType
    agent: str = Field(pattern=r"^t2d-[a-z0-9-]+$")
    base_prompt: InstructionsField
    diagram_refs: list[str] = Field(default_factory=list)
    title: NameField | None = None
    last_updated: datetime | str

    @field_validator("last_updated")
    @classmethod
    def validate_last_updated(cls, v: datetime | str) -> datetime:
        """Convert string to datetime if needed."""
        if isinstance(v, str):
            try:
                # Handle ISO format with Z suffix
                if v.endswith("Z"):
                    v = v[:-1] + "+00:00"
                from datetime import timezone
                v = datetime.fromisoformat(v)
            except (ValueError, TypeError) as e:
                raise ValueError(f"Invalid datetime format: {v}") from e
        return v

    @field_validator("path")
    @classmethod
    def validate_markdown_extension(cls, v: str) -> str:
        """Ensure content files are markdown."""
        path = Path(v)
        if path.suffix not in {".md", ".markdown"}:
            raise ValueError("Content files must be markdown (.md or .markdown)")
        return v

    @field_validator("agent")
    @classmethod
    def validate_agent_type(cls, v: str) -> str:
        """Ensure agent is a valid content agent."""
        valid_agents = {"t2d-mkdocs-generator", "t2d-zudoku-generator", "t2d-slides-generator"}
        if v not in valid_agents:
            raise ValueError(f"Agent must be one of: {valid_agents}")
        return v

    @field_validator("base_prompt")
    @classmethod
    def validate_base_prompt_content(cls, v: str) -> str:
        """Ensure base prompt is appropriate for content generation."""
        if "diagram" in v.lower() and ("![" in v or "path" in v.lower()):
            raise ValueError(
                "Base prompt should not contain specific diagram references or paths. "
                "Diagram context is added dynamically at invocation time."
            )
        return v

    def get_agent_prompt_template(self) -> str:
        """Get the template for combining base prompt with diagram context."""
        return f"""
{self.base_prompt}

Available diagrams for inclusion:
{{diagram_context}}

Guidelines:
- Use relative paths when referencing diagrams
- Include appropriate alt text for accessibility
- Consider the content type ({self.type.value}) when structuring the output
"""

    def format_diagram_context(self, diagram_references: list["DiagramReference"]) -> str:
        """Format diagram references for inclusion in agent prompts."""
        if not diagram_references:
            return "No diagrams available."

        context_lines = []
        for ref in diagram_references:
            if ref.status == "generated" and ref.actual_paths:
                context_lines.append(f"- {ref.id}: {ref.title} ({ref.type.value})")
                for format_type, path in ref.actual_paths.items():
                    context_lines.append(f"  - {format_type.upper()}: {path}")
                if ref.description:
                    context_lines.append(f"  - Description: {ref.description}")
            else:
                context_lines.append(f"- {ref.id}: {ref.title} (Status: {ref.status})")

        return "\n".join(context_lines)


# Import here to avoid circular imports
from .processed_recipe import DiagramReference

# Update forward references
ContentFile.model_rebuild()
