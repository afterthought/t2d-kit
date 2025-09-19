"""
T007: Test ProcessedRecipe model functionality.
This test will fail initially until the ProcessedRecipe model is implemented.
"""
import pytest

from t2d_kit.models.processed_recipe import ProcessedRecipe
from t2d_kit.models.user_recipe import UserRecipe


class TestProcessedRecipe:
    """Test cases for ProcessedRecipe model."""

    def test_processed_recipe_creation(self):
        """Test that ProcessedRecipe can be created with processed data."""
        user_recipe_data = {
            "name": "Basic Flow",
            "description": "Simple flow",
            "components": ["db", "api"],
            "connections": [{"from": "db", "to": "api"}]
        }
        user_recipe = UserRecipe(**user_recipe_data)

        processed_data = {
            "nodes": [
                {"id": "db", "label": "Database", "shape": "cylinder"},
                {"id": "api", "label": "API Server", "shape": "rectangle"}
            ],
            "edges": [
                {"from": "db", "to": "api", "label": "queries"}
            ],
            "layout": "hierarchical"
        }

        processed_recipe = ProcessedRecipe(
            user_recipe=user_recipe,
            processed_data=processed_data
        )

        assert processed_recipe.user_recipe == user_recipe
        assert len(processed_recipe.processed_data["nodes"]) == 2
        assert len(processed_recipe.processed_data["edges"]) == 1

    def test_processed_recipe_validation_missing_nodes(self):
        """Test that ProcessedRecipe requires nodes in processed_data."""
        user_recipe_data = {
            "name": "Test",
            "description": "Test",
            "components": ["a"],
            "connections": []
        }
        user_recipe = UserRecipe(**user_recipe_data)

        processed_data = {
            "edges": [],
            "layout": "hierarchical"
        }

        with pytest.raises(ValueError, match="nodes.*required"):
            ProcessedRecipe(
                user_recipe=user_recipe,
                processed_data=processed_data
            )

    def test_processed_recipe_get_d2_compatible_format(self):
        """Test that ProcessedRecipe can generate D2-compatible format."""
        user_recipe_data = {
            "name": "D2 Test",
            "description": "For D2 generation",
            "components": ["frontend", "backend"],
            "connections": [{"from": "frontend", "to": "backend"}]
        }
        user_recipe = UserRecipe(**user_recipe_data)

        processed_data = {
            "nodes": [
                {"id": "frontend", "label": "Frontend", "shape": "rectangle"},
                {"id": "backend", "label": "Backend", "shape": "rectangle"}
            ],
            "edges": [
                {"from": "frontend", "to": "backend", "label": "API calls"}
            ],
            "layout": "hierarchical"
        }

        processed_recipe = ProcessedRecipe(
            user_recipe=user_recipe,
            processed_data=processed_data
        )

        d2_format = processed_recipe.get_d2_compatible_format()
        assert "frontend" in d2_format
        assert "backend" in d2_format
        assert "->" in d2_format

    def test_processed_recipe_to_dict(self):
        """Test that ProcessedRecipe can be serialized to dictionary."""
        user_recipe_data = {
            "name": "Serialize Test",
            "description": "Test serialization",
            "components": ["a"],
            "connections": []
        }
        user_recipe = UserRecipe(**user_recipe_data)

        processed_data = {
            "nodes": [{"id": "a", "label": "Component A", "shape": "circle"}],
            "edges": [],
            "layout": "circular"
        }

        processed_recipe = ProcessedRecipe(
            user_recipe=user_recipe,
            processed_data=processed_data
        )

        result = processed_recipe.to_dict()
        assert "user_recipe" in result
        assert "processed_data" in result
        assert result["processed_data"]["layout"] == "circular"
