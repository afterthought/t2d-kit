"""
T007: Test ProcessedRecipe model functionality.
"""

from datetime import datetime, timedelta, timezone

import pytest

from t2d_kit.models.base import ContentType, DiagramType, FrameworkType, OutputFormat
from t2d_kit.models.content import ContentFile
from t2d_kit.models.diagram import DiagramSpecification
from t2d_kit.models.processed_recipe import DiagramReference, OutputConfig, ProcessedRecipe


class TestProcessedRecipe:
    """Test cases for ProcessedRecipe model."""

    def create_valid_content_file(self) -> ContentFile:
        """Create a valid ContentFile for testing."""
        return ContentFile(
            id="test-content",
            path="docs/test.md",
            type=ContentType.DOCUMENTATION,
            agent="t2d-markdown-maintainer",
            base_prompt="Generate comprehensive documentation for the system.",
            diagram_refs=["arch-diagram"],
            title="Test Documentation",
            last_updated=datetime.now(timezone.utc)
        )

    def create_valid_diagram_spec(self) -> DiagramSpecification:
        """Create a valid DiagramSpecification for testing."""
        return DiagramSpecification(
            id="arch-diagram",
            type=DiagramType.ARCHITECTURE,
            framework=FrameworkType.D2,
            agent="t2d-diagram-generator",
            title="System Architecture",
            instructions="Create a system architecture diagram showing the main components.",
            output_file="diagrams/architecture.d2",
            output_formats=[OutputFormat.SVG, OutputFormat.PNG]
        )

    def create_valid_diagram_ref(self) -> DiagramReference:
        """Create a valid DiagramReference for testing."""
        return DiagramReference(
            id="arch-diagram",
            title="System Architecture",
            type=DiagramType.ARCHITECTURE,
            expected_path="diagrams/architecture.d2",
            description="Main system architecture",
            status="pending"
        )

    def create_valid_output_config(self) -> OutputConfig:
        """Create a valid OutputConfig for testing."""
        return OutputConfig(
            assets_dir="docs/assets",
            mkdocs={"theme": "material"},
            marp={"theme": "default"}
        )

    def test_processed_recipe_creation(self):
        """Test that ProcessedRecipe can be created with valid data."""
        processed_recipe = ProcessedRecipe(
            name="Test Recipe",
            version="1.0.0",
            source_recipe="recipes/test.yaml",
            generated_at=datetime.now(timezone.utc),
            content_files=[self.create_valid_content_file()],
            diagram_specs=[self.create_valid_diagram_spec()],
            diagram_refs=[self.create_valid_diagram_ref()],
            outputs=self.create_valid_output_config(),
            generation_notes=["Initial generation", "Added documentation"]
        )

        assert processed_recipe.name == "Test Recipe"
        assert processed_recipe.version == "1.0.0"
        assert len(processed_recipe.content_files) == 1
        assert len(processed_recipe.diagram_specs) == 1
        assert len(processed_recipe.diagram_refs) == 1
        assert len(processed_recipe.generation_notes) == 2

    def test_processed_recipe_minimum_required_fields(self):
        """Test ProcessedRecipe with minimum required fields."""
        processed_recipe = ProcessedRecipe(
            name="Minimal Recipe",
            version="1.0.0",
            source_recipe="recipes/minimal.yaml",
            generated_at=datetime.now(timezone.utc),
            content_files=[self.create_valid_content_file()],
            diagram_specs=[self.create_valid_diagram_spec()],
            diagram_refs=[self.create_valid_diagram_ref()],
            outputs=self.create_valid_output_config()
        )

        assert processed_recipe.name == "Minimal Recipe"
        assert processed_recipe.generation_notes is None

    def test_processed_recipe_validation_empty_content_files(self):
        """Test that ProcessedRecipe requires at least one content file."""
        with pytest.raises(ValueError, match="at least 1 item"):
            ProcessedRecipe(
                name="Invalid Recipe",
                version="1.0.0",
                source_recipe="recipes/invalid.yaml",
                generated_at=datetime.now(timezone.utc),
                content_files=[],  # Empty list should fail
                diagram_specs=[self.create_valid_diagram_spec()],
                diagram_refs=[self.create_valid_diagram_ref()],
                outputs=self.create_valid_output_config()
            )

    def test_processed_recipe_validation_empty_diagram_specs(self):
        """Test that ProcessedRecipe requires at least one diagram spec."""
        with pytest.raises(ValueError, match="at least 1 item"):
            ProcessedRecipe(
                name="Invalid Recipe",
                version="1.0.0",
                source_recipe="recipes/invalid.yaml",
                generated_at=datetime.now(timezone.utc),
                content_files=[self.create_valid_content_file()],
                diagram_specs=[],  # Empty list should fail
                diagram_refs=[self.create_valid_diagram_ref()],
                outputs=self.create_valid_output_config()
            )

    def test_processed_recipe_validation_empty_diagram_refs(self):
        """Test that ProcessedRecipe requires at least one diagram reference."""
        with pytest.raises(ValueError, match="at least 1 item"):
            ProcessedRecipe(
                name="Invalid Recipe",
                version="1.0.0",
                source_recipe="recipes/invalid.yaml",
                generated_at=datetime.now(timezone.utc),
                content_files=[self.create_valid_content_file()],
                diagram_specs=[self.create_valid_diagram_spec()],
                diagram_refs=[],  # Empty list should fail
                outputs=self.create_valid_output_config()
            )

    def test_processed_recipe_validation_future_generation_time(self):
        """Test that ProcessedRecipe rejects future generation times."""
        future_time = datetime.now(timezone.utc) + timedelta(hours=1)

        with pytest.raises(ValueError, match="Generation time cannot be in the future"):
            ProcessedRecipe(
                name="Future Recipe",
                version="1.0.0",
                source_recipe="recipes/future.yaml",
                generated_at=future_time,
                content_files=[self.create_valid_content_file()],
                diagram_specs=[self.create_valid_diagram_spec()],
                diagram_refs=[self.create_valid_diagram_ref()],
                outputs=self.create_valid_output_config()
            )

    def test_processed_recipe_diagram_consistency_validation(self):
        """Test that diagram specs and refs must have matching IDs."""
        # Create spec with one ID
        spec = self.create_valid_diagram_spec()
        spec.id = "spec-diagram"

        # Create ref with different ID
        ref = self.create_valid_diagram_ref()
        ref.id = "ref-diagram"

        with pytest.raises(ValueError, match="Missing diagram references.*spec-diagram"):
            ProcessedRecipe(
                name="Inconsistent Recipe",
                version="1.0.0",
                source_recipe="recipes/inconsistent.yaml",
                generated_at=datetime.now(timezone.utc),
                content_files=[self.create_valid_content_file()],
                diagram_specs=[spec],
                diagram_refs=[ref],
                outputs=self.create_valid_output_config()
            )

    def test_processed_recipe_content_diagram_refs_validation(self):
        """Test that content files can only reference valid diagrams."""
        # Create content file that references non-existent diagram
        content_file = self.create_valid_content_file()
        content_file.diagram_refs = ["non-existent-diagram"]

        with pytest.raises(ValueError, match="references invalid diagrams.*non-existent-diagram"):
            ProcessedRecipe(
                name="Invalid Refs Recipe",
                version="1.0.0",
                source_recipe="recipes/invalid_refs.yaml",
                generated_at=datetime.now(timezone.utc),
                content_files=[content_file],
                diagram_specs=[self.create_valid_diagram_spec()],
                diagram_refs=[self.create_valid_diagram_ref()],
                outputs=self.create_valid_output_config()
            )

    def test_processed_recipe_serialization(self):
        """Test that ProcessedRecipe can be serialized and deserialized."""
        original = ProcessedRecipe(
            name="Serialization Test",
            version="2.1.0",
            source_recipe="recipes/serialization.yaml",
            generated_at=datetime.now(timezone.utc),
            content_files=[self.create_valid_content_file()],
            diagram_specs=[self.create_valid_diagram_spec()],
            diagram_refs=[self.create_valid_diagram_ref()],
            outputs=self.create_valid_output_config(),
            generation_notes=["Test note 1", "Test note 2"]
        )

        # Serialize to dict
        data = original.model_dump()

        # Verify structure
        assert "name" in data
        assert "version" in data
        assert "content_files" in data
        assert "diagram_specs" in data
        assert "diagram_refs" in data
        assert "outputs" in data
        assert "generation_notes" in data

        # Deserialize
        recreated = ProcessedRecipe(**data)

        # Verify equality
        assert recreated.name == original.name
        assert recreated.version == original.version
        assert len(recreated.content_files) == len(original.content_files)
        assert len(recreated.diagram_specs) == len(original.diagram_specs)
        assert len(recreated.diagram_refs) == len(original.diagram_refs)
        assert recreated.generation_notes == original.generation_notes
