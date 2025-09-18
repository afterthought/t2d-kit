# Enhanced Data Model: Multi-Framework Diagram Pipeline

**Date**: 2025-01-16
**Feature**: Enhanced Pydantic Models with Validation
**Branch**: 001-i-want-to

## Base Model Configuration

### T2DBaseModel with ConfigDict

```python
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from typing import Annotated, Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import re
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
    options: Optional[Dict[str, Any]] = None

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

---
*Enhanced data model with Pydantic validation: 2025-01-16*