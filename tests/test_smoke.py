"""Basic smoke tests to verify the package imports and works."""

import pytest


def test_package_imports():
    """Test that the main package can be imported."""
    import t2d_kit
    assert t2d_kit is not None


def test_models_import():
    """Test that models can be imported."""
    from t2d_kit.models import ProcessedRecipe, UserRecipe
    assert UserRecipe is not None
    assert ProcessedRecipe is not None


def test_base_model_import():
    """Test that base model can be imported."""
    from t2d_kit.models.base import T2DBaseModel
    assert T2DBaseModel is not None


def test_simple_user_recipe():
    """Test creating a simple UserRecipe."""
    from t2d_kit.models.user_recipe import UserRecipe

    recipe_data = {
        "name": "TestProject",
        "prd": {
            "content": "# Test PRD\n\nThis is a test.",
            "format": "markdown"
        },
        "instructions": {
            "diagrams": [
                {
                    "type": "architecture",
                    "description": "System architecture"
                }
            ]
        }
    }

    recipe = UserRecipe(**recipe_data)
    assert recipe.name == "TestProject"
    assert recipe.prd.content.startswith("# Test PRD")
    assert len(recipe.instructions.diagrams) == 1


def test_version():
    """Test that version is accessible."""
    from t2d_kit._version import __version__
    assert __version__ is not None
    assert isinstance(__version__, str)


@pytest.mark.parametrize("module_name", [
    "t2d_kit.models.base",
    "t2d_kit.models.user_recipe",
    "t2d_kit.models.processed_recipe",
    "t2d_kit.models.state",
    "t2d_kit.models.diagram",
    "t2d_kit.models.content",
])
def test_module_imports(module_name):
    """Test that various modules can be imported."""
    import importlib
    module = importlib.import_module(module_name)
    assert module is not None
