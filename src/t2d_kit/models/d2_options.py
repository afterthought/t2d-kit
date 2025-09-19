"""T021: D2Options model for advanced D2 diagram configuration."""

import os
import warnings
from typing import Literal

from pydantic import Field, field_validator

from .base import T2DBaseModel


class D2Options(T2DBaseModel):
    """Advanced D2 diagram configuration options."""

    # Layout engines
    layout_engine: Literal["dagre", "elk", "tala"] = Field(
        default="dagre",
        description="D2 layout engine to use"
    )

    # Themes
    theme: Literal["neutral-default", "neutral-grey", "flagship-terrastruct", "cool-classics", "mixed-berry-blue", "grape-soda", "aubergine", "colorblind-clear", "vanilla-nitro-cola", "orange-creamsicle", "shirley-temple", "earth-tones", "everglade", "buttered-toast"] | None = Field(
        default="neutral-default",
        description="D2 theme to apply"
    )

    # Rendering options
    sketch: bool = Field(
        default=False,
        description="Enable hand-drawn sketch mode"
    )

    pad: int = Field(
        default=100,
        ge=0,
        description="Padding around the diagram in pixels"
    )

    # Animation options
    animate_interval: int | None = Field(
        default=None,
        ge=0,
        description="Animation interval in milliseconds for multi-board diagrams"
    )

    # Size constraints
    width: int | None = Field(
        default=None,
        gt=0,
        description="Target width in pixels"
    )

    height: int | None = Field(
        default=None,
        gt=0,
        description="Target height in pixels"
    )

    # Export options
    scale: float = Field(
        default=1.0,
        gt=0,
        le=4,
        description="Scale factor for output (0.5 = 50%, 2 = 200%)"
    )

    # Advanced layout options
    direction: Literal["up", "down", "right", "left"] = Field(
        default="down",
        description="Primary direction for layout flow"
    )

    # Font configuration
    font_family: str | None = Field(
        default=None,
        description="Override default font family"
    )

    font_size: int | None = Field(
        default=None,
        ge=8,
        le=72,
        description="Base font size in points"
    )

    # Connection styling
    stroke_width: int | None = Field(
        default=None,
        ge=1,
        le=10,
        description="Default stroke width for connections"
    )

    # Multi-board options
    board_index: int | None = Field(
        default=None,
        ge=0,
        description="Specific board index to render from multi-board diagram"
    )

    # Compiler options
    force_appendix: bool = Field(
        default=False,
        description="Force rendering of appendix elements"
    )

    center: bool = Field(
        default=False,
        description="Center the diagram in the viewport"
    )

    @field_validator('layout_engine')
    @classmethod
    def validate_tala_license(cls, v: str) -> str:
        """Warn if Tala is selected without license."""
        if v == "tala":
            # Check for TALA_LICENSE_KEY env var
            if not os.environ.get("TALA_LICENSE_KEY"):
                warnings.warn(
                    "Tala layout engine requires a license key. "
                    "Set TALA_LICENSE_KEY environment variable.",
                    UserWarning
                )
        return v

    def to_cli_args(self) -> list[str]:
        """Convert options to D2 CLI arguments."""
        args = []

        # Add layout engine
        args.extend(["--layout", self.layout_engine])

        # Add theme if specified
        if self.theme:
            args.extend(["--theme", self.theme])

        # Add sketch mode
        if self.sketch:
            args.append("--sketch")

        # Add padding
        args.extend(["--pad", str(self.pad)])

        # Add dimensions if specified
        if self.width:
            args.extend(["--width", str(self.width)])
        if self.height:
            args.extend(["--height", str(self.height)])

        # Add scale
        if self.scale != 1.0:
            args.extend(["--scale", str(self.scale)])

        # Add animation interval for multi-board
        if self.animate_interval:
            args.extend(["--animate-interval", str(self.animate_interval)])

        # Add direction
        args.extend(["--direction", self.direction])

        # Add board index if specified
        if self.board_index is not None:
            args.extend(["--board", str(self.board_index)])

        # Add force appendix
        if self.force_appendix:
            args.append("--force-appendix")

        # Add center
        if self.center:
            args.append("--center")

        return args

    def to_style_string(self) -> str:
        """Generate D2 style configuration string."""
        styles = []

        if self.font_family:
            styles.append(f"font: {self.font_family}")

        if self.font_size:
            styles.append(f"font-size: {self.font_size}")

        if self.stroke_width:
            styles.append(f"stroke-width: {self.stroke_width}")

        if styles:
            return f"style: {{\n  {chr(10).join(styles)}\n}}"
        return ""

    def get_output_flags(self, output_format: str) -> list[str]:
        """Get format-specific output flags."""
        format_flags = {
            "svg": [],
            "png": ["--format", "png"],
            "pdf": ["--format", "pdf"]
        }
        return format_flags.get(output_format.lower(), [])

    def validate_compatibility(self) -> list[str]:
        """Validate option compatibility and return warnings."""
        warnings = []

        # Check for incompatible combinations
        if self.sketch and self.theme in ["flagship-terrastruct", "cool-classics"]:
            warnings.append("Sketch mode may not work well with complex themes")

        if self.animate_interval and not self.board_index:
            warnings.append("Animation interval is only effective with multi-board diagrams")

        if self.width and self.height and self.scale != 1.0:
            warnings.append("Explicit dimensions with scaling may produce unexpected results")

        return warnings
