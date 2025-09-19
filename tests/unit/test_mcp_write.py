"""
Test MCP write operations for processed recipe data.

This test file has been updated to test the actual MCP server implementation:
- Tests _write_processed_recipe_impl() function from mcp.server
- Removed references to non-existent MCPWriter class
- Uses proper async testing with pytest.mark.asyncio
- Tests validation success and error cases
- Uses proper mocking for file operations with mock_open
- Validates ProcessedRecipe model structure compliance
"""

import asyncio
from datetime import datetime
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, mock_open, patch

import pytest
import yaml

from t2d_kit.mcp.server import _write_processed_recipe_impl
from t2d_kit.models.base import ContentType, DiagramType, FrameworkType, OutputFormat
from t2d_kit.models.content import ContentFile
from t2d_kit.models.diagram import DiagramSpecification
from t2d_kit.models.processed_recipe import DiagramReference, OutputConfig, ProcessedRecipe


class TestMCPWriteProcessedRecipe:
    """Test cases for the write_processed_recipe MCP tool."""

    def create_valid_processed_data(self) -> dict[str, Any]:
        """Create valid test data for ProcessedRecipe."""
        return {
            "name": "Test Recipe",
            "version": "1.0.0",
            "source_recipe": "recipes/test.yaml",
            "generated_at": datetime.now().isoformat(),
            "content_files": [
                {
                    "id": "readme",
                    "path": "docs/README.md",
                    "type": "documentation",
                    "agent": "t2d-markdown-maintainer",
                    "base_prompt": "Generate comprehensive documentation for this recipe.",
                    "diagram_refs": ["arch-diagram"],
                    "title": "Project Documentation",
                    "last_updated": datetime.now().isoformat(),
                }
            ],
            "diagram_specs": [
                {
                    "id": "arch-diagram",
                    "type": "architecture",
                    "framework": "d2",
                    "agent": "t2d-d2-generator",
                    "title": "Architecture Diagram",
                    "instructions": "Create a comprehensive system architecture diagram showing all components.",
                    "output_file": "docs/assets/architecture.d2",
                    "output_formats": ["svg", "png"],
                }
            ],
            "diagram_refs": [
                {
                    "id": "arch-diagram",
                    "title": "Architecture Diagram",
                    "type": "architecture",
                    "expected_path": "docs/assets/architecture.d2",
                    "actual_paths": {"svg": "docs/assets/architecture.svg"},
                    "description": "System architecture overview",
                    "status": "generated",
                }
            ],
            "outputs": {
                "assets_dir": "docs/assets",
                "mkdocs": {"theme": "material"},
                "marp": {"theme": "default"},
            },
            "generation_notes": ["Generated successfully", "All diagrams created"],
        }

    @pytest.mark.asyncio
    async def test_write_processed_recipe_success(self):
        """Test successful writing of processed recipe data."""
        processed_data = self.create_valid_processed_data()
        file_path = "/tmp/test_recipe.t2d.yaml"

        with patch("builtins.open", mock_open()) as mock_file, \
             patch("pathlib.Path.mkdir") as mock_mkdir:

            result = await _write_processed_recipe_impl(file_path, processed_data)

            # Verify the result
            assert result["success"] is True
            assert result["file_path"] == str(Path(file_path).absolute())
            assert "Processed recipe written to" in result["message"]

            # Verify file operations
            mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
            mock_file.assert_called_once_with(Path(file_path), "w")

            # Verify YAML was written
            handle = mock_file.return_value.__enter__.return_value
            handle.write.assert_called()

            # Verify the written content is valid YAML
            written_content = ''.join(call.args[0] for call in handle.write.call_args_list)
            parsed_yaml = yaml.safe_load(written_content)
            assert parsed_yaml is not None
            assert parsed_yaml["name"] == "Test Recipe"

    @pytest.mark.asyncio
    async def test_write_processed_recipe_validation_error(self):
        """Test write_processed_recipe with invalid data."""
        # Create invalid data - missing required fields
        invalid_data = {
            "name": "Test Recipe",
            # Missing required fields like version, source_recipe, etc.
        }

        result = await _write_processed_recipe_impl("/tmp/test.yaml", invalid_data)

        # Should return validation error
        assert "error" in result
        assert result["error"] == "Processed recipe validation failed"
        assert "details" in result
        assert isinstance(result["details"], list)

    @pytest.mark.asyncio
    async def test_write_processed_recipe_inconsistent_diagrams(self):
        """Test validation error when diagram specs and refs are inconsistent."""
        processed_data = self.create_valid_processed_data()

        # Add a diagram ref that doesn't have a corresponding spec
        processed_data["diagram_refs"].append({
            "id": "missing-spec",
            "title": "Missing Spec",
            "type": "flowchart",
            "expected_path": "docs/missing.d2",
            "status": "pending",
        })

        result = await _write_processed_recipe_impl("/tmp/test.yaml", processed_data)

        # Should return validation error
        assert "error" in result
        assert result["error"] == "Processed recipe validation failed"
        assert "details" in result

    @pytest.mark.asyncio
    async def test_write_processed_recipe_invalid_content_diagram_refs(self):
        """Test validation error when content files reference invalid diagrams."""
        processed_data = self.create_valid_processed_data()

        # Make content file reference non-existent diagram
        processed_data["content_files"][0]["diagram_refs"] = ["non-existent-diagram"]

        result = await _write_processed_recipe_impl("/tmp/test.yaml", processed_data)

        # Should return validation error
        assert "error" in result
        assert result["error"] == "Processed recipe validation failed"
        assert "details" in result

    @pytest.mark.asyncio
    async def test_write_processed_recipe_with_minimal_data(self):
        """Test writing with minimal valid data."""
        minimal_data = {
            "name": "Minimal Recipe",
            "version": "1.0.0",
            "source_recipe": "test.yaml",
            "generated_at": datetime.now().isoformat(),
            "content_files": [
                {
                    "id": "simple",
                    "path": "simple.md",
                    "type": "documentation",
                    "agent": "t2d-markdown-maintainer",
                    "base_prompt": "Create simple documentation for this test case.",
                    "last_updated": datetime.now().isoformat(),
                }
            ],
            "diagram_specs": [
                {
                    "id": "simple-diagram",
                    "type": "flowchart",
                    "agent": "t2d-mermaid-generator",
                    "title": "Simple Flowchart",
                    "instructions": "Create a basic flowchart showing the process flow.",
                    "output_file": "simple.mmd",
                    "output_formats": ["svg"],
                }
            ],
            "diagram_refs": [
                {
                    "id": "simple-diagram",
                    "title": "Simple Flowchart",
                    "type": "flowchart",
                    "expected_path": "simple.mmd",
                    "status": "pending",
                }
            ],
            "outputs": {"assets_dir": "assets"},
        }

        with patch("builtins.open", mock_open()), \
             patch("pathlib.Path.mkdir"):

            result = await _write_processed_recipe_impl("/tmp/minimal.yaml", minimal_data)

            assert result["success"] is True
            assert "minimal.yaml" in result["file_path"]

    @pytest.mark.asyncio
    async def test_write_processed_recipe_directory_creation(self):
        """Test that parent directories are created."""
        processed_data = self.create_valid_processed_data()
        file_path = "/tmp/deep/nested/path/recipe.yaml"

        with patch("builtins.open", mock_open()), \
             patch("pathlib.Path.mkdir") as mock_mkdir:

            result = await _write_processed_recipe_impl(file_path, processed_data)

            assert result["success"] is True
            mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)

    @pytest.mark.asyncio
    async def test_write_processed_recipe_yaml_formatting(self):
        """Test that YAML is properly formatted."""
        processed_data = self.create_valid_processed_data()

        with patch("builtins.open", mock_open()), \
             patch("pathlib.Path.mkdir"), \
             patch("yaml.safe_dump") as mock_yaml_dump:

            await _write_processed_recipe_impl("/tmp/test.yaml", processed_data)

            # Verify yaml.safe_dump was called with correct parameters
            mock_yaml_dump.assert_called_once()
            call_args = mock_yaml_dump.call_args

            # Check that the processed recipe model was passed
            assert call_args[0][0] is not None  # First argument is the data

            # Check formatting options
            kwargs = call_args[1]
            assert kwargs["default_flow_style"] is False
            assert kwargs["sort_keys"] is False
            assert kwargs["width"] == 120

    def test_processed_recipe_model_validation(self):
        """Test that ProcessedRecipe model validates correctly with our test data."""
        processed_data = self.create_valid_processed_data()

        # This should not raise an exception
        recipe = ProcessedRecipe(**processed_data)

        assert recipe.name == "Test Recipe"
        assert recipe.version == "1.0.0"
        assert len(recipe.content_files) == 1
        assert len(recipe.diagram_specs) == 1
        assert len(recipe.diagram_refs) == 1
        assert recipe.diagram_specs[0].id == recipe.diagram_refs[0].id
