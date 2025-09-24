"""
Unit tests for MCP resource read operations.
"""

import tempfile
from pathlib import Path

import pytest
import pytest_asyncio
import yaml
from fastmcp import FastMCP

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

            # Get the resource and call it
            resources = await mcp_server.get_resources()
            assert "user-recipes://" in resources

            resource = resources["user-recipes://"]
            response = await resource.fn()
            content = response["content"]

            assert content["total_count"] == 0
            assert content["recipes"] == []
            assert content["directory"] == str(recipe_dir.absolute())

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

            # Get the resource and call it
            resources = await mcp_server.get_resources()
            resource = resources["user-recipes://"]
            response = await resource.fn()
            content = response["content"]

            assert content["total_count"] == 2
            assert len(content["recipes"]) == 2

            # Check recipe summaries
            recipe_names = [r["name"] for r in content["recipes"]]
            assert "recipe1" in recipe_names
            assert "recipe2" in recipe_names

            # Verify .t2d.yaml was ignored
            assert "processed" not in recipe_names

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

            # Get the specific recipe resource
            resources = await mcp_server.get_resources()
            assert "user-recipes://test-recipe" in resources

            resource = resources["user-recipes://test-recipe"]
            response = await resource.fn()
            content = response["content"]

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

            # Get the resource and call it
            resources = await mcp_server.get_resources()
            assert "processed-recipes://" in resources

            resource = resources["processed-recipes://"]
            response = await resource.fn()
            content = response["content"]

            assert content["total_count"] == 1
            assert len(content["recipes"]) == 1

            recipe = content["recipes"][0]
            assert recipe["name"] == "test1"
            assert recipe["diagram_count"] == 1
            assert recipe["content_file_count"] == 1

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

            # Get the specific processed recipe resource
            resources = await mcp_server.get_resources()
            assert "processed-recipes://test-processed" in resources

            resource = resources["processed-recipes://test-processed"]
            response = await resource.fn()
            content = response["content"]

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

            # List recipes
            resources = await mcp_server.get_resources()
            resource = resources["user-recipes://"]
            response = await resource.fn()
            content = response["content"]

            # Find recipes by name
            valid = next(r for r in content["recipes"] if r["name"] == "valid")
            invalid = next(r for r in content["recipes"] if r["name"] == "invalid")

            assert valid["validation_status"] == "valid"
            assert invalid["validation_status"] == "invalid"

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

            # List recipes
            resources = await mcp_server.get_resources()
            resource = resources["user-recipes://"]
            response = await resource.fn()
            content = response["content"]

            recipe_summary = content["recipes"][0]
            assert recipe_summary["diagram_count"] == 3

    @pytest.mark.asyncio
    async def test_nonexistent_recipe_directory(self, mcp_server):
        """Test behavior when recipe directory doesn't exist."""
        non_existent_dir = Path("/tmp/does-not-exist-12345")

        await register_user_recipe_resources(mcp_server, non_existent_dir)

        # Should still register the resource
        resources = await mcp_server.get_resources()
        assert "user-recipes://" in resources

        # But return empty list
        resource = resources["user-recipes://"]
        response = await resource.fn()
        content = response["content"]

        assert content["total_count"] == 0
        assert content["recipes"] == []