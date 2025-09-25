"""Test MCP tools with JSON string parameters as sent by Claude Code."""

import json
from pathlib import Path
from unittest.mock import AsyncMock

import pytest
from fastmcp import Context

from t2d_kit.mcp.tools.user_recipe_tools import register_user_recipe_tools


class TestMCPJSONParams:
    """Test that MCP tools handle JSON string parameters correctly."""

    @pytest.mark.asyncio
    async def test_create_user_recipe_with_json_string(self, mcp_server, temp_recipe_dir):
        """Test create_user_recipe with exact JSON string as sent by Claude Code."""
        # Register the tools
        await register_user_recipe_tools(mcp_server, temp_recipe_dir)

        # This is the exact payload format that Claude Code sends
        json_params = json.dumps({
            "name": "two-tier-graphql-app",
            "prd_content": "# Two-Tier Application with GraphQL and PostgreSQL\n\n## System Overview\nA modern two-tier web application that provides a robust data-driven experience through a GraphQL API layer.\n\n## Architecture Components\n\n### Frontend Tier\n- **Next.js Application**: A React-based frontend framework providing:\n  - Server-side rendering (SSR) for optimal performance\n  - Client-side routing\n  - GraphQL client integration for API communication\n  - Responsive user interface\n  - Real-time data updates via GraphQL subscriptions\n\n### Backend Tier\n- **GraphQL API Server**: A flexible query layer that:\n  - Provides a single endpoint for all data operations\n  - Handles authentication and authorization\n  - Implements business logic and data validation\n  - Manages database connections and query optimization\n  - Supports real-time subscriptions\n\n### Data Layer\n- **PostgreSQL Database**: A relational database system storing:\n  - User accounts and authentication data\n  - Application business data\n  - Session management\n  - Audit logs and analytics data\n\n## Data Flow\n1. Users interact with the Next.js frontend through web browsers\n2. Frontend sends GraphQL queries/mutations to the API server\n3. GraphQL API processes requests and validates permissions\n4. API server queries PostgreSQL database for data operations\n5. Database returns results to API server\n6. API server formats and returns response to frontend\n7. Next.js renders the updated UI for users\n\n## Key Features\n- Type-safe API with GraphQL schema\n- Efficient data fetching with query batching\n- Real-time updates through WebSocket connections\n- Scalable architecture with clear separation of concerns\n- Database connection pooling for performance\n- Caching layer for frequently accessed data",
            "diagrams": [
                {
                    "type": "c4_context",
                    "description": "High-level system context showing users and external systems",
                    "framework_preference": "d2"
                },
                {
                    "type": "c4_container",
                    "description": "Container diagram showing the Next.js frontend, GraphQL API, and PostgreSQL database",
                    "framework_preference": "d2"
                }
            ]
        })

        # Get the tool
        tools = await mcp_server.get_tools()
        create_tool = tools["create_user_recipe"]

        # Create mock context
        mock_context = AsyncMock(spec=Context)

        # Call the tool with JSON string (as Claude Code does)
        result = await create_tool.fn(json_params, mock_context)

        # Verify it succeeded
        assert result.success is True
        assert result.file_path.endswith("two-tier-graphql-app.yaml")
        assert result.validation_result.valid is True

        # Verify the file was created
        recipe_file = temp_recipe_dir / "two-tier-graphql-app.yaml"
        assert recipe_file.exists()

    @pytest.mark.asyncio
    async def test_create_user_recipe_with_dict(self, mcp_server, temp_recipe_dir):
        """Test create_user_recipe with dict parameters."""
        # Register the tools
        await register_user_recipe_tools(mcp_server, temp_recipe_dir)

        # Dict format
        dict_params = {
            "name": "test-dict-recipe",
            "prd_content": "# Test Recipe\n\nSimple test content.",
            "diagrams": [
                {
                    "type": "flowchart",
                    "description": "Test flowchart"
                }
            ]
        }

        # Get the tool
        tools = await mcp_server.get_tools()
        create_tool = tools["create_user_recipe"]

        # Create mock context
        mock_context = AsyncMock(spec=Context)

        # Call the tool with dict
        result = await create_tool.fn(dict_params, mock_context)

        # Verify it succeeded
        assert result.success is True
        assert result.file_path.endswith("test-dict-recipe.yaml")
        assert result.validation_result.valid is True

    @pytest.mark.asyncio
    async def test_create_user_recipe_with_pydantic_model(self, mcp_server, temp_recipe_dir):
        """Test create_user_recipe with proper Pydantic model."""
        from t2d_kit.models.user_recipe import CreateRecipeParams, DiagramRequest

        # Register the tools
        await register_user_recipe_tools(mcp_server, temp_recipe_dir)

        # Pydantic model format
        model_params = CreateRecipeParams(
            name="test-model-recipe",
            prd_content="# Test Recipe\n\nSimple test content.",
            diagrams=[
                DiagramRequest(
                    type="flowchart",
                    description="Test flowchart"
                )
            ]
        )

        # Get the tool
        tools = await mcp_server.get_tools()
        create_tool = tools["create_user_recipe"]

        # Create mock context
        mock_context = AsyncMock(spec=Context)

        # Call the tool with Pydantic model
        result = await create_tool.fn(model_params, mock_context)

        # Verify it succeeded
        assert result.success is True
        assert result.file_path.endswith("test-model-recipe.yaml")
        assert result.validation_result.valid is True

    @pytest.mark.asyncio
    async def test_invalid_json_string(self, mcp_server, temp_recipe_dir):
        """Test that invalid JSON string is handled gracefully."""
        # Register the tools
        await register_user_recipe_tools(mcp_server, temp_recipe_dir)

        # Invalid JSON
        invalid_json = "{'name': 'invalid', this is not valid json}"

        # Get the tool
        tools = await mcp_server.get_tools()
        create_tool = tools["create_user_recipe"]

        # Create mock context
        mock_context = AsyncMock(spec=Context)

        # Call the tool with invalid JSON
        result = await create_tool.fn(invalid_json, mock_context)

        # Verify it failed gracefully
        assert result.success is False
        assert "Invalid JSON" in result.message
        assert result.validation_result.valid is False
        assert len(result.validation_result.errors) > 0

    @pytest.mark.asyncio
    async def test_missing_required_fields_in_json(self, mcp_server, temp_recipe_dir):
        """Test that missing required fields are caught."""
        # Register the tools
        await register_user_recipe_tools(mcp_server, temp_recipe_dir)

        # Missing diagrams field
        json_params = json.dumps({
            "name": "incomplete-recipe",
            "prd_content": "# Test Recipe"
            # Missing required 'diagrams' field
        })

        # Get the tool
        tools = await mcp_server.get_tools()
        create_tool = tools["create_user_recipe"]

        # Create mock context
        mock_context = AsyncMock(spec=Context)

        # Call the tool
        result = await create_tool.fn(json_params, mock_context)

        # Verify it failed with validation error
        assert result.success is False
        assert result.validation_result.valid is False