"""
T006: Test UserRecipe model validation and functionality.
This test will fail initially until the UserRecipe model is implemented.
"""
import pytest

from t2d_kit.models.user_recipe import UserRecipe


class TestUserRecipe:
    """Test cases for UserRecipe model."""

    def test_user_recipe_creation(self):
        """Test that UserRecipe can be created with valid data."""
        recipe_data = {
            "name": "Simple Flow",
            "description": "A basic data flow diagram",
            "components": ["database", "api", "frontend"],
            "connections": [
                {"from": "database", "to": "api"},
                {"from": "api", "to": "frontend"}
            ]
        }

        recipe = UserRecipe(**recipe_data)
        assert recipe.name == "Simple Flow"
        assert recipe.description == "A basic data flow diagram"
        assert len(recipe.components) == 3
        assert len(recipe.connections) == 2

    def test_user_recipe_validation_missing_name(self):
        """Test that UserRecipe raises error when name is missing."""
        recipe_data = {
            "description": "Missing name",
            "components": ["api"],
            "connections": []
        }

        with pytest.raises(ValueError, match="name.*required"):
            UserRecipe(**recipe_data)

    def test_user_recipe_validation_empty_components(self):
        """Test that UserRecipe requires at least one component."""
        recipe_data = {
            "name": "Empty Recipe",
            "description": "No components",
            "components": [],
            "connections": []
        }

        with pytest.raises(ValueError, match="components.*empty"):
            UserRecipe(**recipe_data)

    def test_user_recipe_to_dict(self):
        """Test that UserRecipe can be serialized to dictionary."""
        recipe_data = {
            "name": "Test Recipe",
            "description": "Test description",
            "components": ["a", "b"],
            "connections": [{"from": "a", "to": "b"}]
        }

        recipe = UserRecipe(**recipe_data)
        result = recipe.to_dict()

        assert result["name"] == "Test Recipe"
        assert result["description"] == "Test description"
        assert result["components"] == ["a", "b"]
        assert result["connections"] == [{"from": "a", "to": "b"}]

    def test_user_recipe_from_dict(self):
        """Test that UserRecipe can be created from dictionary."""
        recipe_data = {
            "name": "From Dict",
            "description": "Created from dict",
            "components": ["x", "y"],
            "connections": [{"from": "x", "to": "y"}]
        }

        recipe = UserRecipe.from_dict(recipe_data)
        assert recipe.name == "From Dict"
        assert recipe.components == ["x", "y"]
