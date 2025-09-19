"""MCP server package for t2d-kit."""

from .resources import register_resources
from .server import create_server, main
from .tools import register_tools

__all__ = [
    "create_server",
    "main",
    "register_resources",
    "register_tools",
]
