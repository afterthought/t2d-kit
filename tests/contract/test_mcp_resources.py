"""Contract tests for MCP resources."""

from pathlib import Path
from unittest.mock import AsyncMock

import pytest
from fastmcp import Context


class TestMCPResources:
    """Test MCP resource contracts match specifications."""

    @pytest.fixture
    def mock_context(self):
        """Create a mock Context object for tests."""
        return AsyncMock(spec=Context)

    @pytest.mark.asyncio
    async def test_diagram_types_resource(self, mcp_server, sample_diagram_types):
        """Test diagram-types:// resource contract.

        Contract: specs/002-the-user-can/contracts/mcp_resources.json#DiagramTypesResource
        """
        # Register the resource
        from t2d_kit.mcp.resources.diagram_types import register_diagram_types_resource

        await register_diagram_types_resource(mcp_server)

        # Get resource
        resource = await mcp_server.get_resource("diagram-types://")
        resource_response = await resource.fn()
        # Resource now returns data directly
        result = resource_response

        # Resource now returns just the array
        assert isinstance(result, list)

        # Validate diagram type structure
        for diagram_type in result:
            assert "type_id" in diagram_type
            assert "name" in diagram_type
            assert "framework" in diagram_type
            assert diagram_type["framework"] in ["mermaid", "d2", "plantuml"]
            assert "description" in diagram_type
            assert "example_usage" in diagram_type
            assert "supported_frameworks" in diagram_type
            assert isinstance(diagram_type["supported_frameworks"], list)

    @pytest.mark.asyncio
    async def test_user_recipes_resource(self, mcp_server, temp_recipe_dir, mock_yaml_file):
        """Test user recipe resource template contract.

        Contract: specs/002-the-user-can/contracts/mcp_resources.json#RecipeListResource
        """
        from t2d_kit.mcp.resources.user_recipes import register_user_recipe_resources

        await register_user_recipe_resources(mcp_server, temp_recipe_dir)

        # Get resource templates
        templates = await mcp_server.get_resource_templates()

        # Find the user recipe template
        expected_template = f"file://{temp_recipe_dir.resolve()}/{{name}}.yaml"
        assert expected_template in templates

        # Get a specific recipe through the template
        template = templates[expected_template]
        result = await template.fn("test-recipe")

        # Validate recipe detail structure
        assert "name" in result
        assert "content" in result
        assert "raw_yaml" in result
        assert "file_path" in result
        assert "metadata" in result

        # Validate metadata
        metadata = result["metadata"]
        assert "name" in metadata
        assert "file_path" in metadata
        assert "created_at" in metadata
        assert "modified_at" in metadata
        assert "size_bytes" in metadata
        assert "diagram_count" in metadata
        assert "has_prd" in metadata
        assert "validation_status" in metadata
        assert metadata["validation_status"] in ["valid", "invalid", "unknown"]

    @pytest.mark.asyncio
    async def test_processed_recipes_resource(self, mcp_server, temp_recipe_dir, mock_processed_yaml_file):
        """Test processed recipe resource template contract.

        Contract: specs/002-the-user-can/contracts/mcp_resources.json#ProcessedRecipeListResource
        """
        from t2d_kit.mcp.resources.processed_recipes import register_processed_recipe_resources

        await register_processed_recipe_resources(mcp_server, temp_recipe_dir)

        # Get resource templates
        templates = await mcp_server.get_resource_templates()

        # Find the processed recipe template
        expected_template = f"file://{temp_recipe_dir.resolve()}/{{name}}.t2d.yaml"
        assert expected_template in templates

        # Get a specific processed recipe through the template
        template = templates[expected_template]
        result = await template.fn("test-recipe")

        # Validate recipe detail structure
        assert "name" in result
        assert "content" in result
        assert "raw_yaml" in result
        assert "file_path" in result
        assert "metadata" in result

        # Validate metadata
        metadata = result["metadata"]
        assert "name" in metadata
        assert "file_path" in metadata
        assert "source_recipe" in metadata
        assert "generated_at" in metadata
        assert "modified_at" in metadata
        assert "size_bytes" in metadata
        assert "diagram_count" in metadata
        assert "content_file_count" in metadata
        assert "validation_status" in metadata

    @pytest.mark.asyncio
    async def test_recipe_schemas(self, mcp_server):
        """Test recipe schema resources contract.

        Contract: specs/002-the-user-can/contracts/mcp_resources.json#RecipeSchemaResource
        """
        from t2d_kit.mcp.resources.schemas import register_schema_resources

        await register_schema_resources(mcp_server)

        # Test user recipe schema
        user_schema_resource = await mcp_server.get_resource("user-recipe-schema://")
        user_schema_response = await user_schema_resource.fn()
        # Resource now returns data directly
        user_schema = user_schema_response
        assert "version" in user_schema
        assert "fields" in user_schema
        assert "examples" in user_schema
        assert "validation_rules" in user_schema

        # Test processed recipe schema
        processed_schema_resource = await mcp_server.get_resource("processed-recipe-schema://")
        processed_schema_response = await processed_schema_resource.fn()
        # Resource now returns data directly
        processed_schema = processed_schema_response
        assert "version" in processed_schema
        assert "fields" in processed_schema
        assert "examples" in processed_schema
        assert "validation_rules" in processed_schema

        # Validate field structure
        for field in user_schema["fields"]:
            assert "name" in field
            assert "type" in field
            assert "required" in field
            assert "description" in field

    @pytest.mark.asyncio
    async def test_specific_recipe_resource(self, mcp_server, temp_recipe_dir, mock_yaml_file):
        """Test file://{path}/{name}.yaml specific recipe resource template.

        Contract: specs/002-the-user-can/contracts/mcp_resources.json#RecipeDetailResource
        """
        from t2d_kit.mcp.resources.user_recipes import register_user_recipe_resources

        await register_user_recipe_resources(mcp_server, temp_recipe_dir)

        # Get resource templates
        templates = await mcp_server.get_resource_templates()

        # Find the user recipe template
        expected_template = f"file://{temp_recipe_dir.resolve()}/{{name}}.yaml"
        assert expected_template in templates

        # Get a specific recipe through the template
        template = templates[expected_template]
        result = await template.fn("test-recipe")

        # Validate contract
        assert "name" in result
        assert "content" in result
        assert "raw_yaml" in result
        assert "file_path" in result
        assert "metadata" in result

        # Metadata should match summary structure
        metadata = result["metadata"]
        assert "name" in metadata
        assert "file_path" in metadata
        assert "created_at" in metadata
        assert "modified_at" in metadata

    @pytest.mark.asyncio
    async def test_resource_discovery(self, mcp_server, temp_recipe_dir):
        """Test that all resources are discoverable."""
        from t2d_kit.mcp.resources import register_resources
        import tempfile
        from pathlib import Path

        # Create temporary processed recipe directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            processed_dir = Path(temp_dir)

            await register_resources(mcp_server, temp_recipe_dir, processed_dir)

            # List all regular resources
            resources = await mcp_server.get_resources()

            # List all resource templates
            templates = await mcp_server.get_resource_templates()

        # Verify expected regular resources are registered
        resource_uris = list(resources.keys())
        assert "diagram-types://" in resource_uris
        assert "user-recipe-schema://" in resource_uris
        assert "processed-recipe-schema://" in resource_uris

        # Verify expected resource templates are registered
        expected_user_template = f"file://{temp_recipe_dir.resolve()}/{{name}}.yaml"
        expected_processed_template = f"file://{processed_dir.resolve()}/{{name}}.t2d.yaml"
        assert expected_user_template in templates
        assert expected_processed_template in templates

        # Verify metadata for regular resources
        for uri, resource in resources.items():
            assert hasattr(resource, "uri")
            assert hasattr(resource, "name")
            # Verify the uri matches the key
            assert str(resource.uri) == uri
            # description might be optional
