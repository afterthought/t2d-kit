"""T024: MarpConfig model for advanced Marp presentation configuration."""

from pathlib import Path
from typing import Any, Literal

from pydantic import Field, field_validator

from .base import T2DBaseModel


class MarpConfig(T2DBaseModel):
    """Advanced Marp presentation configuration with directives and exports."""

    # Theme configuration
    theme: Literal[
        "default",
        "gaia",
        "uncover",
        # Custom themes can be added
    ] = Field(default="default", description="Marp theme to apply")

    custom_theme_path: Path | None = Field(
        default=None, description="Path to custom CSS theme file"
    )

    # Global directives
    marp: bool = Field(default=True, description="Enable Marp rendering")

    size: Literal["4:3", "16:9", "4K", "A4", "Letter"] = Field(
        default="16:9", description="Slide size/aspect ratio"
    )

    paginate: bool = Field(default=True, description="Show page numbers")

    header: str | None = Field(default=None, description="Global header text for all slides")

    footer: str | None = Field(default=None, description="Global footer text for all slides")

    # Style configuration
    style: str | None = Field(default=None, description="Custom CSS styles")

    background_color: str | None = Field(default=None, description="Default background color")

    background_image: str | None = Field(
        default=None, description="URL or path to background image"
    )

    background_size: Literal["cover", "contain", "auto", "fit"] = Field(
        default="cover", description="Background image sizing"
    )

    # Typography
    font_family: str | None = Field(default=None, description="Primary font family")

    font_size: str | None = Field(default=None, description="Base font size (e.g., '28px', '2em')")

    # Color scheme
    color: str | None = Field(default=None, description="Default text color")

    # Slide-specific directives
    class_: str | None = Field(
        default=None, alias="class", description="CSS class to apply to slides"
    )

    # Transition effects (for HTML export)
    transition: Literal["none", "fade", "slide", "convex", "concave", "zoom", "linear"] | None = (
        Field(default=None, description="Slide transition effect for HTML export")
    )

    transition_speed: Literal["slow", "default", "fast"] = Field(
        default="default", description="Transition speed"
    )

    # Export configurations
    html_options: dict[str, Any] | None = Field(default=None, description="HTML export options")

    pdf_options: dict[str, Any] | None = Field(default=None, description="PDF export options")

    pptx_options: dict[str, Any] | None = Field(
        default=None, description="PowerPoint export options"
    )

    # Advanced features
    math: Literal["katex", "mathjax", None] = Field(
        default="katex", description="Math rendering engine"
    )

    emoji_shortcode: bool = Field(default=True, description="Enable emoji shortcodes like :smile:")

    html: bool = Field(default=True, description="Allow raw HTML in markdown")

    # Auto-play configuration (for HTML)
    auto_play: int | None = Field(
        default=None, ge=0, description="Auto-advance slides after N seconds (0 = disabled)"
    )

    loop: bool = Field(default=False, description="Loop presentation when auto-playing")

    # Speaker notes
    notes: bool = Field(default=True, description="Enable speaker notes")

    @field_validator("custom_theme_path")
    @classmethod
    def validate_theme_exists(cls, v: Path | None) -> Path | None:
        """Check if custom theme file exists."""
        if v and not v.exists():
            raise ValueError(f"Custom theme file not found: {v}")
        return v

    def to_frontmatter(self) -> str:
        """Generate Marp frontmatter for markdown file."""
        fm = ["---"]

        # Core directives
        fm.append(f"marp: {str(self.marp).lower()}")
        fm.append(f"theme: {self.theme}")
        fm.append(f"size: {self.size}")
        fm.append(f"paginate: {str(self.paginate).lower()}")

        # Optional directives
        if self.header:
            fm.append(f"header: '{self.header}'")
        if self.footer:
            fm.append(f"footer: '{self.footer}'")
        if self.background_color:
            fm.append(f"backgroundColor: {self.background_color}")
        if self.background_image:
            fm.append(f"backgroundImage: url('{self.background_image}')")
        if self.background_size:
            fm.append(f"backgroundSize: {self.background_size}")
        if self.color:
            fm.append(f"color: {self.color}")
        if self.class_:
            fm.append(f"class: {self.class_}")
        if self.math:
            fm.append(f"math: {self.math}")

        # Style block
        if self.style or self.font_family or self.font_size:
            fm.append("style: |")
            if self.font_family or self.font_size:
                fm.append("  section {")
                if self.font_family:
                    fm.append(f"    font-family: {self.font_family};")
                if self.font_size:
                    fm.append(f"    font-size: {self.font_size};")
                fm.append("  }")
            if self.style:
                for line in self.style.strip().split("\n"):
                    fm.append(f"  {line}")

        fm.append("---")
        fm.append("")  # Empty line after frontmatter

        return "\n".join(fm)

    def to_cli_args(self) -> list[str]:
        """Convert to Marp CLI arguments."""
        args = []

        # Theme
        if self.custom_theme_path:
            args.extend(["--theme", str(self.custom_theme_path)])
        elif self.theme != "default":
            args.extend(["--theme", self.theme])

        # HTML options
        if self.html:
            args.append("--html")

        # Math
        if self.math:
            args.extend(["--math", self.math])

        # PDF options
        if self.pdf_options:
            if self.pdf_options.get("format"):
                args.extend(["--pdf-format", self.pdf_options["format"]])
            if self.pdf_options.get("landscape"):
                args.append("--pdf-landscape")

        # Allow local files
        args.append("--allow-local-files")

        return args

    def to_engine_config(self) -> dict[str, Any]:
        """Generate Marp engine configuration."""
        config = {"html": self.html, "emoji": {"shortcode": self.emoji_shortcode}}

        if self.math:
            config["math"] = self.math

        if self.html_options:
            config["options"] = self.html_options

        return config

    def get_default_html_options(self) -> dict[str, Any]:
        """Get default HTML export options."""
        return {
            "printable": True,
            "progress": True,
            "controls": True,
            "controlsLayout": "bottom-right",
            "controlsTutorial": True,
            "hash": True,
            "respondToHashChanges": True,
        }

    def get_default_pdf_options(self) -> dict[str, Any]:
        """Get default PDF export options."""
        return {
            "format": "A4",
            "landscape": True,
            "printBackground": True,
            "displayHeaderFooter": True,
            "margin": {"top": "1cm", "right": "1cm", "bottom": "1cm", "left": "1cm"},
        }

    def get_default_pptx_options(self) -> dict[str, Any]:
        """Get default PowerPoint export options."""
        return {"output_width": 1920, "output_height": 1080}

    def apply_theme_defaults(self, theme_name: str) -> None:
        """Apply default settings for specific themes."""
        theme_defaults = {
            "gaia": {
                "font_family": "'Avenir Next', 'Hiragino Kaku Gothic ProN', 'Meiryo', sans-serif",
                "background_color": "#fafafa",
            },
            "uncover": {
                "font_family": "'Liberation Sans', 'Hiragino Sans', sans-serif",
                "background_color": "#ffffff",
            },
            "default": {"font_family": "'Helvetica Neue', Arial, sans-serif"},
        }

        if theme_name in theme_defaults:
            defaults = theme_defaults[theme_name]
            if not self.font_family and "font_family" in defaults:
                self.font_family = defaults["font_family"]
            if not self.background_color and "background_color" in defaults:
                self.background_color = defaults["background_color"]

    def get_slide_break_syntax(self) -> str:
        """Get the syntax for slide breaks."""
        return "\n---\n\n"

    def get_speaker_notes_syntax(self, notes: str) -> str:
        """Get syntax for speaker notes."""
        if not self.notes:
            return ""

        return f"\n<!-- _footer: '' -->\n<!-- _paginate: false -->\n\n{notes}\n\n---\n"


