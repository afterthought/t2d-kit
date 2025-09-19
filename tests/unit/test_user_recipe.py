"""
T006: Test UserRecipe model validation and functionality.
"""

import pytest
from pydantic import ValidationError

from t2d_kit.models.user_recipe import UserRecipe


class TestUserRecipe:
    """Test cases for UserRecipe model."""

    def test_user_recipe_creation(self):
        """Test that UserRecipe can be created with valid data."""
        recipe_data = {
            "name": "SimpleFlow",
            "version": "1.0.0",
            "prd": {
                "content": "# Product Requirements\n\nThis is a basic data flow diagram system.",
                "format": "markdown"
            },
            "instructions": {
                "diagrams": [
                    {
                        "type": "system_architecture",
                        "description": "High-level system overview"
                    },
                    {
                        "type": "data_flow",
                        "description": "Data movement between components"
                    }
                ]
            }
        }

        recipe = UserRecipe(**recipe_data)
        assert recipe.name == "SimpleFlow"
        assert recipe.version == "1.0.0"
        assert recipe.prd.content == "# Product Requirements\n\nThis is a basic data flow diagram system."
        assert len(recipe.instructions.diagrams) == 2
        assert recipe.instructions.diagrams[0].type == "system_architecture"
        assert recipe.instructions.diagrams[1].type == "data_flow"

    def test_user_recipe_validation_missing_name(self):
        """Test that UserRecipe raises error when name is missing."""
        recipe_data = {
            "prd": {"content": "Missing name PRD"},
            "instructions": {"diagrams": [{"type": "test_diagram"}]}
        }

        with pytest.raises(ValidationError) as exc_info:
            UserRecipe(**recipe_data)

        errors = exc_info.value.errors()
        assert any(e['loc'] == ('name',) and e['type'] == 'missing' for e in errors)

    def test_user_recipe_validation_invalid_name_format(self):
        """Test that UserRecipe validates name format (must start with letter, no spaces)."""
        # Test name with spaces (not allowed)
        recipe_data = {
            "name": "Invalid Name With Spaces",
            "prd": {"content": "Test PRD"},
            "instructions": {"diagrams": [{"type": "test_diagram"}]}
        }

        with pytest.raises(ValidationError) as exc_info:
            UserRecipe(**recipe_data)

        errors = exc_info.value.errors()
        assert any('must start with letter' in str(e.get('ctx', {}).get('error', ''))
                   or 'must start with letter' in str(e.get('msg', ''))
                   for e in errors)

        # Test name starting with number
        recipe_data["name"] = "123InvalidName"
        with pytest.raises(ValidationError):
            UserRecipe(**recipe_data)

    def test_user_recipe_validation_empty_diagrams(self):
        """Test that UserRecipe requires at least one diagram."""
        recipe_data = {
            "name": "EmptyDiagrams",
            "prd": {"content": "Test PRD"},
            "instructions": {"diagrams": []}
        }

        with pytest.raises(ValidationError) as exc_info:
            UserRecipe(**recipe_data)

        errors = exc_info.value.errors()
        assert any(e['loc'] == ('instructions', 'diagrams') for e in errors)

    def test_user_recipe_model_dump(self):
        """Test that UserRecipe can be serialized using model_dump."""
        recipe_data = {
            "name": "TestRecipe",
            "version": "2.0.0",
            "prd": {"content": "Test PRD content"},
            "instructions": {
                "diagrams": [{"type": "flowchart", "description": "Process flow"}]
            }
        }

        recipe = UserRecipe(**recipe_data)
        result = recipe.model_dump()

        assert result["name"] == "TestRecipe"
        assert result["version"] == "2.0.0"
        assert result["prd"]["content"] == "Test PRD content"
        assert len(result["instructions"]["diagrams"]) == 1
        assert result["instructions"]["diagrams"][0]["type"] == "flowchart"

    def test_user_recipe_with_file_path_prd(self):
        """Test that UserRecipe can be created with PRD file path instead of content."""
        recipe_data = {
            "name": "FileBasedRecipe",
            "prd": {
                "file_path": "/path/to/requirements.md",
                "format": "markdown"
            },
            "instructions": {
                "diagrams": [{"type": "architecture"}]
            }
        }

        recipe = UserRecipe(**recipe_data)
        assert recipe.name == "FileBasedRecipe"
        assert recipe.prd.file_path == "/path/to/requirements.md"
        assert recipe.prd.content is None

    def test_user_recipe_with_preferences_and_metadata(self):
        """Test UserRecipe with optional preferences and metadata."""
        recipe_data = {
            "name": "FullRecipe",
            "prd": {"content": "Complete PRD"},
            "instructions": {
                "diagrams": [{"type": "sequence_diagram"}],
                "documentation": {
                    "style": "technical",
                    "audience": "developers"
                }
            },
            "preferences": {
                "default_framework": "d2",
                "diagram_style": "clean",
                "color_scheme": "modern"
            },
            "metadata": {
                "created_by": "test_user",
                "project": "test_project",
                "tags": ["api", "microservices"]
            }
        }

        recipe = UserRecipe(**recipe_data)
        assert recipe.preferences.default_framework == "d2"
        assert recipe.metadata["created_by"] == "test_user"
        assert recipe.instructions.documentation.style == "technical"
