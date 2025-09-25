"""Smoke test for MCP server startup via CLI."""

import asyncio
import json
import subprocess
import sys
import time
from pathlib import Path
from unittest.mock import AsyncMock

import pytest
from fastmcp import Context


class TestMCPServerSmoke:
    """Smoke tests for MCP server functionality."""

    def test_server_imports(self):
        """Test that server modules can be imported without errors."""
        try:
            from t2d_kit.mcp.server import main, create_server
            from t2d_kit.mcp.resources import register_resources
            from t2d_kit.mcp.tools import register_tools
            assert main is not None
            assert create_server is not None
            assert register_resources is not None
            assert register_tools is not None
        except ImportError as e:
            pytest.fail(f"Failed to import MCP server modules: {e}")

    def test_server_creation(self):
        """Test that the MCP server can be created programmatically."""
        from t2d_kit.mcp.server import create_server

        # Create server with default directories
        server = create_server()
        assert server is not None
        assert server.name == "t2d-kit"

    @pytest.mark.asyncio
    async def test_server_has_tools_and_resources(self):
        """Test that the server has tools and resources registered."""
        from t2d_kit.mcp.server import create_server_async

        # Create server
        server = await create_server_async()

        # Check tools are registered
        tools = await server.get_tools()
        assert len(tools) > 0

        # Verify key tools exist
        expected_tools = [
            "create_user_recipe",
            "write_processed_recipe",
            "validate_user_recipe",
            "validate_processed_recipe"
        ]
        tool_names = list(tools.keys())
        for expected in expected_tools:
            assert expected in tool_names, f"Missing expected tool: {expected}"

        # Check resources are registered
        resources = await server.get_resources()
        assert len(resources) > 0

        # Check resource templates are registered
        templates = await server.get_resource_templates()
        assert len(templates) > 0

        # Verify key regular resources exist
        expected_resources = [
            "diagram-types://",
            "user-recipe-schema://",
            "processed-recipe-schema://"
        ]
        resource_uris = list(resources.keys())  # resources is a dict where keys are URIs
        for expected in expected_resources:
            assert expected in resource_uris, f"Missing expected resource: {expected}"

        # Verify resource templates exist (they will have file:// URIs with absolute paths)
        template_uris = list(templates.keys())
        # Check that we have at least templates for user recipes and processed recipes
        has_user_template = any("/{name}.yaml" in uri for uri in template_uris)
        has_processed_template = any("/{name}.t2d.yaml" in uri for uri in template_uris)
        assert has_user_template, "Missing user recipe template"
        assert has_processed_template, "Missing processed recipe template"

    def test_cli_mcp_command_stdio_mode(self, tmp_path):
        """Test that the MCP server can be started via CLI in stdio mode."""
        # Create a test script that sends a simple MCP request
        test_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
            "params": {}
        }

        # Start the server as a subprocess in stdio mode
        process = subprocess.Popen(
            ["t2d", "mcp", str(tmp_path)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        try:
            # Send the request
            process.stdin.write(json.dumps(test_request) + "\n")
            process.stdin.flush()

            # Wait a bit for response
            time.sleep(0.5)

            # Terminate the process
            process.terminate()
            stdout, stderr = process.communicate(timeout=2)

            # Check that no import errors occurred
            if "ImportError" in stderr:
                pytest.fail(f"Import error when starting server: {stderr}")
            if "cannot import name" in stderr:
                pytest.fail(f"Import error when starting server: {stderr}")

        except subprocess.TimeoutExpired:
            process.kill()
            stdout, stderr = process.communicate()
            # Server running without crashing is success for smoke test
            pass
        except Exception as e:
            process.kill()
            pytest.fail(f"Failed to run MCP server: {e}")

    def test_cli_mcp_command_help(self):
        """Test that the MCP command help works."""
        result = subprocess.run(
            ["t2d", "mcp", "--help"],
            capture_output=True,
            text=True
        )

        assert result.returncode == 0
        assert "Start the MCP server" in result.stdout
        assert "--port" in result.stdout

    def test_server_with_custom_directories(self, tmp_path):
        """Test that the server can be created with custom directories."""
        from t2d_kit.mcp.server import create_server

        # Create custom directories
        recipe_dir = tmp_path / "custom_recipes"
        processed_dir = tmp_path / "custom_processed"
        recipe_dir.mkdir(parents=True)
        processed_dir.mkdir(parents=True)

        # Create server with custom directories
        server = create_server(recipe_dir=recipe_dir, processed_dir=processed_dir)
        assert server is not None
        assert server.name == "t2d-kit"

    @pytest.mark.asyncio
    async def test_server_tool_execution(self, tmp_path):
        """Test that a basic tool can be executed."""
        from t2d_kit.mcp.server import create_server_async
        from t2d_kit.models.user_recipe import CreateRecipeParams, DiagramRequest

        # Create server with temp directory
        recipe_dir = tmp_path / "recipes"
        recipe_dir.mkdir(parents=True)

        server = await create_server_async(recipe_dir=recipe_dir)

        # Get the create_user_recipe tool
        tools = await server.get_tools()
        create_tool = tools.get("create_user_recipe")
        assert create_tool is not None

        # Create a simple recipe
        params = CreateRecipeParams(
            name="smoke-test",
            prd_content="# Smoke Test\n\nThis is a smoke test recipe.",
            diagrams=[
                DiagramRequest(
                    type="architecture",
                    description="Test architecture diagram"
                )
            ],
            output_dir=str(recipe_dir)
        )

        # Create mock context
        mock_context = AsyncMock(spec=Context)

        # Execute the tool
        result = await create_tool.fn(params, mock_context)
        assert result is not None

        # Verify the recipe file was created
        recipe_file = recipe_dir / "smoke-test.yaml"
        assert recipe_file.exists()