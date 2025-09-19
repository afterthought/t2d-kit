"""Contract tests for processed recipe MCP tools."""

from datetime import UTC, datetime, timezone
from pathlib import Path

import pytest
import yaml


class TestProcessedRecipeTools:
    """Test processed recipe tool contracts match specifications."""

    @pytest.mark.asyncio
    async def test_write_processed_recipe(self, mcp_server, mcp_context, temp_recipe_dir):
        """Test write_processed_recipe tool contract.

        Contract: specs/002-the-user-can/contracts/mcp_processed_tools.json#WriteProcessedRecipeTool
        """
        from t2d_kit.mcp.tools.processed_recipe_tools import register_processed_recipe_tools
        from t2d_kit.models.processed_recipe import (
            ProcessedRecipeContent,
            WriteProcessedRecipeParams,
        )

        await register_processed_recipe_tools(mcp_server, temp_recipe_dir)

        # Prepare params matching contract
        content = ProcessedRecipeContent(
            name="test-system",
            version="1.0.0",
            source_recipe="./recipes/test-system.yaml",
            generated_at=datetime.now(UTC).isoformat().replace("+00:00", "Z"),
            diagram_specs=[
                {
                    "id": "flow-001",
                    "type": "flowchart",
                    "framework": "mermaid",
                    "agent": "t2d-mermaid-generator",
                    "title": "System Flow",
                    "instructions": "Create a detailed flowchart showing the main system components",
                    "output_file": "docs/assets/flow.mmd",
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
                    "base_prompt": "Create overview",
                    "diagram_refs": ["flow-001"],
                    "title": "Overview",
                    "last_updated": datetime.now(UTC).isoformat().replace("+00:00", "Z")
                }
            ],
            diagram_refs=[
                {
                    "id": "flow-001",
                    "title": "System Flow",
                    "type": "flowchart",
                    "expected_path": "docs/assets/flow.svg",
                    "status": "pending"
                }
            ],
            outputs={
                "assets_dir": "docs/assets",
                "mkdocs": {
                    "config_file": "mkdocs.yml",
                    "site_name": "Test Documentation"
                }
            }
        )

        params = WriteProcessedRecipeParams(
            recipe_path=str(temp_recipe_dir / "test-system.t2d.yaml"),
            content=content,
            validate=True
        )

        # Call tool
        tools = await mcp_server.get_tools()
        tool = tools["write_processed_recipe"]
        response = await tool.fn(params)
        result = response.model_dump()

        # Validate response contract
        assert "success" in result
        assert "recipe_path" in result
        assert "validation_result" in result
        assert "message" in result

        # Validate validation result
        validation = result["validation_result"]
        assert "valid" in validation
        assert "errors" in validation
        assert "warnings" in validation
        assert "validated_at" in validation
        assert "duration_ms" in validation

        # Verify file was created
        if result["success"]:
            recipe_path = Path(result["recipe_path"])
            assert recipe_path.exists()

    @pytest.mark.asyncio
    async def test_update_processed_recipe(self, mcp_server, mcp_context, temp_recipe_dir, mock_processed_yaml_file):
        """Test update_processed_recipe tool contract.

        Contract: specs/002-the-user-can/contracts/mcp_processed_tools.json#UpdateProcessedRecipeTool
        """
        from t2d_kit.mcp.tools.processed_recipe_tools import register_processed_recipe_tools
        from t2d_kit.models.processed_recipe import UpdateProcessedRecipeParams

        await register_processed_recipe_tools(mcp_server, temp_recipe_dir)

        # Update diagram refs to mark as complete
        params = UpdateProcessedRecipeParams(
            recipe_path=str(mock_processed_yaml_file),
            diagram_refs=[
                {
                    "id": "flow-001",
                    "title": "System Flow",
                    "type": "flowchart",
                    "expected_path": "docs/assets/system-flow.svg",
                    "status": "generated"  # Changed from pending
                }
            ],
            generation_notes=["Diagram generation complete"],
            validate=True
        )

        # Call tool
        tools = await mcp_server.get_tools()
        tool = tools["update_processed_recipe"]
        response = await tool.fn(params)
        result = response.model_dump()

        # Validate response contract
        assert "success" in result
        assert "recipe_path" in result
        assert "sections_updated" in result
        assert isinstance(result["sections_updated"], list)
        assert "message" in result

        # If validation requested, should have result
        if params.validate:
            assert "validation_result" in result

    @pytest.mark.asyncio
    async def test_validate_processed_recipe(self, mcp_server, mcp_context, temp_recipe_dir, mock_processed_yaml_file):
        """Test validate_processed_recipe tool contract.

        Contract: specs/002-the-user-can/contracts/mcp_processed_tools.json#ValidateProcessedRecipeTool
        """
        from t2d_kit.mcp.tools.processed_recipe_tools import register_processed_recipe_tools
        from t2d_kit.models.processed_recipe import ValidateProcessedRecipeParams

        await register_processed_recipe_tools(mcp_server, temp_recipe_dir)

        # Test validation by file path
        params = ValidateProcessedRecipeParams(
            recipe_path=str(mock_processed_yaml_file)
        )

        # Call tool
        tools = await mcp_server.get_tools()
        tool = tools["validate_processed_recipe"]
        response = await tool.fn(params)
        result = response.model_dump()

        # Validate response contract (ValidationResult)
        assert "valid" in result
        assert "errors" in result
        assert isinstance(result["errors"], list)
        assert "warnings" in result
        assert isinstance(result["warnings"], list)
        assert "validated_at" in result
        assert "duration_ms" in result

        # Check error structure if present
        if result["errors"]:
            for error in result["errors"]:
                assert "field" in error
                assert "message" in error
                assert "error_type" in error

    @pytest.mark.asyncio
    async def test_validate_with_content(self, mcp_server, mcp_context, sample_processed_recipe):
        """Test validate_processed_recipe with direct content."""
        from t2d_kit.mcp.tools.processed_recipe_tools import register_processed_recipe_tools
        from t2d_kit.models.processed_recipe import (
            ProcessedRecipeContent,
            ValidateProcessedRecipeParams,
        )

        await register_processed_recipe_tools(mcp_server, None)

        # Test validation with content directly
        content = ProcessedRecipeContent(**sample_processed_recipe)
        params = ValidateProcessedRecipeParams(content=content)

        # Call tool
        tools = await mcp_server.get_tools()
        tool = tools["validate_processed_recipe"]
        response = await tool.fn(params)
        result = response.model_dump()

        # Should validate successfully
        assert result["valid"] is True
        assert result["duration_ms"] < 200  # Performance requirement

    @pytest.mark.asyncio
    async def test_write_with_invalid_data(self, mcp_server, mcp_context, temp_recipe_dir):
        """Test write_processed_recipe with invalid data."""
        from t2d_kit.mcp.tools.processed_recipe_tools import register_processed_recipe_tools
        from t2d_kit.models.processed_recipe import (
            ProcessedRecipeContent,
            WriteProcessedRecipeParams,
        )

        await register_processed_recipe_tools(mcp_server, temp_recipe_dir)

        # Invalid version format - bypass Pydantic validation to test tool handling
        try:
            content = ProcessedRecipeContent(
                name="test",
                version="invalid-version",  # Should be x.y.z
                source_recipe="test.yaml",
                generated_at=datetime.now(UTC).isoformat().replace("+00:00", "Z"),
                diagram_specs=[],  # Empty - violates min_items
                content_files=[],  # Empty - violates min_items
                diagram_refs=[],
                outputs={"assets_dir": "docs/assets"}
            )
        except Exception:
            # Pydantic validation prevents creating invalid content, so use model_construct
            content = ProcessedRecipeContent.model_construct(
                name="test",
                version="invalid-version",
                source_recipe="test.yaml",
                generated_at=datetime.now(UTC).isoformat().replace("+00:00", "Z"),
                diagram_specs=[],
                content_files=[],
                diagram_refs=[],
                outputs={"assets_dir": "docs/assets"}
            )

        params = WriteProcessedRecipeParams(
            recipe_path=str(temp_recipe_dir / "invalid.t2d.yaml"),
            content=content,
            validate=True
        )

        # Call tool - should handle validation error
        tools = await mcp_server.get_tools()
        tool = tools["write_processed_recipe"]
        response = await tool.fn(params)
        result = response.model_dump()

        # Should indicate failure
        assert result["success"] is False
        assert result["validation_result"]["valid"] is False
        assert len(result["validation_result"]["errors"]) > 0

    @pytest.mark.asyncio
    async def test_processed_tool_discovery(self, mcp_server, temp_recipe_dir):
        """Test that all processed recipe tools are discoverable."""
        from t2d_kit.mcp.tools.processed_recipe_tools import register_processed_recipe_tools

        await register_processed_recipe_tools(mcp_server, temp_recipe_dir)

        # List all tools
        tools = await mcp_server.get_tools()

        # Verify expected tools are registered
        tool_names = list(tools.keys())
        assert "write_processed_recipe" in tool_names
        assert "update_processed_recipe" in tool_names
        assert "validate_processed_recipe" in tool_names

        # Verify tool metadata
        for tool_name, tool in tools.items():
            if "processed_recipe" in tool_name:
                assert hasattr(tool, "name")
                assert hasattr(tool, "description")
                # FastMCP tools have 'parameters' or can get schema via model_json_schema()
                assert hasattr(tool, "parameters") or hasattr(tool, "model_json_schema")
