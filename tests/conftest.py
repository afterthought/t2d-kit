"""Pytest configuration and shared fixtures for t2d-kit tests."""

import asyncio
import json
import sys
import tempfile
from collections.abc import AsyncGenerator, Generator
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio
from fastmcp import FastMCP

# Add src to path for imports
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the test session."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def mcp_server() -> AsyncGenerator[FastMCP, None]:
    """Create a test MCP server instance."""
    server = FastMCP("test-t2d-kit")
    yield server


@pytest_asyncio.fixture
async def mcp_context():
    """Create a test MCP context for tool testing."""
    # Create a simple mock context since fastmcp.testing is not available
    context = MagicMock()
    context.user = {"id": "test-user"}
    context.session = {"id": "test-session"}
    return context


@pytest.fixture
def temp_recipe_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for recipe files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        recipe_dir = Path(tmpdir) / "recipes"
        recipe_dir.mkdir()
        yield recipe_dir


@pytest.fixture
def sample_user_recipe() -> dict:
    """Provide a sample user recipe for testing."""
    return {
        "name": "test-system",
        "prd": {
            "content": """# Test System PRD

## Overview
A test system for validation.

## Features
- User management
- Data processing
"""
        },
        "instructions": {
            "diagrams": [
                {
                    "type": "flowchart",
                    "description": "System flow",
                    "framework_preference": "mermaid"
                },
                {
                    "type": "erd",
                    "description": "Database schema",
                    "framework_preference": "d2"
                }
            ],
            "documentation": {
                "style": "technical",
                "audience": "developers",
                "sections": ["Overview", "Architecture"]
            }
        }
    }


@pytest.fixture
def sample_processed_recipe() -> dict:
    """Provide a sample processed recipe for testing."""
    return {
        "name": "test-system",
        "version": "1.0.0",
        "source_recipe": "./recipes/test-system.yaml",
        "generated_at": "2025-09-18T10:00:00Z",
        "diagram_specs": [
            {
                "id": "flow-001",
                "type": "flowchart",
                "framework": "mermaid",
                "agent": "t2d-mermaid-generator",
                "title": "System Flow",
                "instructions": "Create a flowchart showing the system flow",
                "output_file": "docs/assets/system-flow.mmd",
                "output_formats": ["svg", "png"],
                "options": {}
            }
        ],
        "content_files": [
            {
                "id": "overview",
                "path": "docs/overview.md",
                "type": "documentation",
                "agent": "t2d-markdown-maintainer",
                "base_prompt": "Create overview documentation",
                "diagram_refs": ["flow-001"],
                "title": "System Overview",
                "last_updated": "2025-09-18T10:00:00Z"
            }
        ],
        "diagram_refs": [
            {
                "id": "flow-001",
                "title": "System Flow",
                "type": "flowchart",
                "expected_path": "docs/assets/system-flow.svg",
                "status": "pending"
            }
        ],
        "outputs": {
            "assets_dir": "docs/assets",
            "mkdocs": {
                "config_file": "mkdocs.yml",
                "site_name": "Test System Documentation"
            }
        }
    }


@pytest.fixture
def sample_diagram_types() -> list:
    """Provide sample diagram types for testing."""
    return [
        {
            "type_id": "flowchart",
            "name": "Flowchart",
            "framework": "mermaid",
            "description": "Process flow visualization",
            "example_usage": "Show the order processing workflow",
            "supported_frameworks": ["mermaid", "d2"]
        },
        {
            "type_id": "sequence",
            "name": "Sequence Diagram",
            "framework": "mermaid",
            "description": "Interaction sequences between components",
            "example_usage": "Show API call sequence",
            "supported_frameworks": ["mermaid", "plantuml"]
        },
        {
            "type_id": "erd",
            "name": "Entity Relationship Diagram",
            "framework": "d2",
            "description": "Database schema visualization",
            "example_usage": "Show database tables and relationships",
            "supported_frameworks": ["d2", "plantuml"]
        }
    ]


@pytest.fixture
def mock_yaml_file(temp_recipe_dir, sample_user_recipe) -> Path:
    """Create a mock YAML recipe file."""
    import yaml

    file_path = temp_recipe_dir / "test-recipe.yaml"
    with open(file_path, "w") as f:
        yaml.safe_dump(sample_user_recipe, f)
    return file_path


@pytest.fixture
def mock_processed_yaml_file(temp_recipe_dir, sample_processed_recipe) -> Path:
    """Create a mock processed YAML recipe file."""
    import yaml

    file_path = temp_recipe_dir / "test-recipe.t2d.yaml"
    with open(file_path, "w") as f:
        yaml.safe_dump(sample_processed_recipe, f)
    return file_path


@pytest.fixture
def performance_timer():
    """Simple timer for performance testing."""
    import time

    class Timer:
        def __init__(self):
            self.start_time = None
            self.elapsed = None

        def __enter__(self):
            self.start_time = time.perf_counter()
            return self

        def __exit__(self, *args):
            self.elapsed = (time.perf_counter() - self.start_time) * 1000  # Convert to ms

    return Timer
