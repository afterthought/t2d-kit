"""T022: MermaidConfig model for advanced Mermaid diagram configuration."""

import json
from typing import Any, Literal

from pydantic import Field, model_validator

from .base import T2DBaseModel


class MermaidConfig(T2DBaseModel):
    """Advanced Mermaid diagram configuration options."""

    # Theme configuration
    theme: Literal[
        "default", "dark", "forest", "neutral",
        "base", "minimal", "neo", "future", "vintage"
    ] = Field(
        default="default",
        description="Mermaid theme to apply"
    )

    # Custom theme variables
    theme_variables: dict[str, str] | None = Field(
        default=None,
        description="Custom theme CSS variables"
    )

    # Layout configuration
    look_and_feel: Literal["classic", "handDrawn"] = Field(
        default="classic",
        description="Visual style of the diagram"
    )

    # Security level
    security_level: Literal["strict", "loose", "antiscript"] = Field(
        default="strict",
        description="Security level for rendering"
    )

    # Diagram-specific settings
    flowchart_config: dict[str, Any] | None = Field(
        default=None,
        description="Flowchart-specific configuration"
    )

    sequence_config: dict[str, Any] | None = Field(
        default=None,
        description="Sequence diagram configuration"
    )

    gantt_config: dict[str, Any] | None = Field(
        default=None,
        description="Gantt chart configuration"
    )

    er_config: dict[str, Any] | None = Field(
        default=None,
        description="ER diagram configuration"
    )

    pie_config: dict[str, Any] | None = Field(
        default=None,
        description="Pie chart configuration"
    )

    state_config: dict[str, Any] | None = Field(
        default=None,
        description="State diagram configuration"
    )

    # Rendering options
    width: int | None = Field(
        default=None,
        gt=0,
        description="Diagram width in pixels"
    )

    height: int | None = Field(
        default=None,
        gt=0,
        description="Diagram height in pixels"
    )

    background_color: str | None = Field(
        default="white",
        description="Background color (CSS color value)"
    )

    # Output options
    puppeteer_config: dict[str, Any] | None = Field(
        default=None,
        description="Puppeteer configuration for rendering"
    )

    # Font configuration
    font_family: str | None = Field(
        default=None,
        description="Override default font family"
    )

    # Accessibility
    wrap: bool = Field(
        default=False,
        description="Enable text wrapping in nodes"
    )

    @model_validator(mode='after')
    def apply_diagram_defaults(self) -> 'MermaidConfig':
        """Apply sensible defaults based on look_and_feel."""
        if self.look_and_feel == "handDrawn":
            if not self.theme_variables:
                self.theme_variables = {}
            # Apply hand-drawn style variables
            self.theme_variables.update({
                "fontFamily": "Kalam, cursive",
                "primaryBorderColor": "#666",
                "primaryColor": "#f9f9f9"
            })
        return self

    def to_config_json(self) -> str:
        """Generate mermaid configuration JSON."""
        config = {
            "theme": self.theme,
            "securityLevel": self.security_level,
            "look": self.look_and_feel
        }

        # Add theme variables
        if self.theme_variables:
            config["themeVariables"] = self.theme_variables

        # Add diagram-specific configs
        if self.flowchart_config:
            config["flowchart"] = self.flowchart_config
        if self.sequence_config:
            config["sequence"] = self.sequence_config
        if self.gantt_config:
            config["gantt"] = self.gantt_config
        if self.er_config:
            config["er"] = self.er_config
        if self.pie_config:
            config["pie"] = self.pie_config
        if self.state_config:
            config["state"] = self.state_config

        # Add font family
        if self.font_family:
            config["fontFamily"] = self.font_family

        # Add wrap
        config["wrap"] = self.wrap

        return json.dumps(config, indent=2)

    def to_cli_args(self) -> list[str]:
        """Convert to mermaid CLI (mmdc) arguments."""
        args = []

        # Add dimensions
        if self.width:
            args.extend(["--width", str(self.width)])
        if self.height:
            args.extend(["--height", str(self.height)])

        # Add background color
        if self.background_color:
            args.extend(["--backgroundColor", self.background_color])

        # Note: Configuration file would be written separately
        # and passed with --configFile flag
        config_json = self.to_config_json()
        if config_json != '{"theme": "default", "securityLevel": "strict", "look": "classic", "wrap": false}':
            args.extend(["--configFile", "<generated-config.json>"])

        return args

    def get_default_configs(self) -> dict[str, dict[str, Any]]:
        """Get default configurations for different diagram types."""
        return {
            "flowchart": {
                "curve": "linear",
                "padding": 10,
                "nodeSpacing": 50,
                "rankSpacing": 50,
                "diagramPadding": 8,
                "useMaxWidth": True,
                "htmlLabels": True
            },
            "sequence": {
                "diagramMarginX": 50,
                "diagramMarginY": 10,
                "actorMargin": 50,
                "width": 150,
                "height": 65,
                "boxMargin": 10,
                "boxTextMargin": 5,
                "noteMargin": 10,
                "messageMargin": 35,
                "mirrorActors": True,
                "bottomMarginAdj": 1,
                "useMaxWidth": True,
                "rightAngles": False,
                "showSequenceNumbers": False
            },
            "gantt": {
                "numberSectionStyles": 4,
                "axisFormat": "%Y-%m-%d",
                "topAxis": False,
                "displayMode": "compact",
                "gridLineStartPadding": 350,
                "fontSize": 11,
                "fontFamily": '"Open-Sans", sans-serif',
                "sectionFontSize": 11,
                "leftPadding": 75
            },
            "er": {
                "diagramPadding": 20,
                "layoutDirection": "TB",
                "minEntityWidth": 100,
                "minEntityHeight": 75,
                "entityPadding": 15,
                "stroke": "gray",
                "fill": "honeydew",
                "fontSize": 12,
                "useMaxWidth": True
            },
            "pie": {
                "useMaxWidth": True,
                "textPosition": 0.75,
                "legendPosition": "right"
            },
            "state": {
                "dividerMargin": 10,
                "sizeUnit": 5,
                "padding": 5,
                "textHeight": 10,
                "titleShift": -15,
                "noteMargin": 10,
                "forkWidth": 70,
                "forkHeight": 7,
                "miniPadding": 2,
                "fontSizeFactor": 5.02,
                "fontSize": 24,
                "labelHeight": 16,
                "edgeLengthFactor": "20",
                "compositTitleSize": 35,
                "radius": 5,
                "useMaxWidth": True
            }
        }

    def apply_diagram_type_defaults(self, diagram_type: str) -> None:
        """Apply default configuration for a specific diagram type."""
        defaults = self.get_default_configs()

        if diagram_type == "flowchart" and not self.flowchart_config:
            self.flowchart_config = defaults["flowchart"]
        elif diagram_type == "sequence" and not self.sequence_config:
            self.sequence_config = defaults["sequence"]
        elif diagram_type == "gantt" and not self.gantt_config:
            self.gantt_config = defaults["gantt"]
        elif diagram_type == "erd" and not self.er_config:
            self.er_config = defaults["er"]
        elif diagram_type == "pie" and not self.pie_config:
            self.pie_config = defaults["pie"]
        elif diagram_type == "state" and not self.state_config:
            self.state_config = defaults["state"]

    def get_theme_variables_for_style(self, style: str) -> dict[str, str]:
        """Get theme variables for common styles."""
        style_themes = {
            "corporate": {
                "primaryColor": "#0073e6",
                "primaryTextColor": "#ffffff",
                "primaryBorderColor": "#0073e6",
                "lineColor": "#666666",
                "secondaryColor": "#f0f8ff",
                "tertiaryColor": "#e6f3ff"
            },
            "dark": {
                "primaryColor": "#2d3748",
                "primaryTextColor": "#ffffff",
                "primaryBorderColor": "#4a5568",
                "lineColor": "#a0aec0",
                "secondaryColor": "#1a202c",
                "tertiaryColor": "#2d3748"
            },
            "colorful": {
                "primaryColor": "#ff6b6b",
                "primaryTextColor": "#ffffff",
                "primaryBorderColor": "#ff6b6b",
                "lineColor": "#4ecdc4",
                "secondaryColor": "#45b7d1",
                "tertiaryColor": "#96ceb4"
            }
        }
        return style_themes.get(style, {})

    def optimize_for_output_format(self, output_format: str) -> None:
        """Optimize configuration for specific output format."""
        if output_format.lower() == "png":
            # Optimize for PNG output
            if not self.width:
                self.width = 1920
            if not self.height:
                self.height = 1080
            self.background_color = "white"
        elif output_format.lower() == "svg":
            # Optimize for SVG output
            self.background_color = "transparent"
        elif output_format.lower() == "pdf":
            # Optimize for PDF output
            self.background_color = "white"
            if not self.width:
                self.width = 1920
