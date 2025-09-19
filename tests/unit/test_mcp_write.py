"""
T010: Test MCP write operations for user recipes and processed data.
This test will fail initially until the MCP write functionality is implemented.
"""

from unittest.mock import patch

import pytest

from t2d_kit.mcp.write import MCPWriter
from t2d_kit.models.processed_recipe import ProcessedRecipe
from t2d_kit.models.user_recipe import UserRecipe


class TestMCPWrite:
    """Test cases for MCP write operations."""

    def test_mcp_writer_initialization(self):
        """Test that MCPWriter can be initialized."""
        writer = MCPWriter()
        assert writer is not None
        assert hasattr(writer, "write_user_recipe")
        assert hasattr(writer, "write_processed_recipe")

    @patch("t2d_kit.mcp.write.mcp_client")
    def test_write_user_recipe_success(self, mock_client):
        """Test successful writing of user recipe via MCP."""
        recipe_data = {
            "name": "New Recipe",
            "description": "A new test recipe",
            "components": ["comp1", "comp2"],
            "connections": [{"from": "comp1", "to": "comp2"}],
        }
        recipe = UserRecipe(**recipe_data)

        mock_client.call_tool.return_value = {"id": "new_recipe_123", "status": "created"}

        writer = MCPWriter()
        result = writer.write_user_recipe(recipe)

        assert result["id"] == "new_recipe_123"
        assert result["status"] == "created"
        mock_client.call_tool.assert_called_once_with("write_user_recipe", recipe.to_dict())

    @patch("t2d_kit.mcp.write.mcp_client")
    def test_update_user_recipe(self, mock_client):
        """Test updating an existing user recipe."""
        recipe_data = {
            "name": "Updated Recipe",
            "description": "Updated description",
            "components": ["comp1", "comp2", "comp3"],
            "connections": [{"from": "comp1", "to": "comp2"}],
        }
        recipe = UserRecipe(**recipe_data)

        mock_client.call_tool.return_value = {"id": "recipe_123", "status": "updated"}

        writer = MCPWriter()
        result = writer.update_user_recipe("recipe_123", recipe)

        assert result["status"] == "updated"
        mock_client.call_tool.assert_called_once_with(
            "update_user_recipe", {"id": "recipe_123", **recipe.to_dict()}
        )

    @patch("t2d_kit.mcp.write.mcp_client")
    def test_write_processed_recipe(self, mock_client):
        """Test writing processed recipe data."""
        user_recipe_data = {
            "name": "Process Test",
            "description": "For processing",
            "components": ["a", "b"],
            "connections": [{"from": "a", "to": "b"}],
        }
        user_recipe = UserRecipe(**user_recipe_data)

        processed_data = {
            "nodes": [
                {"id": "a", "label": "Component A", "shape": "rectangle"},
                {"id": "b", "label": "Component B", "shape": "circle"},
            ],
            "edges": [{"from": "a", "to": "b", "label": "connection"}],
            "layout": "hierarchical",
        }

        processed_recipe = ProcessedRecipe(user_recipe=user_recipe, processed_data=processed_data)

        mock_client.call_tool.return_value = {"id": "processed_123", "status": "saved"}

        writer = MCPWriter()
        result = writer.write_processed_recipe(processed_recipe)

        assert result["id"] == "processed_123"
        assert result["status"] == "saved"
        mock_client.call_tool.assert_called_once_with(
            "write_processed_recipe", processed_recipe.to_dict()
        )

    @patch("t2d_kit.mcp.write.mcp_client")
    def test_delete_user_recipe(self, mock_client):
        """Test deleting a user recipe."""
        mock_client.call_tool.return_value = {"status": "deleted"}

        writer = MCPWriter()
        result = writer.delete_user_recipe("recipe_to_delete")

        assert result["status"] == "deleted"
        mock_client.call_tool.assert_called_once_with(
            "delete_user_recipe", {"id": "recipe_to_delete"}
        )

    @patch("t2d_kit.mcp.write.mcp_client")
    def test_write_user_recipe_failure(self, mock_client):
        """Test handling of write failures."""
        recipe_data = {
            "name": "Fail Recipe",
            "description": "Will fail to write",
            "components": ["comp1"],
            "connections": [],
        }
        recipe = UserRecipe(**recipe_data)

        mock_client.call_tool.side_effect = Exception("Write failed")

        writer = MCPWriter()
        with pytest.raises(Exception, match="Write failed"):
            writer.write_user_recipe(recipe)

    def test_mcp_writer_validation(self):
        """Test that MCPWriter validates input before writing."""
        writer = MCPWriter()

        # Test that writer validates UserRecipe objects
        with pytest.raises(TypeError):
            writer.write_user_recipe("not_a_recipe")

        # Test that writer validates ProcessedRecipe objects
        with pytest.raises(TypeError):
            writer.write_processed_recipe("not_a_processed_recipe")

    @patch("t2d_kit.mcp.write.mcp_client")
    def test_batch_write_user_recipes(self, mock_client):
        """Test writing multiple user recipes in batch."""
        recipes = []
        for i in range(3):
            recipe_data = {
                "name": f"Batch Recipe {i+1}",
                "description": f"Batch recipe number {i+1}",
                "components": [f"comp{i+1}"],
                "connections": [],
            }
            recipes.append(UserRecipe(**recipe_data))

        mock_client.call_tool.return_value = {"written": 3, "ids": ["batch1", "batch2", "batch3"]}

        writer = MCPWriter()
        result = writer.batch_write_user_recipes(recipes)

        assert result["written"] == 3
        assert len(result["ids"]) == 3
        mock_client.call_tool.assert_called_once()
