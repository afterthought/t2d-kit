"""
T008: Test DiagramSpecification model with proper field validation.
Tests the actual DiagramSpecification model from t2d_kit.models.diagram.
"""

import pytest
from pydantic import ValidationError

from t2d_kit.models.base import DiagramType, FrameworkType, OutputFormat
from t2d_kit.models.diagram import DiagramSpecification


class TestDiagramSpecification:
    """Test cases for DiagramSpecification model."""

    def test_diagram_specification_creation_minimal(self):
        """Test that DiagramSpecification can be created with minimal valid data."""
        spec = DiagramSpecification(
            id="test-diagram-1",
            type=DiagramType.ARCHITECTURE,
            agent="t2d-generator-v1",
            title="System Architecture",
            instructions="This is a detailed system architecture diagram showing the main components and their interactions in the application",
            output_file="architecture.d2",
            output_formats=[OutputFormat.SVG]
        )

        assert spec.id == "test-diagram-1"
        assert spec.type == DiagramType.ARCHITECTURE
        assert spec.framework == FrameworkType.D2  # Auto-selected
        assert spec.agent == "t2d-generator-v1"
        assert spec.title == "System Architecture"
        assert spec.instructions == "This is a detailed system architecture diagram showing the main components and their interactions in the application"
        assert spec.output_file == "architecture.d2"
        assert spec.output_formats == [OutputFormat.SVG]

    def test_diagram_specification_creation_full(self):
        """Test DiagramSpecification creation with all fields."""
        spec = DiagramSpecification(
            id="test-diagram-2",
            type=DiagramType.FLOWCHART,
            framework=FrameworkType.MERMAID,
            agent="t2d-mermaid-agent",
            title="Process Flow",
            instructions="Create a detailed flowchart showing the user registration process with error handling and validation steps",
            output_file="process.mmd",
            output_formats=[OutputFormat.SVG, OutputFormat.PNG],
            options={"theme": "dark", "fontFamily": "Arial"}
        )

        assert spec.id == "test-diagram-2"
        assert spec.type == DiagramType.FLOWCHART
        assert spec.framework == FrameworkType.MERMAID
        assert spec.agent == "t2d-mermaid-agent"
        assert spec.title == "Process Flow"
        assert spec.instructions == "Create a detailed flowchart showing the user registration process with error handling and validation steps"
        assert spec.output_file == "process.mmd"
        assert spec.output_formats == [OutputFormat.SVG, OutputFormat.PNG]
        assert spec.options == {"theme": "dark", "fontFamily": "Arial"}

    def test_diagram_specification_validation_invalid_id(self):
        """Test that DiagramSpecification validates ID pattern."""
        with pytest.raises(ValidationError, match="String should match pattern"):
            DiagramSpecification(
                id="invalid id with spaces",
                type=DiagramType.ARCHITECTURE,
                agent="t2d-generator-v1",
                title="Test",
                instructions="This is a test diagram with detailed instructions",
                output_file="test.d2",
                output_formats=[OutputFormat.SVG]
            )

    def test_diagram_specification_validation_invalid_agent(self):
        """Test that DiagramSpecification validates agent pattern."""
        with pytest.raises(ValidationError, match="String should match pattern"):
            DiagramSpecification(
                id="test-diagram",
                type=DiagramType.ARCHITECTURE,
                agent="invalid-agent-name",
                title="Test",
                instructions="This is a test diagram with detailed instructions",
                output_file="test.d2",
                output_formats=[OutputFormat.SVG]
            )

    def test_diagram_specification_validation_short_instructions(self):
        """Test that DiagramSpecification requires detailed instructions."""
        with pytest.raises(ValidationError, match="Instructions must be at least 5 words"):
            DiagramSpecification(
                id="test-diagram",
                type=DiagramType.ARCHITECTURE,
                agent="t2d-generator-v1",
                title="Test",
                instructions="Short instruction",  # Only 2 words
                output_file="test.d2",
                output_formats=[OutputFormat.SVG]
            )

    def test_diagram_specification_validation_invalid_output_file(self):
        """Test that DiagramSpecification validates output file extension."""
        with pytest.raises(ValidationError, match="Output file must have extension"):
            DiagramSpecification(
                id="test-diagram",
                type=DiagramType.ARCHITECTURE,
                agent="t2d-generator-v1",
                title="Test",
                instructions="This is a test diagram with detailed instructions",
                output_file="test.txt",  # Invalid extension
                output_formats=[OutputFormat.SVG]
            )

    def test_diagram_specification_validation_empty_output_formats(self):
        """Test that DiagramSpecification sets default output formats when empty."""
        spec = DiagramSpecification(
            id="test-diagram",
            type=DiagramType.ARCHITECTURE,
            agent="t2d-generator-v1",
            title="Test",
            instructions="This is a test diagram with detailed instructions",
            output_file="test.d2",
            output_formats=[]  # Empty list
        )
        # Should default to SVG for D2
        assert spec.output_formats == [OutputFormat.SVG]
        assert spec.framework == FrameworkType.D2  # Auto-detected from .d2 extension

    def test_diagram_specification_framework_compatibility_d2(self):
        """Test framework compatibility validation for D2."""
        # Valid D2 diagram
        spec = DiagramSpecification(
            id="test-d2",
            type=DiagramType.ARCHITECTURE,
            framework=FrameworkType.D2,
            agent="t2d-d2-agent",
            title="Architecture",
            instructions="Create an architecture diagram using D2 framework with proper component layout",
            output_file="arch.d2",
            output_formats=[OutputFormat.SVG]
        )
        assert spec.framework == FrameworkType.D2

        # Invalid D2 diagram type - should raise ValidationError
        with pytest.raises(ValidationError, match="Framework d2 does not support diagram type sequence"):
            DiagramSpecification(
                id="test-d2-invalid",
                type=DiagramType.SEQUENCE,  # Not supported by D2
                framework=FrameworkType.D2,
                agent="t2d-d2-agent",
                title="Sequence",
                instructions="Create a sequence diagram using D2 framework",
                output_file="seq.d2",
                output_formats=[OutputFormat.SVG]
            )

    def test_diagram_specification_framework_compatibility_mermaid(self):
        """Test framework compatibility validation for Mermaid."""
        # Valid Mermaid diagram
        spec = DiagramSpecification(
            id="test-mermaid",
            type=DiagramType.SEQUENCE,
            framework=FrameworkType.MERMAID,
            agent="t2d-mermaid-agent",
            title="Sequence Diagram",
            instructions="Create a sequence diagram showing user authentication flow with proper timing",
            output_file="sequence.mmd",
            output_formats=[OutputFormat.SVG]
        )
        assert spec.framework == FrameworkType.MERMAID

    def test_diagram_specification_framework_compatibility_plantuml(self):
        """Test framework compatibility validation for PlantUML."""
        # Valid PlantUML diagram
        spec = DiagramSpecification(
            id="test-plantuml",
            type=DiagramType.PLANTUML_USECASE,
            framework=FrameworkType.PLANTUML,
            agent="t2d-plantuml-agent",
            title="Use Case Diagram",
            instructions="Create a use case diagram showing system actors and their interactions",
            output_file="usecase.puml",
            output_formats=[OutputFormat.SVG]
        )
        assert spec.framework == FrameworkType.PLANTUML

    def test_diagram_specification_auto_framework_selection(self):
        """Test automatic framework selection based on diagram type."""
        # Should auto-select D2 for architecture
        arch_spec = DiagramSpecification(
            id="auto-arch",
            type=DiagramType.ARCHITECTURE,
            agent="t2d-auto-agent",
            title="Auto Architecture",
            instructions="Create an architecture diagram with automatic framework selection",
            output_file="auto.d2",
            output_formats=[OutputFormat.SVG]
        )
        assert arch_spec.framework == FrameworkType.D2

        # Should auto-select Mermaid for sequence
        seq_spec = DiagramSpecification(
            id="auto-seq",
            type=DiagramType.SEQUENCE,
            agent="t2d-auto-agent",
            title="Auto Sequence",
            instructions="Create a sequence diagram with automatic framework selection",
            output_file="auto.mmd",
            output_formats=[OutputFormat.SVG]
        )
        assert seq_spec.framework == FrameworkType.MERMAID

        # Should auto-select PlantUML for PlantUML-specific types
        usecase_spec = DiagramSpecification(
            id="auto-usecase",
            type=DiagramType.PLANTUML_USECASE,
            agent="t2d-auto-agent",
            title="Auto Use Case",
            instructions="Create a use case diagram with automatic framework selection",
            output_file="auto.puml",
            output_formats=[OutputFormat.SVG]
        )
        assert usecase_spec.framework == FrameworkType.PLANTUML

    def test_diagram_specification_invalid_format_for_framework(self):
        """Test that invalid output formats for framework are rejected."""
        # Invalid output format for Mermaid - should raise ValidationError
        with pytest.raises(ValidationError, match="Framework mermaid does not support formats"):
            DiagramSpecification(
                id="invalid-format",
                type=DiagramType.SEQUENCE,
                framework=FrameworkType.MERMAID,
                agent="t2d-mermaid-agent",
                title="Invalid Format",
                instructions="Create a sequence diagram with invalid output format",
                output_file="seq.mmd",
                output_formats=[OutputFormat.INLINE]  # Not supported by Mermaid
            )

    def test_diagram_specification_model_serialization(self):
        """Test that DiagramSpecification can be serialized to dict."""
        spec = DiagramSpecification(
            id="serialize-test",
            type=DiagramType.FLOWCHART,
            framework=FrameworkType.MERMAID,
            agent="t2d-serializer",
            title="Serialization Test",
            instructions="Create a flowchart to test model serialization capabilities",
            output_file="serialize.mmd",
            output_formats=[OutputFormat.SVG, OutputFormat.PNG],
            options={"theme": "default"}
        )

        result = spec.model_dump()
        assert result["id"] == "serialize-test"
        assert result["type"] == "flowchart"
        assert result["framework"] == "mermaid"
        assert result["agent"] == "t2d-serializer"
        assert result["title"] == "Serialization Test"
        assert result["instructions"] == "Create a flowchart to test model serialization capabilities"
        assert result["output_file"] == "serialize.mmd"
        assert result["output_formats"] == ["svg", "png"]
        assert result["options"] == {"theme": "default"}
