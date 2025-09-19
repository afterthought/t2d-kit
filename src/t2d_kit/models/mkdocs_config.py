"""T023: MkDocsPageConfig model for generating MkDocs-compatible pages."""

from datetime import datetime
from pathlib import Path
from typing import Any, Literal

from pydantic import Field

from .base import T2DBaseModel


class MkDocsPageConfig(T2DBaseModel):
    """Configuration for generating MkDocs-compatible pages to integrate into existing sites."""

    # Output configuration
    output_dir: Path = Field(
        default=Path("docs"),
        description="Directory where markdown pages will be generated"
    )

    pages_subdir: Path | None = Field(
        default=None,
        description="Subdirectory within output_dir for these pages (e.g., 'api', 'architecture')"
    )

    # Page metadata (for frontmatter)
    page_template: str | None = Field(
        default=None,
        description="Template name if the site uses custom templates"
    )

    page_category: str | None = Field(
        default=None,
        description="Category or section these pages belong to"
    )

    page_tags: list[str] | None = Field(
        default=None,
        description="Tags to apply to generated pages"
    )

    page_authors: list[str] | None = Field(
        default=None,
        description="Authors to credit in page metadata"
    )

    # Navigation hints
    nav_parent: str | None = Field(
        default=None,
        description="Parent section in nav where these pages should appear"
    )

    nav_position: int | None = Field(
        default=None,
        description="Position/weight in navigation ordering"
    )

    nav_title_prefix: str | None = Field(
        default=None,
        description="Prefix to add to page titles in navigation"
    )

    # Diagram integration
    diagrams_dir: str = Field(
        default="diagrams",
        description="Relative path from page location to diagrams directory"
    )

    diagram_format: Literal["svg", "png", "both"] = Field(
        default="svg",
        description="Preferred diagram format for embedding"
    )

    diagram_classes: list[str] | None = Field(
        default=None,
        description="CSS classes to apply to diagram images"
    )

    # Material theme features
    use_admonitions: bool = Field(
        default=True,
        description="Use Material admonition syntax for callouts"
    )

    use_content_tabs: bool = Field(
        default=False,
        description="Use Material content tabs for multi-version content"
    )

    use_annotations: bool = Field(
        default=False,
        description="Use Material annotations feature"
    )

    use_grids: bool = Field(
        default=False,
        description="Use Material grids for layout"
    )

    # Code block configuration
    code_highlight: bool = Field(
        default=True,
        description="Enable syntax highlighting in code blocks"
    )

    code_line_numbers: bool = Field(
        default=False,
        description="Show line numbers in code blocks"
    )

    code_copy_button: bool = Field(
        default=True,
        description="Add copy button to code blocks"
    )

    # Page generation options
    include_toc: bool = Field(
        default=True,
        description="Include table of contents in pages"
    )

    toc_depth: int = Field(
        default=3,
        ge=1,
        le=6,
        description="Maximum heading level for TOC"
    )

    include_edit_link: bool = Field(
        default=False,
        description="Include edit link (requires repo_url in main mkdocs.yml)"
    )

    include_created_date: bool = Field(
        default=False,
        description="Include creation date in page metadata"
    )

    include_updated_date: bool = Field(
        default=True,
        description="Include last updated date in page metadata"
    )

    # Index page generation
    generate_index: bool = Field(
        default=True,
        description="Generate an index page for the documentation set"
    )

    index_title: str = Field(
        default="Documentation",
        description="Title for the index page"
    )

    index_description: str | None = Field(
        default=None,
        description="Description for the index page"
    )

    # Cross-references
    cross_reference_base: str | None = Field(
        default=None,
        description="Base path for cross-references between generated pages"
    )

    enable_relative_links: bool = Field(
        default=True,
        description="Use relative links between generated pages"
    )

    # Integration hints
    mkdocs_yml_path: Path | None = Field(
        default=None,
        description="Path to existing mkdocs.yml to read configuration from"
    )

    inherit_theme_config: bool = Field(
        default=True,
        description="Inherit theme configuration from main site"
    )

    custom_css_classes: dict[str, str] | None = Field(
        default=None,
        description="Custom CSS classes to apply to elements"
    )

    def generate_frontmatter(self,
                           title: str,
                           description: str | None = None,
                           extra_metadata: dict[str, Any] | None = None) -> str:
        """Generate frontmatter for a page."""
        fm = ["---"]
        fm.append(f"title: {title}")

        if description:
            fm.append(f"description: {description}")

        if self.page_template:
            fm.append(f"template: {self.page_template}")

        if self.page_category:
            fm.append(f"category: {self.page_category}")

        if self.page_tags:
            fm.append(f"tags: {', '.join(self.page_tags)}")

        if self.page_authors:
            fm.append(f"authors: {', '.join(self.page_authors)}")

        if self.nav_position is not None:
            fm.append(f"nav_order: {self.nav_position}")

        if self.include_created_date:
            fm.append(f"created: {datetime.utcnow().isoformat()}")

        if self.include_updated_date:
            fm.append(f"updated: {datetime.utcnow().isoformat()}")

        # Add any extra metadata
        if extra_metadata:
            for key, value in extra_metadata.items():
                if isinstance(value, list):
                    fm.append(f"{key}: {', '.join(str(v) for v in value)}")
                else:
                    fm.append(f"{key}: {value}")

        fm.append("---")
        fm.append("")

        return "\n".join(fm)

    def get_diagram_reference(self, diagram_path: Path, alt_text: str) -> str:
        """Generate markdown for embedding a diagram."""
        rel_path = f"{self.diagrams_dir}/{diagram_path.name}"

        classes = ""
        if self.diagram_classes:
            classes = f"{{: .{' .'.join(self.diagram_classes)} }}"

        # Material for MkDocs supports figure syntax
        if self.use_annotations:
            return f"<figure markdown>\n  ![{alt_text}]({rel_path})\n  <figcaption>{alt_text}</figcaption>\n</figure>"
        else:
            return f"![{alt_text}]({rel_path}){classes}"

    def get_admonition(self,
                      type: str,
                      title: str | None = None,
                      content: str = "") -> str:
        """Generate Material admonition syntax."""
        if not self.use_admonitions:
            return f"**{title or type.upper()}**: {content}"

        if title:
            return f'!!! {type} "{title}"\n    {content}'
        else:
            return f'!!! {type}\n    {content}'

    def get_content_tab(self, tabs: dict[str, str]) -> str:
        """Generate Material content tabs syntax."""
        if not self.use_content_tabs:
            # Fallback to sections
            sections = []
            for tab_name, tab_content in tabs.items():
                sections.append(f"### {tab_name}\n\n{tab_content}")
            return "\n\n".join(sections)

        tab_blocks = []
        for tab_name, tab_content in tabs.items():
            tab_blocks.append(f'=== "{tab_name}"\n\n    {tab_content}')

        return "\n\n".join(tab_blocks)

    def get_output_path(self, filename: str) -> Path:
        """Get the full output path for a file."""
        if self.pages_subdir:
            return self.output_dir / self.pages_subdir / filename
        return self.output_dir / filename

    def create_nav_entry(self, pages: list[str]) -> dict[str, Any]:
        """Create navigation entry for mkdocs.yml."""
        nav_entry = {}

        if self.nav_parent:
            # Nested under parent
            nav_entry[self.nav_parent] = []
            for page in pages:
                page_title = page.replace('.md', '').replace('-', ' ').title()
                if self.nav_title_prefix:
                    page_title = f"{self.nav_title_prefix} {page_title}"

                if self.pages_subdir:
                    nav_entry[self.nav_parent].append({
                        page_title: f"{self.pages_subdir}/{page}"
                    })
                else:
                    nav_entry[self.nav_parent].append({
                        page_title: page
                    })
        else:
            # Top level
            for page in pages:
                page_title = page.replace('.md', '').replace('-', ' ').title()
                if self.nav_title_prefix:
                    page_title = f"{self.nav_title_prefix} {page_title}"

                if self.pages_subdir:
                    nav_entry[page_title] = f"{self.pages_subdir}/{page}"
                else:
                    nav_entry[page_title] = page

        return nav_entry

    def get_code_block_syntax(self, language: str, code: str,
                             title: str | None = None,
                             highlight_lines: list[int] | None = None) -> str:
        """Generate code block with optional enhancements."""
        options = []

        if title:
            options.append(f'title="{title}"')

        if self.code_line_numbers:
            options.append("linenums=\"1\"")

        if highlight_lines:
            options.append(f"hl_lines=\"{' '.join(map(str, highlight_lines))}\"")

        if options:
            return f"```{language} {' '.join(options)}\n{code}\n```"
        else:
            return f"```{language}\n{code}\n```"

    def get_grid_layout(self, items: list[dict[str, str]]) -> str:
        """Generate Material grid layout."""
        if not self.use_grids:
            # Fallback to simple layout
            sections = []
            for item in items:
                sections.append(f"## {item.get('title', 'Section')}\n\n{item.get('content', '')}")
            return "\n\n".join(sections)

        grid_html = '<div class="grid cards" markdown>\n\n'
        for item in items:
            grid_html += f"- **{item.get('title', 'Title')}**\n\n"
            grid_html += f"    {item.get('content', 'Content')}\n\n"
        grid_html += "</div>"

        return grid_html

    def generate_index_page(self, pages: list[str], descriptions: dict[str, str] | None = None) -> str:
        """Generate an index page for the documentation set."""
        content = self.generate_frontmatter(
            title=self.index_title,
            description=self.index_description or f"Generated documentation for {self.index_title.lower()}"
        )

        content += f"# {self.index_title}\n\n"

        if self.index_description:
            content += f"{self.index_description}\n\n"

        content += "## Contents\n\n"

        for page in pages:
            page_name = page.replace('.md', '').replace('-', ' ').title()
            page_link = page if not self.pages_subdir else f"{self.pages_subdir}/{page}"

            description = ""
            if descriptions and page in descriptions:
                description = f" - {descriptions[page]}"

            content += f"- [{page_name}]({page_link}){description}\n"

        return content
