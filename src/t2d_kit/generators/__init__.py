"""T2D-Kit Generators Package

This package contains generator classes that wrap the agent-based architecture
for integration testing and compatibility with traditional class-based interfaces.

These generators provide a Python class interface to the underlying
Claude Code agent system.
"""

from .d2_generator import D2Generator

__all__ = [
    "D2Generator",
]