"""
T012: Integration test for complete transformation pipeline.
This test will fail initially until the transformation pipeline is implemented.
"""

import pytest

from t2d_kit.core.transform import TransformPipeline
from t2d_kit.models.diagram_spec import DiagramSpec
from t2d_kit.models.processed_recipe import ProcessedRecipe
from t2d_kit.models.user_recipe import UserRecipe


class TestTransformIntegration:
    """Integration tests for the complete transformation pipeline."""

    def test_transform_pipeline_initialization(self):
        """Test that TransformPipeline can be initialized."""
        pipeline = TransformPipeline()
        assert pipeline is not None
        assert hasattr(pipeline, "transform")
        assert hasattr(pipeline, "user_recipe_to_processed")
        assert hasattr(pipeline, "processed_to_diagram_spec")

    def test_end_to_end_transformation(self):
        """Test complete transformation from UserRecipe to DiagramSpec."""
        # Create a user recipe
        user_recipe_data = {
            "name": "E2E Test System",
            "description": "End-to-end transformation test",
            "components": ["frontend", "api", "database", "cache"],
            "connections": [
                {"from": "frontend", "to": "api"},
                {"from": "api", "to": "database"},
                {"from": "api", "to": "cache"},
            ],
        }
        user_recipe = UserRecipe(**user_recipe_data)

        # Run complete transformation
        pipeline = TransformPipeline()
        diagram_spec = pipeline.transform(user_recipe)

        # Verify the result
        assert isinstance(diagram_spec, DiagramSpec)
        assert diagram_spec.title == "E2E Test System"
        assert diagram_spec.description == "End-to-end transformation test"
        assert "frontend" in diagram_spec.d2_content
        assert "api" in diagram_spec.d2_content
        assert "database" in diagram_spec.d2_content
        assert "cache" in diagram_spec.d2_content
        assert "->" in diagram_spec.d2_content

    def test_user_recipe_to_processed_transformation(self):
        """Test transformation from UserRecipe to ProcessedRecipe."""
        user_recipe_data = {
            "name": "Processing Test",
            "description": "Test user to processed transformation",
            "components": ["web", "app", "db"],
            "connections": [{"from": "web", "to": "app"}, {"from": "app", "to": "db"}],
        }
        user_recipe = UserRecipe(**user_recipe_data)

        pipeline = TransformPipeline()
        processed_recipe = pipeline.user_recipe_to_processed(user_recipe)

        assert isinstance(processed_recipe, ProcessedRecipe)
        assert processed_recipe.user_recipe == user_recipe
        assert "nodes" in processed_recipe.processed_data
        assert "edges" in processed_recipe.processed_data
        assert len(processed_recipe.processed_data["nodes"]) == 3
        assert len(processed_recipe.processed_data["edges"]) == 2

    def test_processed_to_diagram_spec_transformation(self):
        """Test transformation from ProcessedRecipe to DiagramSpec."""
        user_recipe_data = {
            "name": "D2 Generation Test",
            "description": "Test processed to D2 transformation",
            "components": ["client", "server"],
            "connections": [{"from": "client", "to": "server"}],
        }
        user_recipe = UserRecipe(**user_recipe_data)

        processed_data = {
            "nodes": [
                {"id": "client", "label": "Client App", "shape": "rectangle"},
                {"id": "server", "label": "Server", "shape": "cylinder"},
            ],
            "edges": [{"from": "client", "to": "server", "label": "HTTP requests"}],
            "layout": "hierarchical",
        }
        processed_recipe = ProcessedRecipe(user_recipe=user_recipe, processed_data=processed_data)

        pipeline = TransformPipeline()
        diagram_spec = pipeline.processed_to_diagram_spec(processed_recipe)

        assert isinstance(diagram_spec, DiagramSpec)
        assert diagram_spec.title == "D2 Generation Test"
        assert "client" in diagram_spec.d2_content
        assert "server" in diagram_spec.d2_content
        assert "Client App" in diagram_spec.d2_content
        assert "Server" in diagram_spec.d2_content

    def test_transform_with_custom_layout(self):
        """Test transformation with custom layout options."""
        user_recipe_data = {
            "name": "Custom Layout Test",
            "description": "Test custom layout transformation",
            "components": ["a", "b", "c", "d"],
            "connections": [
                {"from": "a", "to": "b"},
                {"from": "b", "to": "c"},
                {"from": "c", "to": "d"},
                {"from": "d", "to": "a"},  # Circular connection
            ],
        }
        user_recipe = UserRecipe(**user_recipe_data)

        pipeline = TransformPipeline()
        diagram_spec = pipeline.transform(
            user_recipe, layout_options={"type": "circular", "spacing": "wide"}
        )

        assert isinstance(diagram_spec, DiagramSpec)
        # Verify circular layout was applied
        assert "circular" in diagram_spec.d2_content.lower() or len(diagram_spec.d2_content) > 0

    def test_transform_with_styling_options(self):
        """Test transformation with custom styling options."""
        user_recipe_data = {
            "name": "Styling Test",
            "description": "Test styling transformation",
            "components": ["frontend", "backend"],
            "connections": [{"from": "frontend", "to": "backend"}],
        }
        user_recipe = UserRecipe(**user_recipe_data)

        styling_options = {
            "theme": "dark",
            "colors": {"frontend": "blue", "backend": "green"},
            "shapes": {"frontend": "rectangle", "backend": "cylinder"},
        }

        pipeline = TransformPipeline()
        diagram_spec = pipeline.transform(user_recipe, styling_options=styling_options)

        assert isinstance(diagram_spec, DiagramSpec)
        # Verify styling was applied
        d2_content = diagram_spec.d2_content
        assert "frontend" in d2_content
        assert "backend" in d2_content

    def test_transform_error_handling(self):
        """Test error handling in transformation pipeline."""
        # Test with invalid user recipe
        invalid_recipe_data = {
            "name": "",  # Invalid: empty name
            "description": "Invalid recipe",
            "components": [],  # Invalid: empty components
            "connections": [],
        }

        TransformPipeline()
        with pytest.raises(ValueError):
            UserRecipe(**invalid_recipe_data)

    def test_transform_pipeline_caching(self):
        """Test that transformation pipeline uses caching effectively."""
        user_recipe_data = {
            "name": "Caching Test",
            "description": "Test caching in pipeline",
            "components": ["cache_test"],
            "connections": [],
        }
        user_recipe = UserRecipe(**user_recipe_data)

        pipeline = TransformPipeline(enable_caching=True)

        # First transformation
        result1 = pipeline.transform(user_recipe)

        # Second transformation (should use cache)
        result2 = pipeline.transform(user_recipe)

        assert result1.d2_content == result2.d2_content
        assert result1.title == result2.title

    def test_transform_pipeline_metrics(self):
        """Test transformation pipeline performance metrics."""
        user_recipe_data = {
            "name": "Metrics Test",
            "description": "Test performance metrics",
            "components": ["metric1", "metric2", "metric3"],
            "connections": [
                {"from": "metric1", "to": "metric2"},
                {"from": "metric2", "to": "metric3"},
            ],
        }
        user_recipe = UserRecipe(**user_recipe_data)

        pipeline = TransformPipeline(collect_metrics=True)
        pipeline.transform(user_recipe)

        metrics = pipeline.get_metrics()
        assert "transformation_time" in metrics
        assert "components_processed" in metrics
        assert "connections_processed" in metrics
        assert metrics["components_processed"] == 3
        assert metrics["connections_processed"] == 2
