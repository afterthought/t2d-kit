"""
Test UserRecipe model with correct structure.
"""

import pytest
from pydantic import ValidationError

from t2d_kit.models.user_recipe import UserRecipe


class TestUserRecipeWorking:
    """Test cases for UserRecipe model with correct structure."""

    def test_user_recipe_creation(self):
        """Test that UserRecipe can be created with valid data."""
        recipe_data = {
            "name": "SimpleFlow",
            "version": "1.0.0",
            "prd": {
                "content": "# Product Requirements\n\nThis is a test PRD.",
                "format": "markdown"
            },
            "instructions": {
                "diagrams": [
                    {
                        "type": "system_architecture",
                        "description": "High-level system overview"
                    }
                ]
            }
        }

        recipe = UserRecipe(**recipe_data)
        assert recipe.name == "SimpleFlow"
        assert recipe.version == "1.0.0"
        assert recipe.prd.content == "# Product Requirements\n\nThis is a test PRD."
        assert len(recipe.instructions.diagrams) == 1

    def test_user_recipe_validation_missing_name(self):
        """Test that UserRecipe raises error when name is missing."""
        recipe_data = {
            "prd": {"content": "Test PRD"},
            "instructions": {"diagrams": [{"type": "test"}]}
        }

        with pytest.raises(ValidationError) as exc_info:
            UserRecipe(**recipe_data)

        errors = exc_info.value.errors()
        assert any(e['loc'] == ('name',) and e['type'] == 'missing' for e in errors)

    def test_user_recipe_validation_invalid_name(self):
        """Test that UserRecipe validates name format."""
        recipe_data = {
            "name": "123-invalid",  # Must start with letter
            "prd": {"content": "Test PRD"},
            "instructions": {"diagrams": [{"type": "test"}]}
        }

        with pytest.raises(ValidationError) as exc_info:
            UserRecipe(**recipe_data)

        errors = exc_info.value.errors()
        assert any('must start with letter' in str(e.get('ctx', {}).get('error', ''))
                   or 'must start with letter' in str(e.get('msg', ''))
                   for e in errors)

    def test_user_recipe_with_preferences(self):
        """Test UserRecipe with preferences."""
        recipe_data = {
            "name": "ProjectWithPrefs",
            "prd": {"content": "Test PRD"},
            "instructions": {"diagrams": [{"type": "flowchart"}]},
            "preferences": {
                "default_framework": "d2",
                "diagram_style": "clean",
                "color_scheme": "modern"
            }
        }

        recipe = UserRecipe(**recipe_data)
        assert recipe.preferences.default_framework == "d2"
        assert recipe.preferences.diagram_style == "clean"

    def test_user_recipe_model_dump(self):
        """Test that UserRecipe can be serialized."""
        recipe_data = {
            "name": "TestRecipe",
            "prd": {"content": "Test PRD"},
            "instructions": {"diagrams": [{"type": "test_diagram"}]}
        }

        recipe = UserRecipe(**recipe_data)
        result = recipe.model_dump()

        assert result["name"] == "TestRecipe"
        assert result["prd"]["content"] == "Test PRD"
        assert len(result["instructions"]["diagrams"]) == 1

    def test_user_recipe_no_diagrams_fails(self):
        """Test that recipe without diagrams fails validation."""
        recipe_data = {
            "name": "NoDiagrams",
            "prd": {"content": "Test PRD"},
            "instructions": {}  # No diagrams
        }

        with pytest.raises(ValidationError) as exc_info:
            UserRecipe(**recipe_data)

        errors = exc_info.value.errors()
        assert any(e['loc'] == ('instructions', 'diagrams') for e in errors)
