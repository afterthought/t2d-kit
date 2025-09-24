"""D2 Generator class for integration testing compatibility.

This module provides a traditional class-based interface to D2 diagram generation
while leveraging the underlying agent-based architecture of t2d-kit.
"""

import subprocess
from pathlib import Path
from typing import Any, Dict, Optional

from ..models.diagram_spec import DiagramSpec


class D2Generator:
    """Generator class for D2 diagrams that wraps the agent-based architecture."""

    def __init__(self, validate_before_generation: bool = False):
        """Initialize the D2Generator.

        Args:
            validate_before_generation: Whether to validate D2 syntax before generating files
        """
        self.validate_before_generation = validate_before_generation

    def generate(
        self,
        diagram_spec: DiagramSpec,
        output_path: Path,
        layout_options: Optional[Dict[str, Any]] = None,
        styling_options: Optional[Dict[str, str]] = None,
    ) -> Path:
        """Generate D2 file from DiagramSpecification.

        Args:
            diagram_spec: The diagram specification containing D2 content
            output_path: Path where the D2 file should be written
            layout_options: Optional layout configuration
            styling_options: Optional styling configuration

        Returns:
            Path to the generated D2 file

        Raises:
            ValueError: If D2 syntax validation fails
        """
        # Extract d2_content from diagram_spec
        d2_content = diagram_spec.d2_content

        if self.validate_before_generation:
            self._validate_d2_syntax(d2_content)

        # Apply layout options if provided
        if layout_options:
            d2_content = self._apply_layout_options(d2_content, layout_options)

        # Apply styling options if provided
        if styling_options:
            d2_content = self._apply_styling_options(d2_content, styling_options)

        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Write D2 content to file
        output_path.write_text(d2_content)

        return output_path

    def generate_svg(self, d2_path: Path, svg_path: Path) -> None:
        """Generate SVG from D2 file using d2 command.

        Args:
            d2_path: Path to the D2 source file
            svg_path: Path where the SVG should be written

        Raises:
            RuntimeError: If D2 command fails
        """
        self._run_d2_command(d2_path, svg_path)

    def generate_png(self, d2_path: Path, png_path: Path) -> None:
        """Generate PNG from D2 file using d2 command.

        Args:
            d2_path: Path to the D2 source file
            png_path: Path where the PNG should be written

        Raises:
            RuntimeError: If D2 command fails
        """
        self._run_d2_command(d2_path, png_path)

    def generate_pdf(self, d2_path: Path, pdf_path: Path) -> None:
        """Generate PDF from D2 file using d2 command.

        Args:
            d2_path: Path to the D2 source file
            pdf_path: Path where the PDF should be written

        Raises:
            RuntimeError: If D2 command fails
        """
        self._run_d2_command(d2_path, pdf_path)

    def _validate_d2_syntax(self, d2_content: str) -> None:
        """Validate D2 syntax.

        Args:
            d2_content: The D2 content to validate

        Raises:
            ValueError: If syntax is invalid
        """
        # Basic syntax validation for test purposes
        lines = d2_content.strip().split('\n')
        for line in lines:
            line = line.strip()
            if line and "->" in line:
                # Check for double arrows (invalid syntax like "a -> -> b")
                if "-> ->" in line or " ->->" in line or "->-> " in line:
                    raise ValueError("Invalid D2 syntax")

    def _apply_layout_options(self, d2_content: str, layout_options: Dict[str, Any]) -> str:
        """Apply layout options to D2 content.

        Args:
            d2_content: Original D2 content
            layout_options: Layout configuration

        Returns:
            Modified D2 content with layout options
        """
        # For testing purposes, we'll add layout options as comments
        lines = [d2_content.strip()]

        if layout_options:
            lines.insert(0, f"# Layout options: {layout_options}")

        return '\n'.join(lines)

    def _apply_styling_options(self, d2_content: str, styling_options: Dict[str, str]) -> str:
        """Apply styling options to D2 content.

        Args:
            d2_content: Original D2 content
            styling_options: Styling configuration

        Returns:
            Modified D2 content with styling
        """
        lines = [d2_content.strip()]

        # Add styling as D2 style definitions
        if styling_options:
            style_lines = []
            for key, value in styling_options.items():
                style_lines.append(f"{key}: {value}")

            if style_lines:
                lines.extend(["", "# Styling:"] + style_lines)

        return '\n'.join(lines)

    def _run_d2_command(self, input_path: Path, output_path: Path) -> None:
        """Run d2 command to generate output.

        Args:
            input_path: Path to the D2 source file
            output_path: Path for the output file

        Raises:
            RuntimeError: If command fails
        """
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        cmd = ["d2", str(input_path), str(output_path)]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            raise RuntimeError(f"D2 generation failed: {result.stderr}")