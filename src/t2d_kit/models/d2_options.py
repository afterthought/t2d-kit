"""T021: D2Options model for advanced D2 diagram configuration."""

import os
import warnings
from typing import Literal, Optional

from pydantic import Field, field_validator, model_validator

from .base import T2DBaseModel


class D2Options(T2DBaseModel):
    """Advanced D2 diagram configuration options."""

    # Layout engines
    layout_engine: Literal["dagre", "elk", "tala"] | None = Field(
        default=None, description="D2 layout engine to use (auto-detect if None)"
    )

    # Diagram type hint for auto-detection
    diagram_type: str | None = Field(
        default=None,
        description="Diagram type hint for layout auto-detection",
        exclude=True  # Don't include in serialization
    )

    # Themes
    theme: (
        Literal[
            "neutral-default",
            "neutral-grey",
            "flagship-terrastruct",
            "cool-classics",
            "mixed-berry-blue",
            "grape-soda",
            "aubergine",
            "colorblind-clear",
            "vanilla-nitro-cola",
            "orange-creamsicle",
            "shirley-temple",
            "earth-tones",
            "everglade",
            "buttered-toast",
        ]
        | None
    ) = Field(default="neutral-default", description="D2 theme to apply")

    # Rendering options
    sketch: bool = Field(default=False, description="Enable hand-drawn sketch mode")

    pad: int = Field(default=100, ge=0, description="Padding around the diagram in pixels")

    # Animation options
    animate_interval: int | None = Field(
        default=None,
        ge=0,
        description="Animation interval in milliseconds for multi-board diagrams",
    )

    # Size constraints
    width: int | None = Field(default=None, gt=0, description="Target width in pixels")

    height: int | None = Field(default=None, gt=0, description="Target height in pixels")

    # Export options
    scale: float = Field(
        default=1.0, gt=0, le=4, description="Scale factor for output (0.5 = 50%, 2 = 200%)"
    )

    # Advanced layout options
    direction: Literal["up", "down", "right", "left"] = Field(
        default="down", description="Primary direction for layout flow"
    )

    # Font configuration
    font_family: str | None = Field(default=None, description="Override default font family")

    font_size: int | None = Field(default=None, ge=8, le=72, description="Base font size in points")

    # Connection styling
    stroke_width: int | None = Field(
        default=None, ge=1, le=10, description="Default stroke width for connections"
    )

    # Multi-board options
    board_index: int | None = Field(
        default=None, ge=0, description="Specific board index to render from multi-board diagram"
    )

    # Compiler options
    force_appendix: bool = Field(default=False, description="Force rendering of appendix elements")

    center: bool = Field(default=False, description="Center the diagram in the viewport")

    @model_validator(mode="after")
    def auto_detect_layout_engine(self) -> "D2Options":
        """Auto-detect the best layout engine if not specified."""
        if self.layout_engine is None:
            # Import here to avoid circular dependency
            from t2d_kit.utils.d2_utils import get_default_layout_for_diagram

            # Use diagram type hint if available, otherwise default to dagre
            if self.diagram_type:
                self.layout_engine = get_default_layout_for_diagram(self.diagram_type)
            else:
                self.layout_engine = "dagre"

        # Validate Tala license if Tala is selected
        if self.layout_engine == "tala" and not os.environ.get("TALA_LICENSE_KEY"):
            # Check if Tala is actually installed
            from t2d_kit.utils.d2_utils import is_tala_installed

            if is_tala_installed():
                warnings.warn(
                    "Tala layout engine may require a license key for full features. "
                    "Set TALA_LICENSE_KEY environment variable if you have a license.",
                    UserWarning,
                    stacklevel=2,
                )

        return self

    def to_cli_args(self) -> list[str]:
        """Convert options to D2 CLI arguments."""
        args = []

        # Add layout engine
        args.extend(["--layout", self.layout_engine])

        # Add theme if specified
        if self.theme:
            # Map theme names to numeric IDs that D2 expects
            theme_map = {
                "neutral-default": "0",
                "neutral-grey": "1",
                "flagship-terrastruct": "2",
                "cool-classics": "3",
                "mixed-berry-blue": "4",
                "grape-soda": "5",
                "aubergine": "6",
                "colorblind-clear": "3",  # same as cool-classics
                "vanilla-nitro-cola": "4",  # same as mixed-berry-blue
                "orange-creamsicle": "5",  # same as grape-soda
                "shirley-temple": "6",  # same as aubergine
                "earth-tones": "7",
                "everglade": "0",  # fallback to default
                "buttered-toast": "0",  # fallback to default
            }
            theme_id = theme_map.get(self.theme, "0")
            args.extend(["--theme", theme_id])

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
        format_flags = {"svg": [], "png": ["--format", "png"], "pdf": ["--format", "pdf"]}
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

    @classmethod
    def for_architectural_diagram(cls, diagram_type: str) -> "D2Options":
        """Create D2Options optimized for architectural diagrams.

        Args:
            diagram_type: The type of diagram (e.g., "c4_container")

        Returns:
            D2Options configured for architectural diagrams with Tala if available
        """
        return cls(
            diagram_type=diagram_type,
            # Layout will auto-detect to Tala if available
            layout_engine=None,
            # Good defaults for architectural diagrams
            theme="neutral-default",
            pad=120,  # More padding for complex diagrams
            direction="down",  # Top-down is typical for architecture
            center=True,  # Center in viewport
        )