class SlideDirective(T2DBaseModel):
    """Individual slide directives for fine control."""

    # Layout directives
    class_: Literal["lead", "invert", "fit", "centered"] | None = Field(default=None, alias="class")

    # Background directives (per slide)
    bg: str | None = Field(default=None, description="Background color or image URL")

    bg_color: str | None = Field(default=None, description="Background color")

    bg_image: str | None = Field(default=None, description="Background image URL")

    bg_size: str | None = Field(default=None, description="Background size")

    # Pagination
    paginate_skip: bool = Field(default=False, description="Skip page number on this slide")

    # Header/Footer overrides
    header: str | None = None
    footer: str | None = None

    def to_markdown_comment(self) -> str:
        """Convert to HTML comment for slide."""
        directives = []

        if self.class_:
            directives.append(f"_class: {self.class_}")
        if self.bg:
            directives.append(f"bg: {self.bg}")
        if self.bg_color:
            directives.append(f"backgroundColor: {self.bg_color}")
        if self.bg_image:
            directives.append(f"backgroundImage: url('{self.bg_image}')")
        if self.bg_size:
            directives.append(f"backgroundSize: {self.bg_size}")
        if self.paginate_skip:
            directives.append("_paginate: false")
        if self.header is not None:
            directives.append(f"_header: '{self.header}'")
        if self.footer is not None:
            directives.append(f"_footer: '{self.footer}'")

        if directives:
            return f"<!-- {' '.join(directives)} -->"
        return ""
