"""t2d-kit: Multi-Framework Diagram Pipeline.

Transform requirements into beautiful diagrams and documentation using self-organizing agents.
"""

__version__ = "0.1.0"

# Re-export main components
from .models.base import T2DBaseModel

__all__ = ["T2DBaseModel", "__version__"]
