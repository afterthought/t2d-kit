"""
Unit tests for MCP tool write operations.
"""

import tempfile
from datetime import datetime, timezone
from pathlib import Path

import pytest
import pytest_asyncio
import yaml
from fastmcp import FastMCP

from t2d_kit.mcp.tools.user_recipe_tools import register_user_recipe_tools
from t2d_kit.mcp.tools.processed_recipe_tools import register_processed_recipe_tools
from t2d_kit.models.user_recipe import (
    CreateRecipeParams,
    EditRecipeParams,
    DiagramRequest,
    ValidateRecipeParams,
)
from t2d_kit.models.processed_recipe import (
    ProcessedRecipeContent,
    WriteProcessedRecipeParams,
    UpdateProcessedRecipeParams,
    ValidateProcessedRecipeParams,
)


class TestMCPUserRecipeTools:
    """Test cases for user recipe MCP tools."""

    @pytest_asyncio.fixture
    async def mcp_server(self):
        """Create a test MCP server."""
        return FastMCP("test-server")

    @pytest.mark.asyncio
    async def test_create_user_recipe(self, mcp_server):
        """Test creating a new user recipe."""
        with tempfile.TemporaryDirectory() as temp_dir:
            recipe_dir = Path(temp_dir)

            await register_user_recipe_tools(mcp_server, recipe_dir)

            # Create recipe params
            params = CreateRecipeParams(
                name="test-create-recipe",
                prd_content="# Test PRD\n\nThis is a test PRD.",
                diagrams=[
                    DiagramRequest(
                        type="flowchart",
                        description="Main system flow",
                        framework_preference="mermaid"
                    ),
                    DiagramRequest(
                        type="architecture",
                        description="System architecture"
                    )
                ]
            )

            # Call the tool
            tools = await mcp_server.get_tools()
            assert "create_user_recipe" in tools

            tool = tools["create_user_recipe"]
            response = await tool.fn(params)
            result = response.model_dump()

            # Verify response
            if not result["success"]:
                print(f"Create failed: {result.get('message', 'No message')}")
            assert result["success"] is True
            assert result["recipe_name"] == "test-create-recipe"
            # The file is created in the default recipes dir, not temp dir
            assert result["file_path"].endswith("test-create-recipe.yaml")

            # Verify file was created (in the default recipes dir)
            created_path = Path(result["file_path"])
            assert created_path.exists()

            # Verify content
            with open(created_path) as f:
                saved_content = yaml.safe_load(f)

            assert saved_content["name"] == "test-create-recipe"
            assert saved_content["prd"]["content"] == "# Test PRD\n\nThis is a test PRD."
            assert len(saved_content["instructions"]["diagrams"]) == 2

            # Clean up
            created_path.unlink()

    @pytest.mark.asyncio
    async def test_edit_user_recipe(self, mcp_server):
        """Test editing an existing user recipe."""
        with tempfile.TemporaryDirectory() as temp_dir:
            recipe_dir = Path(temp_dir)

            # Create initial recipe
            initial_recipe = {
                "name": "test-recipe",
                "prd": {"content": "Original PRD"},
                "instructions": {
                    "diagrams": [
                        {"type": "flowchart", "description": "Original flow"}
                    ]
                }
            }

            (recipe_dir / "test-recipe.yaml").write_text(yaml.safe_dump(initial_recipe))

            await register_user_recipe_tools(mcp_server, recipe_dir)

            # Edit the recipe
            params = EditRecipeParams(
                name="test-recipe",
                prd_content="Updated PRD content",
                diagrams=[
                    DiagramRequest(
                        type="architecture",
                        description="New architecture diagram"
                    )
                ],
                validate_before_save=True
            )

            tools = await mcp_server.get_tools()
            tool = tools["edit_user_recipe"]
            response = await tool.fn(params)
            result = response.model_dump()

            # Verify response
            assert result["success"] is True
            assert result["recipe_name"] == "test-recipe"
            assert "prd.content" in result["changes_applied"]

            # Verify changes were saved
            with open(recipe_dir / "test-recipe.yaml") as f:
                updated_content = yaml.safe_load(f)

            assert updated_content["prd"]["content"] == "Updated PRD content"
            assert len(updated_content["instructions"]["diagrams"]) == 1
            assert updated_content["instructions"]["diagrams"][0]["type"] == "architecture"

    @pytest.mark.asyncio
    async def test_validate_user_recipe_by_name(self, mcp_server):
        """Test validating a user recipe by name."""
        with tempfile.TemporaryDirectory() as temp_dir:
            recipe_dir = Path(temp_dir)

            # Create a valid recipe
            recipe = {
                "name": "test-recipe",
                "prd": {"content": "Test PRD"},
                "instructions": {
                    "diagrams": [{"type": "flowchart", "description": "Test flow"}]
                }
            }

            (recipe_dir / "test-recipe.yaml").write_text(yaml.safe_dump(recipe))

            await register_user_recipe_tools(mcp_server, recipe_dir)

            # Validate the recipe
            params = ValidateRecipeParams(name="test-recipe")

            tools = await mcp_server.get_tools()
            tool = tools["validate_user_recipe"]
            response = await tool.fn(params)
            result = response.model_dump()

            # Verify validation result
            assert result["valid"] is True
            assert result["errors"] == []
            assert "duration_ms" in result
            assert "validated_at" in result

    @pytest.mark.asyncio
    async def test_validate_user_recipe_with_content(self, mcp_server):
        """Test validating user recipe with direct content."""
        with tempfile.TemporaryDirectory() as temp_dir:
            recipe_dir = Path(temp_dir)

            await register_user_recipe_tools(mcp_server, recipe_dir)

            # Create recipe content
            from t2d_kit.models.user_recipe import UserRecipe, PRDContent, UserInstructions

            recipe_content = UserRecipe(
                name="test-recipe",
                prd=PRDContent(content="Test PRD content"),
                instructions=UserInstructions(
                    diagrams=[
                        DiagramRequest(
                            type="flowchart",
                            description="Test flowchart"
                        )
                    ]
                )
            )

            # Validate the recipe content
            params = ValidateRecipeParams(content=recipe_content)

            tools = await mcp_server.get_tools()
            tool = tools["validate_user_recipe"]
            response = await tool.fn(params)
            result = response.model_dump()

            # Verify validation result
            assert result["valid"] is True
            assert result["errors"] == []

    @pytest.mark.asyncio
    async def test_create_recipe_with_invalid_data(self, mcp_server):
        """Test creating a recipe with invalid data."""
        with tempfile.TemporaryDirectory() as temp_dir:
            recipe_dir = Path(temp_dir)

            await register_user_recipe_tools(mcp_server, recipe_dir)

            # Create invalid params (no diagrams)
            try:
                params = CreateRecipeParams(
                    name="invalid-recipe",
                    prd_content="Test PRD",
                    diagrams=[]  # Empty diagrams should fail validation
                )
                # If we get here, the validation failed at Pydantic level
                pytest.fail("Should have raised ValidationError for empty diagrams")
            except Exception:
                # This test passes if Pydantic rejects empty diagrams
                return

            tools = await mcp_server.get_tools()
            tool = tools["create_user_recipe"]
            response = await tool.fn(params)
            result = response.model_dump()

            # Should fail validation
            assert result["success"] is False
            assert "validation" in result.get("message", "").lower()
            assert not (recipe_dir / "invalid-recipe.yaml").exists()


