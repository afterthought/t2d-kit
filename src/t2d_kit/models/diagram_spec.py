"""Simple DiagramSpec model for testing compatibility.

This module provides a simplified diagram specification model
for integration testing purposes.
"""

from typing import Optional

from pydantic import ConfigDict

from .base import T2DBaseModel


class DiagramSpec(T2DBaseModel):
    """Simplified diagram specification for testing."""

    model_config = ConfigDict(extra="allow")

    d2_content: str
    title: str
    description: Optional[str] = None