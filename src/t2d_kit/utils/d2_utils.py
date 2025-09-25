"""Utilities for D2 diagram generation."""

import subprocess
from functools import lru_cache


@lru_cache(maxsize=1)
def is_tala_installed() -> bool:
    """Check if Tala layout engine is installed for D2.

    Returns:
        bool: True if Tala is available, False otherwise
    """
    try:
        result = subprocess.run(
            ["d2", "layout"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return "tala" in result.stdout.lower()
    except (subprocess.SubprocessError, FileNotFoundError):
        return False


def get_default_layout_for_diagram(diagram_type: str) -> str:
    """Get the default layout engine for a diagram type.

    For architectural diagrams (C4, architecture types), prefer Tala if available.

    Args:
        diagram_type: The type of diagram being created

    Returns:
        str: The layout engine to use ("tala", "elk", or "dagre")
    """
    architectural_types = {
        "c4_context",
        "c4_container",
        "c4_component",
        "c4_deployment",
        "c4_landscape",
        "architecture",
        "system_architecture",
        "deployment",
    }

    # Check if this is an architectural diagram
    if diagram_type.lower() in architectural_types:
        # Prefer Tala for architectural diagrams if available
        if is_tala_installed():
            return "tala"
        # Fall back to ELK for better architectural layouts
        return "elk"

    # Use default dagre for other diagram types
    return "dagre"