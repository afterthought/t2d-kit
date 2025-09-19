"""
T008: Test DiagramSpec model for D2 diagram specifications.
This test will fail initially until the DiagramSpec model is implemented.
"""
import pytest

from t2d_kit.models.diagram_spec import DiagramSpec


class TestDiagramSpec:
    """Test cases for DiagramSpec model."""

    def test_diagram_spec_creation(self):
        """Test that DiagramSpec can be created with valid D2 specification."""
        d2_content = """
        frontend: Frontend App {
          shape: rectangle
        }
        backend: Backend API {
          shape: rectangle
        }
        database: Database {
          shape: cylinder
        }

        frontend -> backend: HTTP requests
        backend -> database: SQL queries
        """

        spec = DiagramSpec(
            d2_content=d2_content,
            title="System Architecture",
            description="Basic system diagram"
        )

        assert spec.d2_content.strip() == d2_content.strip()
        assert spec.title == "System Architecture"
        assert spec.description == "Basic system diagram"

    def test_diagram_spec_validation_empty_content(self):
        """Test that DiagramSpec requires non-empty D2 content."""
        with pytest.raises(ValueError, match="d2_content.*empty"):
            DiagramSpec(
                d2_content="",
                title="Empty Diagram"
            )

    def test_diagram_spec_validation_missing_title(self):
        """Test that DiagramSpec requires a title."""
        with pytest.raises(ValueError, match="title.*required"):
            DiagramSpec(
                d2_content="a -> b",
                title=""
            )

    def test_diagram_spec_parse_components(self):
        """Test that DiagramSpec can parse components from D2 content."""
        d2_content = """
        user: User
        api: API Gateway
        db: Database
        """

        spec = DiagramSpec(
            d2_content=d2_content,
            title="Component Test"
        )

        components = spec.parse_components()
        assert "user" in components
        assert "api" in components
        assert "db" in components
        assert len(components) == 3

    def test_diagram_spec_parse_connections(self):
        """Test that DiagramSpec can parse connections from D2 content."""
        d2_content = """
        a -> b: connection1
        b -> c: connection2
        c -> a: connection3
        """

        spec = DiagramSpec(
            d2_content=d2_content,
            title="Connection Test"
        )

        connections = spec.parse_connections()
        assert len(connections) == 3
        assert any(conn["from"] == "a" and conn["to"] == "b" for conn in connections)
        assert any(conn["from"] == "b" and conn["to"] == "c" for conn in connections)
        assert any(conn["from"] == "c" and conn["to"] == "a" for conn in connections)

    def test_diagram_spec_validate_syntax(self):
        """Test that DiagramSpec can validate D2 syntax."""
        valid_d2 = "a -> b: valid connection"
        invalid_d2 = "a -> -> b: invalid syntax"

        valid_spec = DiagramSpec(
            d2_content=valid_d2,
            title="Valid Syntax"
        )
        assert valid_spec.validate_syntax() is True

        invalid_spec = DiagramSpec(
            d2_content=invalid_d2,
            title="Invalid Syntax"
        )
        assert invalid_spec.validate_syntax() is False

    def test_diagram_spec_to_dict(self):
        """Test that DiagramSpec can be serialized to dictionary."""
        d2_content = "component1 -> component2"
        spec = DiagramSpec(
            d2_content=d2_content,
            title="Serialization Test",
            description="Test description"
        )

        result = spec.to_dict()
        assert result["d2_content"] == d2_content
        assert result["title"] == "Serialization Test"
        assert result["description"] == "Test description"
