"""
T009: Test MCP read operations for user recipes.
"""

import tempfile
from pathlib import Path
from unittest.mock import mock_open, patch

import pytest
import yaml
from pydantic import ValidationError

from t2d_kit.mcp.server import read_user_recipe
from t2d_kit.models.user_recipe import UserRecipe


class TestMCPRead:
    """Test cases for MCP read operations."""

    @pytest.mark.asyncio
    async def test_read_user_recipe_success(self):
        """Test successful reading of user recipe from YAML file."""
        # Valid recipe data
        recipe_data = {
            "name": "TestRecipe",
            "version": "1.0.0",
            "prd": {
                "content": "This is a test PRD content",
                "format": "markdown"
            },
            "instructions": {
                "diagrams": [
                    {
                        "type": "architecture",
                        "description": "System architecture overview"
                    }
                ]
            }
        }

        yaml_content = yaml.safe_dump(recipe_data)

        with patch("pathlib.Path.exists", return_value=True), \
             patch("builtins.open", mock_open(read_data=yaml_content)):

            result = await read_user_recipe.fn("test_recipe.yaml")

            assert isinstance(result, dict)
            assert result["name"] == "TestRecipe"
            assert result["version"] == "1.0.0"
            assert "prd" in result
            assert "instructions" in result

    @pytest.mark.asyncio
    async def test_read_user_recipe_file_not_found(self):
        """Test reading non-existent user recipe file."""
        with patch("pathlib.Path.exists", return_value=False):
            with pytest.raises(FileNotFoundError, match="Recipe file not found"):
                await read_user_recipe.fn("nonexistent.yaml")

    @pytest.mark.asyncio
    async def test_read_user_recipe_invalid_yaml(self):
        """Test handling of invalid YAML content."""
        invalid_yaml = "invalid: yaml: content: ["

        with patch("pathlib.Path.exists", return_value=True), \
             patch("builtins.open", mock_open(read_data=invalid_yaml)):

            with pytest.raises(yaml.YAMLError):
                await read_user_recipe.fn("invalid.yaml")

    @pytest.mark.asyncio
    async def test_read_user_recipe_validation_error(self):
        """Test handling of recipe data that fails validation."""
        # Invalid recipe data (missing required fields)
        invalid_recipe_data = {
            "name": "TestRecipe",
            # Missing required 'prd' and 'instructions' fields
        }

        yaml_content = yaml.safe_dump(invalid_recipe_data)

        with patch("pathlib.Path.exists", return_value=True), \
             patch("builtins.open", mock_open(read_data=yaml_content)):

            result = await read_user_recipe.fn("invalid_recipe.yaml")

            assert "error" in result
            assert result["error"] == "Recipe validation failed"
            assert "details" in result

    @pytest.mark.asyncio
    async def test_read_user_recipe_minimal_valid(self):
        """Test reading a minimal but valid recipe."""
        minimal_recipe = {
            "name": "MinimalRecipe",
            "prd": {
                "content": "Minimal PRD content"
            },
            "instructions": {
                "diagrams": [
                    {
                        "type": "simple_diagram"
                    }
                ]
            }
        }

        yaml_content = yaml.safe_dump(minimal_recipe)

        with patch("pathlib.Path.exists", return_value=True), \
             patch("builtins.open", mock_open(read_data=yaml_content)):

            result = await read_user_recipe.fn("minimal.yaml")

            assert result["name"] == "MinimalRecipe"
            assert "error" not in result

    @pytest.mark.asyncio
    async def test_read_user_recipe_with_real_file(self):
        """Test reading from an actual temporary file."""
        recipe_data = {
            "name": "RealFileTest",
            "version": "2.0.0",
            "prd": {
                "content": "Real file test content",
                "format": "markdown"
            },
            "instructions": {
                "diagrams": [
                    {
                        "type": "sequence",
                        "description": "User flow diagram"
                    }
                ],
                "documentation": {
                    "style": "technical",
                    "audience": "developers"
                }
            }
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.safe_dump(recipe_data, f)
            temp_path = f.name

        try:
            result = await read_user_recipe.fn(temp_path)

            assert result["name"] == "RealFileTest"
            assert result["version"] == "2.0.0"
            assert len(result["instructions"]["diagrams"]) == 1
            assert result["instructions"]["diagrams"][0]["type"] == "sequence"
        finally:
            Path(temp_path).unlink()

    @pytest.mark.asyncio
    async def test_read_user_recipe_complex_structure(self):
        """Test reading a recipe with complex nested structure."""
        complex_recipe = {
            "name": "ComplexRecipe",
            "version": "1.5.0",
            "prd": {
                "content": "Complex system requirements",
                "format": "markdown",
                "sections": ["overview", "requirements", "architecture"]
            },
            "instructions": {
                "diagrams": [
                    {
                        "type": "architecture",
                        "description": "High-level architecture",
                        "framework_preference": "d2"
                    },
                    {
                        "type": "sequence",
                        "description": "User interaction flow"
                    }
                ],
                "documentation": {
                    "style": "technical",
                    "audience": "developers and architects",
                    "sections": ["introduction", "design", "implementation"],
                    "detail_level": "detailed",
                    "include_code_examples": True
                },
                "presentation": {
                    "audience": "stakeholders",
                    "max_slides": 20,
                    "style": "executive"
                }
            },
            "preferences": {
                "default_framework": "d2",
                "diagram_style": "modern",
                "color_scheme": "blue"
            },
            "metadata": {
                "author": "test_user",
                "created": "2024-01-01"
            }
        }

        yaml_content = yaml.safe_dump(complex_recipe)

        with patch("pathlib.Path.exists", return_value=True), \
             patch("builtins.open", mock_open(read_data=yaml_content)):

            result = await read_user_recipe.fn("complex.yaml")

            # Check if there was a validation error
            if "error" in result:
                pytest.fail(f"Validation error: {result}")

            assert result["name"] == "ComplexRecipe"
            assert result["version"] == "1.5.0"
            assert len(result["instructions"]["diagrams"]) == 2
            assert result["preferences"]["default_framework"] == "d2"
            assert result["metadata"]["author"] == "test_user"