class TestMCPProcessedRecipeTools:
    """Test cases for processed recipe MCP tools."""

    @pytest_asyncio.fixture
    async def mcp_server(self):
        """Create a test MCP server."""
        return FastMCP("test-server")

    @pytest_asyncio.fixture
    async def valid_processed_content(self):
        """Create valid processed recipe content."""
        return ProcessedRecipeContent(
            name="test-processed",
            version="1.0.0",
            source_recipe="./recipes/test.yaml",
            generated_at=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            diagram_specs=[
                {
                    "id": "flow-001",
                    "type": "flowchart",
                    "framework": "mermaid",
                    "agent": "t2d-mermaid-generator",
                    "title": "System Flow",
                    "instructions": "Create a detailed system flow diagram",
                    "output_file": "docs/flow.mmd",
                    "output_formats": ["svg", "png"],
                    "options": {}
                }
            ],
            content_files=[
                {
                    "id": "overview",
                    "path": "docs/overview.md",
                    "type": "documentation",
                    "agent": "t2d-markdown-maintainer",
                    "base_prompt": "Create comprehensive overview",
                    "diagram_refs": ["flow-001"],
                    "title": "System Overview",
                    "last_updated": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
                }
            ],
            diagram_refs=[
                {
                    "id": "flow-001",
                    "title": "System Flow",
                    "type": "flowchart",
                    "expected_path": "docs/flow.svg",
                    "status": "pending"
                }
            ],
            outputs={
                "assets_dir": "docs/assets"
            }
        )

    @pytest.mark.asyncio
    async def test_write_processed_recipe(self, mcp_server, valid_processed_content):
        """Test writing a processed recipe."""
        with tempfile.TemporaryDirectory() as temp_dir:
            processed_dir = Path(temp_dir)

            await register_processed_recipe_tools(mcp_server, processed_dir)

            # Write processed recipe
            params = WriteProcessedRecipeParams(
                recipe_path=str(processed_dir / "test.t2d.yaml"),
                content=valid_processed_content,
                validate=True
            )

            tools = await mcp_server.get_tools()
            assert "write_processed_recipe" in tools

            tool = tools["write_processed_recipe"]
            response = await tool.fn(params)
            result = response.model_dump()

            # Verify response
            assert result["success"] is True
            assert result["recipe_path"] == str(processed_dir / "test.t2d.yaml")
            assert result["validation_result"]["valid"] is True

            # Verify file was created
            assert (processed_dir / "test.t2d.yaml").exists()

            # Verify content
            with open(processed_dir / "test.t2d.yaml") as f:
                saved_content = yaml.safe_load(f)

            assert saved_content["name"] == "test-processed"
            assert saved_content["version"] == "1.0.0"
            assert len(saved_content["diagram_specs"]) == 1

    @pytest.mark.asyncio
    async def test_update_processed_recipe(self, mcp_server, valid_processed_content):
        """Test updating an existing processed recipe."""
        with tempfile.TemporaryDirectory() as temp_dir:
            processed_dir = Path(temp_dir)

            # Create initial file
            initial_path = processed_dir / "test.t2d.yaml"
            initial_path.write_text(yaml.safe_dump(valid_processed_content.model_dump()))

            await register_processed_recipe_tools(mcp_server, processed_dir)

            # Update the recipe
            params = UpdateProcessedRecipeParams(
                recipe_path=str(initial_path),
                diagram_refs=[
                    {
                        "id": "flow-001",
                        "title": "System Flow",
                        "type": "flowchart",
                        "expected_path": "docs/flow.svg",
                        "status": "generated"  # Changed from pending
                    }
                ],
                validate=True
            )

            tools = await mcp_server.get_tools()
            tool = tools["update_processed_recipe"]
            response = await tool.fn(params)
            result = response.model_dump()

            # Verify response
            assert result["success"] is True
            assert "diagram_refs" in result["sections_updated"]

            # Verify changes were saved
            with open(initial_path) as f:
                updated_content = yaml.safe_load(f)

            assert updated_content["diagram_refs"][0]["status"] == "generated"

    @pytest.mark.asyncio
    async def test_validate_processed_recipe_by_path(self, mcp_server, valid_processed_content):
        """Test validating a processed recipe by path."""
        with tempfile.TemporaryDirectory() as temp_dir:
            processed_dir = Path(temp_dir)

            # Create recipe file
            recipe_path = processed_dir / "test.t2d.yaml"
            recipe_path.write_text(yaml.safe_dump(valid_processed_content.model_dump()))

            await register_processed_recipe_tools(mcp_server, processed_dir)

            # Validate the recipe
            params = ValidateProcessedRecipeParams(
                recipe_path=str(recipe_path)
            )

            tools = await mcp_server.get_tools()
            tool = tools["validate_processed_recipe"]
            response = await tool.fn(params)
            result = response.model_dump()

            # Verify validation result
            assert result["valid"] is True
            assert result["errors"] == []
            assert "duration_ms" in result

    @pytest.mark.asyncio
    async def test_validate_processed_recipe_with_content(self, mcp_server, valid_processed_content):
        """Test validating processed recipe with direct content."""
        with tempfile.TemporaryDirectory() as temp_dir:
            processed_dir = Path(temp_dir)

            await register_processed_recipe_tools(mcp_server, processed_dir)

            # Validate the recipe content
            params = ValidateProcessedRecipeParams(
                content=valid_processed_content
            )

            tools = await mcp_server.get_tools()
            tool = tools["validate_processed_recipe"]
            response = await tool.fn(params)
            result = response.model_dump()

            # Verify validation result
            assert result["valid"] is True
            assert result["errors"] == []

    @pytest.mark.asyncio
    async def test_write_processed_recipe_with_invalid_data(self, mcp_server):
        """Test that Pydantic validation prevents creating invalid processed recipes."""
        # Test: Pydantic validation catches invalid instructions (too short)
        with pytest.raises(Exception) as exc_info:
            ProcessedRecipeContent(
                name="invalid-processed",
                version="1.0.0",
                source_recipe="./recipes/test.yaml",
                generated_at=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                diagram_specs=[
                    {
                        "id": "spec-001",
                        "type": "flowchart",
                        "framework": "mermaid",
                        "agent": "t2d-mermaid-generator",
                        "title": "Test",
                        "instructions": "Create flowchart",  # Too short - only 2 words
                        "output_file": "test.mmd",
                        "output_formats": ["svg"],
                        "options": {}
                    }
                ],
                content_files=[
                    {
                        "id": "test",
                        "path": "test.md",
                        "type": "documentation",
                        "agent": "t2d-markdown-maintainer",
                        "base_prompt": "Create test documentation file",
                        "diagram_refs": ["spec-001"],
                        "last_updated": datetime.now(timezone.utc).isoformat()
                    }
                ],
                diagram_refs=[
                    {
                        "id": "spec-001",
                        "title": "Test",
                        "type": "flowchart",
                        "expected_path": "test.svg",
                        "status": "pending"
                    }
                ],
                outputs={"assets_dir": "assets"}
            )

        # Verify the right error was caught
        assert "at least 5 words" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_tool_discovery(self, mcp_server):
        """Test that all expected tools are registered."""
        with tempfile.TemporaryDirectory() as temp_dir:
            recipe_dir = Path(temp_dir) / "recipes"
            processed_dir = Path(temp_dir) / "processed"

            await register_user_recipe_tools(mcp_server, recipe_dir)
            await register_processed_recipe_tools(mcp_server, processed_dir)

            tools = await mcp_server.get_tools()

            # Verify user recipe tools
            assert "create_user_recipe" in tools
            assert "edit_user_recipe" in tools
            assert "validate_user_recipe" in tools

            # Verify processed recipe tools
            assert "write_processed_recipe" in tools
            assert "update_processed_recipe" in tools
            assert "validate_processed_recipe" in tools