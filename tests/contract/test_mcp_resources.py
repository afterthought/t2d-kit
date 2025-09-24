"""Contract tests for MCP resources."""

from pathlib import Path

import pytest


class TestMCPResources:
    """Test MCP resource contracts match specifications."""

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
        result = resource_response["content"]

        # Validate contract
        assert "diagram_types" in result
        assert "total_count" in result
        assert "categories" in result

        # Validate diagram type structure
        for diagram_type in result["diagram_types"]:
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
        """Test user-recipes:// resource contract.

        Contract: specs/002-the-user-can/contracts/mcp_resources.json#RecipeListResource
        """
        from t2d_kit.mcp.resources.user_recipes import register_user_recipe_resources

        await register_user_recipe_resources(mcp_server, temp_recipe_dir)

        # List all recipes
        resource = await mcp_server.get_resource("user-recipes://")
        resource_response = await resource.fn()
        result = resource_response["content"]

        # Validate contract
        assert "recipes" in result
        assert "total_count" in result
        assert "directory" in result

        # Validate recipe summary structure
        for recipe in result["recipes"]:
            assert "name" in recipe
            assert "file_path" in recipe
            assert "created_at" in recipe
            assert "modified_at" in recipe
            assert "size_bytes" in recipe
            assert "diagram_count" in recipe
            assert "has_prd" in recipe
            assert "validation_status" in recipe
            assert recipe["validation_status"] in ["valid", "invalid", "unknown"]

    @pytest.mark.asyncio
    async def test_processed_recipes_resource(self, mcp_server, temp_recipe_dir, mock_processed_yaml_file):
        """Test processed-recipes:// resource contract.

        Contract: specs/002-the-user-can/contracts/mcp_resources.json#ProcessedRecipeListResource
        """
        from t2d_kit.mcp.resources.processed_recipes import register_processed_recipe_resources

        await register_processed_recipe_resources(mcp_server, temp_recipe_dir)

        # List all processed recipes
        resource = await mcp_server.get_resource("processed-recipes://")
        resource_response = await resource.fn()
        result = resource_response["content"]

        # Validate contract
        assert "recipes" in result
        assert "total_count" in result
        assert "directory" in result

        # Validate processed recipe summary structure
        for recipe in result["recipes"]:
            assert "name" in recipe
            assert "file_path" in recipe
            assert "source_recipe" in recipe
            assert "generated_at" in recipe
            assert "modified_at" in recipe
            assert "size_bytes" in recipe
            assert "diagram_count" in recipe
            assert "content_file_count" in recipe
            assert "validation_status" in recipe

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
        user_schema = user_schema_response["content"]
        assert "version" in user_schema
        assert "fields" in user_schema
        assert "examples" in user_schema
        assert "validation_rules" in user_schema

        # Test processed recipe schema
        processed_schema_resource = await mcp_server.get_resource("processed-recipe-schema://")
        processed_schema_response = await processed_schema_resource.fn()
        processed_schema = processed_schema_response["content"]
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
        """Test user-recipes://{name} specific recipe resource.

        Contract: specs/002-the-user-can/contracts/mcp_resources.json#RecipeDetailResource
        """
        from t2d_kit.mcp.resources.user_recipes import register_user_recipe_resources

        await register_user_recipe_resources(mcp_server, temp_recipe_dir)

        # Get specific recipe
        resource = await mcp_server.get_resource("user-recipes://test-recipe")
        resource_response = await resource.fn()
        result = resource_response["content"]

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
    async def test_resource_discovery(self, mcp_server):
        """Test that all resources are discoverable."""
        from t2d_kit.mcp.resources import register_resources

        await register_resources(mcp_server)

        # List all resources
        resources = await mcp_server.get_resources()

        # Verify expected resources are registered
        resource_uris = list(resources.keys())
        assert "diagram-types://" in resource_uris
        assert "user-recipes://" in resource_uris
        assert "processed-recipes://" in resource_uris
        assert "user-recipe-schema://" in resource_uris
        assert "processed-recipe-schema://" in resource_uris

        # Verify metadata
        for _uri, resource in resources.items():
            assert hasattr(resource, "uri")
            assert hasattr(resource, "name")
            # description might be optional
