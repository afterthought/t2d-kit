"""
T012: Integration test for complete transformation pipeline.
Tests the transformation workflow using MCP tools and agents.
"""

from datetime import datetime
from pathlib import Path

import pytest

from t2d_kit.models.diagram import DiagramSpecification
from t2d_kit.models.processed_recipe import (
    DiagramReference,
    ProcessedRecipe,
    ProcessedRecipeContent,
    WriteProcessedRecipeParams,
)
from t2d_kit.models.user_recipe import (
    CreateRecipeParams,
    DiagramRequest,
    UserRecipe,
    ValidateRecipeParams,
)
from t2d_kit.models.content import ContentFile


class TestTransformIntegration:
    """Integration tests for the complete transformation pipeline using MCP tools."""

    @pytest.mark.asyncio
    async def test_model_validation(self, sample_user_recipe):
        """Test that models can be properly instantiated and validated."""
        # Test UserRecipe creation using the fixture
        user_recipe = UserRecipe(**sample_user_recipe)
        assert user_recipe.name == "test-system"
        assert user_recipe.prd.content is not None
        assert len(user_recipe.instructions.diagrams) == 2
        assert user_recipe.instructions.diagrams[0].type == "flowchart"

    @pytest.mark.asyncio
    async def test_processed_recipe_creation(self, sample_processed_recipe):
        """Test creating a ProcessedRecipe from valid components."""
        # Create processed recipe content using the fixture
        processed_content = ProcessedRecipeContent(**sample_processed_recipe)

        assert processed_content.name == "test-system"
        assert len(processed_content.diagram_specs) == 1
        assert len(processed_content.content_files) == 1
        assert len(processed_content.diagram_refs) == 1

        # Verify the diagram spec has proper validation
        diagram_spec = processed_content.diagram_specs[0]
        assert diagram_spec.id == "flow-001"
        assert diagram_spec.framework == "mermaid"
        assert diagram_spec.agent == "t2d-mermaid-generator"
        assert len(diagram_spec.instructions.split()) >= 5  # Validation requirement

    @pytest.mark.asyncio
    async def test_transformation_workflow(self, temp_recipe_dir, sample_user_recipe, sample_processed_recipe):
        """Test the complete transformation workflow using model validation."""
        # Step 1: Create and validate user recipe
        user_recipe = UserRecipe(**sample_user_recipe)
        assert user_recipe.name == "test-system"
        assert len(user_recipe.instructions.diagrams) == 2

        # Step 2: Transform to processed recipe (simulating what t2d-transform agent does)
        # Create enhanced diagram specs with proper validation
        enhanced_processed_recipe = sample_processed_recipe.copy()
        enhanced_processed_recipe["diagram_specs"][0]["instructions"] = "Create a flowchart showing the complete system flow from user input to database"

        processed_content = ProcessedRecipeContent(**enhanced_processed_recipe)
        assert processed_content.name == "test-system"
        assert len(processed_content.diagram_specs) == 1
        assert len(processed_content.content_files) == 1
        assert len(processed_content.diagram_refs) == 1

        # Step 3: Verify transformation workflow compatibility
        # Check that diagram requests can be mapped to specifications
        diagram_request = user_recipe.instructions.diagrams[0]
        diagram_spec = processed_content.diagram_specs[0]

        assert diagram_request.type == diagram_spec.type
        assert diagram_spec.framework in ["mermaid", "d2", "plantuml"]  # Valid frameworks
        assert diagram_spec.agent.startswith("t2d-")  # Proper agent naming

        # Verify output structure is properly formed
        assert processed_content.outputs.assets_dir == "docs/assets"
        assert processed_content.outputs.mkdocs is not None

    @pytest.mark.asyncio
    async def test_validation_error_handling(self):
        """Test that validation errors are properly handled."""
        # Test with invalid diagram request
        with pytest.raises(ValueError):
            DiagramRequest(
                type="invalid-diagram-type",
                description="Invalid diagram"
            )

        # Test with invalid user recipe data
        with pytest.raises(ValueError):
            UserRecipe(
                name="",  # Invalid: empty name
                description="Test",
                instructions={
                    "prd": {"content": "Test"},
                    "diagrams": []  # Invalid: no diagrams
                }
            )

    @pytest.mark.asyncio
    async def test_diagram_specification_validation(self):
        """Test DiagramSpecification model validation."""
        # Valid diagram spec with proper instruction length
        diagram_spec = DiagramSpecification(
            id="valid-spec",
            type="flowchart",
            framework="mermaid",
            agent="t2d-mermaid-generator",
            title="Valid Specification",
            instructions="Generate a comprehensive flowchart diagram showing system workflow",
            output_file="test.mmd",
            output_formats=["svg"],
            options={}
        )
        assert diagram_spec.id == "valid-spec"
        assert diagram_spec.framework == "mermaid"

        # Test invalid framework for diagram type
        with pytest.raises(ValueError):
            DiagramSpecification(
                id="invalid-spec",
                type="flowchart",
                framework="invalid-framework",  # Invalid
                agent="t2d-agent",
                title="Invalid Framework",
                instructions="Generate a comprehensive test diagram for validation purposes",
                output_file="test.mmd",
                output_formats=["svg"],
                options={}
            )
