"""
Unit tests for MCP resource read operations.
"""

import tempfile
from pathlib import Path
from unittest.mock import AsyncMock

import pytest
import pytest_asyncio
import yaml
from fastmcp import FastMCP, Context

from t2d_kit.mcp.resources.user_recipes import register_user_recipe_resources
from t2d_kit.mcp.resources.processed_recipes import register_processed_recipe_resources


class TestMCPResourceRead:
    """Test cases for MCP resource read operations."""

    @pytest_asyncio.fixture
    async def mcp_server(self):
        """Create a test MCP server."""
        return FastMCP("test-server")

    @pytest.mark.asyncio
    async def test_list_user_recipes_empty_directory(self, mcp_server):
        """Test listing user recipes when directory is empty."""
        with tempfile.TemporaryDirectory() as temp_dir:
            recipe_dir = Path(temp_dir)

            await register_user_recipe_resources(mcp_server, recipe_dir)

            # Get all resource templates - should have the template registered
            templates = await mcp_server.get_resource_templates()

            # Check that the resource template is registered with file:// URI
            # The template key should be the absolute path
            expected_template = f"file://{recipe_dir.resolve()}/{{name}}.yaml"
            assert expected_template in templates

    @pytest.mark.asyncio
    async def test_list_user_recipes_with_files(self, mcp_server):
        """Test listing user recipes with actual recipe files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            recipe_dir = Path(temp_dir)

            # Create test recipe files
            recipe1 = {
                "name": "test-recipe-1",
                "prd": {"content": "Test PRD 1"},
                "instructions": {
                    "diagrams": [{"type": "flowchart", "description": "Test flow"}]
                }
            }
            recipe2 = {
                "name": "test-recipe-2",
                "prd": {"content": "Test PRD 2"},
                "instructions": {
                    "diagrams": [{"type": "architecture", "description": "Test arch"}]
                }
            }

            (recipe_dir / "recipe1.yaml").write_text(yaml.safe_dump(recipe1))
            (recipe_dir / "recipe2.yaml").write_text(yaml.safe_dump(recipe2))
            # Create a .t2d.yaml file that should be ignored
            (recipe_dir / "processed.t2d.yaml").write_text(yaml.safe_dump({}))

            await register_user_recipe_resources(mcp_server, recipe_dir)

            # Get all resource templates
            templates = await mcp_server.get_resource_templates()

            # Check that the resource template is registered with file:// URI
            # The template key should be the absolute path
            expected_template = f"file://{recipe_dir.resolve()}/{{name}}.yaml"
            assert expected_template in templates

            # Test reading specific recipes through the template
            template = templates[expected_template]

            # Read recipe1
            content1 = await template.fn("recipe1")
            assert content1["name"] == "recipe1"
            assert content1["content"]["name"] == "test-recipe-1"

            # Read recipe2
            content2 = await template.fn("recipe2")
            assert content2["name"] == "recipe2"
            assert content2["content"]["name"] == "test-recipe-2"

    @pytest.mark.asyncio
    async def test_get_specific_user_recipe(self, mcp_server):
        """Test getting a specific user recipe by name."""
        with tempfile.TemporaryDirectory() as temp_dir:
            recipe_dir = Path(temp_dir)

            # Create a test recipe
            recipe_data = {
                "name": "test-recipe",
                "version": "1.0.0",
                "prd": {"content": "Test PRD content"},
                "instructions": {
                    "diagrams": [
                        {"type": "flowchart", "description": "Test flowchart"}
                    ],
                    "documentation": {
                        "style": "technical",
                        "audience": "developers"
                    }
                }
            }

            (recipe_dir / "test-recipe.yaml").write_text(yaml.safe_dump(recipe_data))

            await register_user_recipe_resources(mcp_server, recipe_dir)

            # Get the resource template
            templates = await mcp_server.get_resource_templates()
            expected_template = f"file://{recipe_dir.resolve()}/{{name}}.yaml"
            assert expected_template in templates

            # Read the recipe through the template
            template = templates[expected_template]
            content = await template.fn("test-recipe")

            # Validate the content structure

            assert content["name"] == "test-recipe"
            assert content["content"]["name"] == "test-recipe"
            assert content["content"]["version"] == "1.0.0"
            assert "raw_yaml" in content
            assert "metadata" in content
            assert "validation_result" in content

    @pytest.mark.asyncio
    async def test_list_processed_recipes(self, mcp_server):
        """Test listing processed recipes."""
        with tempfile.TemporaryDirectory() as temp_dir:
            processed_dir = Path(temp_dir)

            # Create test processed recipe files
            processed1 = {
                "name": "test-processed-1",
                "version": "1.0.0",
                "source_recipe": "./recipes/test1.yaml",
                "generated_at": "2024-01-01T10:00:00Z",
                "diagram_specs": [
                    {
                        "id": "flow-001",
                        "type": "flowchart",
                        "framework": "mermaid",
                        "agent": "t2d-mermaid-generator",
                        "title": "Test Flow",
                        "instructions": "Create a flowchart",
                        "output_file": "docs/flow.mmd",
                        "output_formats": ["svg"],
                        "options": {}
                    }
                ],
                "content_files": [
                    {
                        "id": "readme",
                        "path": "README.md",
                        "type": "documentation",
                        "agent": "t2d-markdown-maintainer",
                        "base_prompt": "Create readme",
                        "diagram_refs": ["flow-001"],
                        "last_updated": "2024-01-01T10:00:00Z"
                    }
                ],
                "diagram_refs": [
                    {
                        "id": "flow-001",
                        "title": "Test Flow",
                        "type": "flowchart",
                        "expected_path": "docs/flow.svg",
                        "status": "pending"
                    }
                ],
                "outputs": {
                    "assets_dir": "docs/assets"
                }
            }

            (processed_dir / "test1.t2d.yaml").write_text(yaml.safe_dump(processed1))

            await register_processed_recipe_resources(mcp_server, processed_dir)

            # Get the resource template
            templates = await mcp_server.get_resource_templates()
            expected_template = f"file://{processed_dir.resolve()}/{{name}}.t2d.yaml"
            assert expected_template in templates

            # Read the recipe through the template
            template = templates[expected_template]
            content = await template.fn("test1")

            # Validate the content
            assert content["name"] == "test1"
            assert content["metadata"]["diagram_count"] == 1
            assert content["metadata"]["content_file_count"] == 1

    @pytest.mark.asyncio
    async def test_get_specific_processed_recipe(self, mcp_server):
        """Test getting a specific processed recipe."""
        with tempfile.TemporaryDirectory() as temp_dir:
            processed_dir = Path(temp_dir)

            # Create a test processed recipe
            processed_data = {
                "name": "test-processed",
                "version": "1.0.0",
                "source_recipe": "./recipes/test.yaml",
                "generated_at": "2024-01-01T10:00:00Z",
                "diagram_specs": [
                    {
                        "id": "arch-001",
                        "type": "architecture",
                        "framework": "d2",
                        "agent": "t2d-d2-generator",
                        "title": "System Architecture",
                        "instructions": "Create architecture diagram",
                        "output_file": "docs/arch.d2",
                        "output_formats": ["svg", "png"],
                        "options": {}
                    }
                ],
                "content_files": [
                    {
                        "id": "overview",
                        "path": "docs/overview.md",
                        "type": "documentation",
                        "agent": "t2d-markdown-maintainer",
                        "base_prompt": "Create overview",
                        "diagram_refs": ["arch-001"],
                        "last_updated": "2024-01-01T10:00:00Z"
                    }
                ],
                "diagram_refs": [
                    {
                        "id": "arch-001",
                        "title": "System Architecture",
                        "type": "architecture",
                        "expected_path": "docs/arch.svg",
                        "status": "pending"
                    }
                ],
                "outputs": {
                    "assets_dir": "docs/assets"
                }
            }

            (processed_dir / "test-processed.t2d.yaml").write_text(
                yaml.safe_dump(processed_data)
            )

            await register_processed_recipe_resources(mcp_server, processed_dir)

            # Get the resource template
            templates = await mcp_server.get_resource_templates()
            expected_template = f"file://{processed_dir.resolve()}/{{name}}.t2d.yaml"
            assert expected_template in templates

            # Read the recipe through the template
            template = templates[expected_template]
            content = await template.fn("test-processed")

            assert content["name"] == "test-processed"
            assert content["content"]["name"] == "test-processed"
            assert content["content"]["version"] == "1.0.0"
            assert "raw_yaml" in content
            assert "metadata" in content
            assert content["metadata"]["diagram_count"] == 1
            assert content["metadata"]["content_file_count"] == 1

    @pytest.mark.asyncio
    async def test_recipe_validation_status(self, mcp_server):
        """Test that recipe validation status is correctly reported."""
        with tempfile.TemporaryDirectory() as temp_dir:
            recipe_dir = Path(temp_dir)

            # Create valid recipe
            valid_recipe = {
                "name": "valid-recipe",
                "prd": {"content": "Valid PRD"},
                "instructions": {
                    "diagrams": [{"type": "flowchart", "description": "Test"}]
                }
            }

            # Create invalid recipe (missing required fields)
            invalid_recipe = {
                "name": "invalid-recipe"
                # Missing prd and instructions
            }

            (recipe_dir / "valid.yaml").write_text(yaml.safe_dump(valid_recipe))
            (recipe_dir / "invalid.yaml").write_text(yaml.safe_dump(invalid_recipe))

            await register_user_recipe_resources(mcp_server, recipe_dir)

            # Get the resource template
            templates = await mcp_server.get_resource_templates()
            expected_template = f"file://{recipe_dir.resolve()}/{{name}}.yaml"
            assert expected_template in templates

            template = templates[expected_template]

            # Read the valid recipe
            valid_content = await template.fn("valid")
            assert valid_content["validation_result"]["valid"] is True

            # Read the invalid recipe
            invalid_content = await template.fn("invalid")
            assert invalid_content["validation_result"]["valid"] is False

    @pytest.mark.asyncio
    async def test_recipe_with_diagrams_count(self, mcp_server):
        """Test that diagram count is correctly extracted."""
        with tempfile.TemporaryDirectory() as temp_dir:
            recipe_dir = Path(temp_dir)

            # Create recipe with multiple diagrams
            recipe = {
                "name": "multi-diagram",
                "prd": {"content": "Test"},
                "instructions": {
                    "diagrams": [
                        {"type": "flowchart", "description": "Flow 1"},
                        {"type": "architecture", "description": "Arch"},
                        {"type": "sequence", "description": "Seq"}
                    ]
                }
            }

            (recipe_dir / "multi.yaml").write_text(yaml.safe_dump(recipe))

            await register_user_recipe_resources(mcp_server, recipe_dir)

            # Get the resource template
            templates = await mcp_server.get_resource_templates()
            expected_template = f"file://{recipe_dir.resolve()}/{{name}}.yaml"
            assert expected_template in templates

            # Read the recipe through the template
            template = templates[expected_template]
            content = await template.fn("multi")

            # Check the metadata
            assert content["metadata"]["diagram_count"] == 3

    @pytest.mark.asyncio
    async def test_nonexistent_recipe_directory(self, mcp_server):
        """Test behavior when recipe directory doesn't exist."""
        non_existent_dir = Path("/tmp/does-not-exist-12345")

        await register_user_recipe_resources(mcp_server, non_existent_dir)

        # Get all resource templates
        templates = await mcp_server.get_resource_templates()

        # The template should still be registered even if no recipes exist
        # Note: /tmp resolves to /private/tmp on macOS
        resolved_path = non_existent_dir.resolve()
        expected_template = f"file://{resolved_path}/{{name}}.yaml"
        assert expected_template in templates