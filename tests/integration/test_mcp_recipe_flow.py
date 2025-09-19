"""Integration tests for MCP recipe workflows."""

from datetime import datetime
from pathlib import Path

import pytest
import yaml


class TestMCPRecipeFlow:
    """Test end-to-end MCP recipe workflows."""

    @pytest.mark.asyncio
    async def test_create_recipe_flow(self, mcp_server, mcp_context, temp_recipe_dir):
        """Test complete recipe creation workflow.

        1. Create user recipe
        2. Validate it
        3. Transform to processed recipe
        4. Update status
        """
        from t2d_kit.mcp.tools.processed_recipe_tools import register_processed_recipe_tools
        from t2d_kit.mcp.tools.user_recipe_tools import register_user_recipe_tools
        from t2d_kit.models.content import ContentFile
        from t2d_kit.models.diagram import DiagramSpecification
        from t2d_kit.models.processed_recipe import (
            DiagramReference,
            ProcessedRecipeContent,
            UpdateProcessedRecipeParams,
            WriteProcessedRecipeParams,
        )
        from t2d_kit.models.user_recipe import (
            CreateRecipeParams,
            DiagramRequest,
            ValidateRecipeParams,
        )

        # Register tools
        await register_user_recipe_tools(mcp_server, temp_recipe_dir)
        await register_processed_recipe_tools(mcp_server, temp_recipe_dir)

        # Step 1: Create user recipe
        create_params = CreateRecipeParams(
            name="integration-test",
            prd_content="# Integration Test System\n\nTest system for workflow.",
            diagrams=[
                DiagramRequest(
                    type="flowchart",
                    description="Main workflow",
                    framework_preference="mermaid"
                )
            ],
            output_dir=str(temp_recipe_dir)
        )

        # Call tools using call_tool method
        create_result = await mcp_server.call_tool("create_user_recipe", create_params, mcp_context)
        assert create_result["success"] is True
        user_recipe_path = create_result["file_path"]

        # Step 2: Validate the created recipe
        validate_params = ValidateRecipeParams(name="integration-test")
        validate_result = await mcp_server.call_tool("validate_user_recipe", validate_params, mcp_context)
        assert validate_result["valid"] is True

        # Step 3: Transform to processed recipe
        processed_content = ProcessedRecipeContent(
            name="integration-test",
            version="1.0.0",
            source_recipe=user_recipe_path,
            generated_at=datetime.utcnow(),
            diagram_specs=[
                DiagramSpecification(
                    id="flow-001",
                    type="flowchart",
                    framework="mermaid",
                    agent="t2d-mermaid-generator",
                    title="Main Workflow",
                    instructions="Generate flowchart from PRD showing the main workflow",
                    output_file="docs/assets/main-flow.mmd",
                    output_formats=["svg"],
                    options={}
                )
            ],
            content_files=[
                ContentFile(
                    id="main-doc",
                    path="docs/main.md",
                    type="documentation",
                    agent="t2d-markdown-maintainer",
                    base_prompt="Document the system with comprehensive overview",
                    diagram_refs=["flow-001"],
                    last_updated=datetime.utcnow()
                )
            ],
            diagram_refs=[
                DiagramReference(
                    id="flow-001",
                    title="Main Workflow",
                    type="flowchart",
                    expected_path="docs/assets/main-flow.svg",
                    status="pending"
                )
            ],
            outputs={"assets_dir": "docs/assets"}
        )

        write_params = WriteProcessedRecipeParams(
            recipe_path=str(temp_recipe_dir / "integration-test.t2d.yaml"),
            content=processed_content,
            validate=True
        )

        # Call write tool
        write_result = await mcp_server.call_tool("write_processed_recipe", write_params, mcp_context)
        assert write_result["success"] is True

        # Step 4: Update status after "generation"
        update_params = UpdateProcessedRecipeParams(
            recipe_path=write_result["recipe_path"],
            diagram_refs=[
                DiagramReference(
                    id="flow-001",
                    title="Main Workflow",
                    type="flowchart",
                    expected_path="docs/assets/main-flow.svg",
                    status="generated"
                )
            ],
            validate=True
        )

        # Call update tool
        update_result = await mcp_server.call_tool("update_processed_recipe", update_params, mcp_context)
        assert update_result["success"] is True

        # Verify files exist
        assert Path(user_recipe_path).exists()
        assert Path(write_result["recipe_path"]).exists()

    @pytest.mark.asyncio
    async def test_resource_discovery(self, mcp_server, temp_recipe_dir, mock_yaml_file):
        """Test discovering recipes via resources."""
        from t2d_kit.mcp.resources import register_resources

        await register_resources(mcp_server)

        # Discover diagram types
        diagram_types = await mcp_server.read_resource("diagram-types://")
        assert len(diagram_types["diagram_types"]) > 0
        assert diagram_types["categories"] is not None

        # Discover user recipes
        user_recipes = await mcp_server.read_resource("user-recipes://")
        assert "recipes" in user_recipes
        assert user_recipes["total_count"] >= 0

        # Get specific recipe
        if user_recipes["total_count"] > 0:
            first_recipe = user_recipes["recipes"][0]
            specific_recipe = await mcp_server.read_resource(f"user-recipes://{first_recipe['name']}")
            assert specific_recipe["name"] == first_recipe["name"]
            assert "content" in specific_recipe
            assert "raw_yaml" in specific_recipe

        # Get schemas
        user_schema = await mcp_server.read_resource("user-recipe-schema://")
        assert "version" in user_schema
        assert "fields" in user_schema

        processed_schema = await mcp_server.read_resource("processed-recipe-schema://")
        assert "version" in processed_schema
        assert len(processed_schema["fields"]) > len(user_schema["fields"])  # More complex

    @pytest.mark.asyncio
    async def test_transform_recipe_flow(self, mcp_server, mcp_context, temp_recipe_dir):
        """Test the recipe transformation flow from user to processed.

        This simulates what the t2d-transform agent would do.
        """
        from t2d_kit.mcp.resources import register_resources
        from t2d_kit.mcp.tools.processed_recipe_tools import register_processed_recipe_tools
        from t2d_kit.mcp.tools.user_recipe_tools import register_user_recipe_tools
        from t2d_kit.models.processed_recipe import (
            ProcessedRecipeContent,
            WriteProcessedRecipeParams,
        )
        from t2d_kit.models.user_recipe import CreateRecipeParams, DiagramRequest

        # Register everything
        await register_resources(mcp_server)
        await register_user_recipe_tools(mcp_server, temp_recipe_dir)
        await register_processed_recipe_tools(mcp_server, temp_recipe_dir)

        # Create a user recipe with multiple diagrams
        create_params = CreateRecipeParams(
            name="transform-test",
            prd_content="""# Transform Test System

## Overview
A comprehensive system for testing transformation.

## Components
- User Service
- Order Service
- Payment Service

## Workflows
- User registration and authentication
- Order placement and processing
- Payment handling
""",
            diagrams=[
                DiagramRequest(type="architecture", description="System architecture", framework_preference="d2"),
                DiagramRequest(type="flowchart", description="Order flow", framework_preference="mermaid"),
                DiagramRequest(type="sequence", description="Payment sequence", framework_preference="mermaid"),
                DiagramRequest(type="erd", description="Database schema", framework_preference="d2")
            ],
            documentation_config={
                "style": "technical",
                "audience": "developers",
                "sections": ["Overview", "Architecture", "API", "Deployment"],
                "format": "mkdocs"
            },
            output_dir=str(temp_recipe_dir)
        )

        result = await mcp_server.call_tool("create_user_recipe", create_params, mcp_context)
        assert result["success"] is True

        # Read the created recipe
        recipe_content = await mcp_server.read_resource("user-recipes://transform-test")
        assert recipe_content is not None

        # Get available diagram types for mapping
        diagram_types = await mcp_server.read_resource("diagram-types://")
        type_map = {dt["type_id"]: dt for dt in diagram_types["diagram_types"]}

        # Transform to processed recipe (what agent would do)
        diagram_specs = []
        diagram_refs = []
        for i, diagram in enumerate(recipe_content["content"]["instructions"]["diagrams"]):
            diagram_id = f"{diagram['type']}-{i:03d}"
            diagram_specs.append({
                "id": diagram_id,
                "type": diagram["type"],
                "framework": diagram.get("framework", type_map[diagram["type"]]["framework"]),
                "agent": f"t2d-{diagram.get('framework', 'mermaid')}-generator",
                "title": diagram["description"],
                "instructions": f"Generate {diagram['type']} showing: {diagram['description']}",
                "output_file": f"docs/assets/{diagram['type']}-{i}",
                "output_formats": ["svg", "png"],
                "options": {}
            })
            diagram_refs.append({
                "id": diagram_id,
                "title": diagram["description"],
                "type": diagram["type"],
                "expected_path": f"docs/assets/{diagram['type']}-{i}.svg",
                "status": "pending"
            })

        # Create content files based on documentation config
        content_files = []
        if "documentation" in recipe_content["content"]["instructions"]:
            doc_config = recipe_content["content"]["instructions"]["documentation"]
            for section in doc_config.get("sections", []):
                content_files.append({
                    "id": section.lower().replace(" ", "-"),
                    "path": f"docs/{section.lower().replace(' ', '-')}.md",
                    "type": "documentation",
                    "agent": "t2d-docs",
                    "base_prompt": f"Write {section} documentation",
                    "diagram_refs": [d["id"] for d in diagram_refs],
                    "title": section,
                    "last_updated": datetime.utcnow().isoformat() + "Z"
                })

        # Write processed recipe
        processed_content = ProcessedRecipeContent(
            name="transform-test",
            version="1.0.0",
            source_recipe=result["file_path"],
            generated_at=datetime.utcnow().isoformat() + "Z",
            diagram_specs=diagram_specs,
            content_files=content_files if content_files else [{
                "id": "default",
                "path": "docs/index.md",
                "type": "documentation",
                "agent": "t2d-docs",
                "base_prompt": "Write documentation",
                "diagram_refs": [],
                "last_updated": datetime.utcnow().isoformat() + "Z"
            }],
            diagram_refs=diagram_refs,
            outputs={
                "assets_dir": "docs/assets",
                "mkdocs": {
                    "config_file": "mkdocs.yml",
                    "site_name": "Transform Test Documentation",
                    "theme": "material"
                }
            },
            generation_notes=["Transformed from user recipe", f"Generated {len(diagram_specs)} diagrams"]
        )

        write_params = WriteProcessedRecipeParams(
            recipe_path=str(temp_recipe_dir / "transform-test.t2d.yaml"),
            content=processed_content,
            validate=True
        )

        write_result = await mcp_server.call_tool("write_processed_recipe", write_params, mcp_context)
        assert write_result["success"] is True

        # Verify both recipes exist
        user_recipes = await mcp_server.read_resource("user-recipes://")
        processed_recipes = await mcp_server.read_resource("processed-recipes://")

        user_names = [r["name"] for r in user_recipes["recipes"]]
        processed_names = [r["name"] for r in processed_recipes["recipes"]]

        assert "transform-test" in user_names
        assert "transform-test" in processed_names

    @pytest.mark.asyncio
    async def test_validation_errors(self, mcp_server, mcp_context, temp_recipe_dir):
        """Test handling of validation errors throughout the workflow."""
        from t2d_kit.mcp.tools.user_recipe_tools import register_user_recipe_tools
        from t2d_kit.models.user_recipe import (
            CreateRecipeParams,
            DiagramRequest,
            ValidateRecipeParams,
        )

        await register_user_recipe_tools(mcp_server, temp_recipe_dir)

        # Test 1: Invalid recipe name
        params = CreateRecipeParams(
            name="123-starts-with-number",  # Invalid
            prd_content="Test",
            diagrams=[DiagramRequest(type="flowchart")],
            output_dir=str(temp_recipe_dir)
        )

        result = await mcp_server.call_tool("create_user_recipe", params, mcp_context)
        assert result["success"] is False
        assert result["validation_result"]["valid"] is False
        errors = result["validation_result"]["errors"]
        assert any("name" in e["field"] for e in errors)

        # Test 2: Missing required fields
        params = CreateRecipeParams(
            name="valid-name",
            prd_content="",  # Empty content
            diagrams=[],  # No diagrams
            output_dir=str(temp_recipe_dir)
        )

        result = await mcp_server.call_tool("create_user_recipe", params, mcp_context)
        assert result["success"] is False
        assert len(result["validation_result"]["errors"]) > 0

        # Test 3: Invalid diagram type
        params = CreateRecipeParams(
            name="test-invalid-diagram",
            prd_content="Test PRD",
            diagrams=[
                DiagramRequest(
                    type="not-a-real-diagram-type",
                    description="Invalid diagram"
                )
            ],
            output_dir=str(temp_recipe_dir)
        )

        result = await mcp_server.call_tool("create_user_recipe", params, mcp_context)
        assert result["success"] is False
        validation = result["validation_result"]
        assert not validation["valid"]
        assert any("diagram" in e["field"].lower() for e in validation["errors"])

        # Test 4: Validate non-existent recipe
        validate_params = ValidateRecipeParams(name="does-not-exist")
        result = await mcp_server.call_tool("validate_user_recipe", validate_params, mcp_context)
        assert result["valid"] is False
        assert any("not found" in e["message"].lower() for e in result["errors"])

    @pytest.mark.asyncio
    async def test_concurrent_operations(self, mcp_server, mcp_context, temp_recipe_dir):
        """Test that concurrent operations are handled safely."""
        import asyncio

        from t2d_kit.mcp.tools.user_recipe_tools import register_user_recipe_tools
        from t2d_kit.models.user_recipe import CreateRecipeParams, DiagramRequest

        await register_user_recipe_tools(mcp_server, temp_recipe_dir)

        # Create multiple recipes concurrently
        tasks = []
        for i in range(5):
            params = CreateRecipeParams(
                name=f"concurrent-test-{i}",
                prd_content=f"Test PRD {i}",
                diagrams=[DiagramRequest(type="flowchart", description=f"Flow {i}")],
                output_dir=str(temp_recipe_dir)
            )
            tasks.append(mcp_server.call_tool("create_user_recipe", params, mcp_context))

        results = await asyncio.gather(*tasks)

        # All should succeed
        assert all(r["success"] for r in results)

        # All files should exist
        for i in range(5):
            recipe_path = temp_recipe_dir / f"concurrent-test-{i}.yaml"
            assert recipe_path.exists()
