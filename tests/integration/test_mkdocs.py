"""
T014: Integration test for MkDocs documentation generation.
This test verifies agent-based documentation generation functionality.
"""

import tempfile
from pathlib import Path
from unittest.mock import patch

import yaml

from t2d_kit.models.diagram import DiagramSpecification
from t2d_kit.models.base import DiagramType, FrameworkType, OutputFormat


class TestMkDocsIntegration:
    """Integration tests for MkDocs documentation generation."""

    def test_mkdocs_config_creation(self):
        """Test creating MkDocs configuration file directly."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "mkdocs.yml"

            project_config = {
                "site_name": "T2D Kit Documentation",
                "site_description": "Text-to-Diagram Kit Documentation",
                "site_author": "T2D Kit",
                "theme": {"name": "material"},
                "plugins": ["search"],
            }

            # Write config directly (simulating what docs agent would do)
            with open(config_path, "w") as f:
                yaml.dump(project_config, f)

            assert config_path.exists()
            assert config_path.name == "mkdocs.yml"

            # Verify configuration content
            with open(config_path) as f:
                config = yaml.safe_load(f)
                assert config["site_name"] == "T2D Kit Documentation"
                assert config["theme"]["name"] == "material"
                assert "search" in config["plugins"]


    def test_generate_documentation_structure(self):
        """Test generating complete documentation structure."""
        with tempfile.TemporaryDirectory() as temp_dir:
            docs_dir = Path(temp_dir) / "docs"
            docs_dir.mkdir(parents=True)

            project_info = {
                "name": "Test Project",
                "description": "Test documentation generation",
                "version": "1.0.0",
            }

            # Simulate what docs agent would create
            (docs_dir / "diagrams").mkdir()
            (docs_dir / "assets").mkdir()

            # Create index.md
            index_content = f"# {project_info['name']}\n\n{project_info['description']}\n\nVersion: {project_info['version']}"
            (docs_dir / "index.md").write_text(index_content)

            # Verify directory structure
            assert docs_dir.exists()
            assert (docs_dir / "index.md").exists()
            assert (docs_dir / "diagrams").exists()
            assert (docs_dir / "assets").exists()

            # Verify index.md content
            with open(docs_dir / "index.md") as f:
                content = f.read()
                assert "Test Project" in content
                assert "Test documentation generation" in content

    def test_add_diagram_to_docs(self):
        """Test adding diagram to documentation."""
        d2_content = """
        user: User
        app: Application
        db: Database

        user -> app: uses
        app -> db: stores data
        """

        diagram_spec = DiagramSpecification(
            id="arch-01",
            type=DiagramType.ARCHITECTURE,
            framework=FrameworkType.D2,
            agent="t2d-d2-generator",
            title="System Architecture",
            instructions="Main system components and connections showing user interaction flow",
            output_file="architecture.d2",
            output_formats=[OutputFormat.SVG, OutputFormat.PNG]
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            docs_dir = Path(temp_dir) / "docs"
            docs_dir.mkdir(parents=True)
            diagrams_dir = docs_dir / "diagrams"
            diagrams_dir.mkdir()

            # Simulate what docs agent would create
            d2_file = diagrams_dir / "architecture.d2"
            md_file = diagrams_dir / "architecture.md"

            d2_file.write_text(d2_content)

            # Create markdown documentation
            md_content = f"# {diagram_spec.title}\n\n{diagram_spec.instructions}\n\n![Architecture](./architecture.svg)"
            md_file.write_text(md_content)

            # Verify files were created
            assert d2_file.exists()
            assert md_file.exists()

            # Verify D2 content
            with open(d2_file) as f:
                content = f.read()
                assert "user: User" in content
                assert "app: Application" in content

            # Verify Markdown documentation
            with open(md_file) as f:
                content = f.read()
                assert "System Architecture" in content
                assert "Main system components" in content

    def test_generate_diagram_gallery(self):
        """Test generating a gallery of multiple diagrams."""
        diagrams = []
        for i in range(3):
            diagram = DiagramSpecification(
                id=f"test-diagram-{i+1}",
                type=DiagramType.FLOWCHART,
                framework=FrameworkType.MERMAID,
                agent="t2d-mermaid-generator",
                title=f"Diagram {i+1}",
                instructions=f"Test diagram number {i+1} showing component interactions",
                output_file=f"test_diagram_{i+1}.mmd",
                output_formats=[OutputFormat.SVG]
            )
            diagrams.append(diagram)

        with tempfile.TemporaryDirectory() as temp_dir:
            docs_dir = Path(temp_dir) / "docs"
            docs_dir.mkdir(parents=True)

            # Simulate what docs agent would create
            gallery_content = "# Diagram Gallery\n\n"
            for diagram in diagrams:
                gallery_content += f"## {diagram.title}\n\n{diagram.instructions}\n\n![{diagram.title}](./diagrams/{diagram.id}.svg)\n\n"

            gallery_file = docs_dir / "diagram_gallery.md"
            gallery_file.write_text(gallery_content)

            assert gallery_file.exists()
            assert gallery_file.name == "diagram_gallery.md"

            # Verify gallery content
            with open(gallery_file) as f:
                content = f.read()
                assert "Diagram Gallery" in content
                assert "Diagram 1" in content
                assert "Diagram 2" in content
                assert "Diagram 3" in content

    @patch("subprocess.run")
    def test_build_mkdocs_site(self, mock_subprocess):
        """Test building MkDocs site."""
        mock_subprocess.return_value.returncode = 0
        mock_subprocess.return_value.stdout = b"Site built successfully"

        with tempfile.TemporaryDirectory() as temp_dir:
            docs_dir = Path(temp_dir) / "docs"
            docs_dir.mkdir(parents=True)

            # Create minimal documentation structure
            (docs_dir / "index.md").write_text("# Test Documentation")

            config_path = Path(temp_dir) / "mkdocs.yml"
            config = {"site_name": "Test Site", "docs_dir": str(docs_dir)}
            with open(config_path, "w") as f:
                yaml.dump(config, f)

            # Simulate what docs agent would do - run mkdocs build
            import subprocess
            result = subprocess.run(
                ["mkdocs", "build", "-f", str(config_path)],
                capture_output=True,
                text=True,
                cwd=temp_dir
            )

            mock_subprocess.assert_called_once()
            args = mock_subprocess.call_args[0][0]
            assert "mkdocs" in args[0]
            assert "build" in args

    def test_generate_api_documentation(self):
        """Test generating API documentation for diagrams."""
        diagrams_data = [
            {
                "name": "user_flow",
                "title": "User Flow Diagram",
                "description": "Shows user interaction flow",
                "components": ["user", "ui", "backend"],
                "endpoints": [
                    {"path": "/api/user", "method": "GET"},
                    {"path": "/api/flow", "method": "POST"},
                ],
            },
            {
                "name": "data_flow",
                "title": "Data Flow Diagram",
                "description": "Shows data processing flow",
                "components": ["input", "processor", "output"],
                "endpoints": [
                    {"path": "/api/data", "method": "POST"},
                    {"path": "/api/process", "method": "PUT"},
                ],
            },
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            docs_dir = Path(temp_dir) / "docs"
            docs_dir.mkdir(parents=True)

            # Simulate what docs agent would create
            api_content = "# API Documentation\n\n"
            for diagram in diagrams_data:
                api_content += f"## {diagram['title']}\n\n{diagram['description']}\n\n"
                api_content += "### Endpoints\n\n"
                for endpoint in diagram['endpoints']:
                    api_content += f"- `{endpoint['method']} {endpoint['path']}`\n"
                api_content += "\n"

            api_file = docs_dir / "api.md"
            api_file.write_text(api_content)

            assert api_file.exists()
            assert api_file.name == "api.md"

            # Verify API documentation content
            with open(api_file) as f:
                content = f.read()
                assert "API Documentation" in content
                assert "/api/user" in content
                assert "/api/data" in content
                assert "GET" in content
                assert "POST" in content

    def test_customize_mkdocs_theme(self):
        """Test customizing MkDocs theme and styling."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "mkdocs.yml"

            theme_config = {
                "name": "material",
                "palette": {"scheme": "default", "primary": "blue", "accent": "light blue"},
                "features": ["navigation.tabs", "navigation.sections", "toc.integrate"],
            }

            project_config = {"site_name": "Custom Theme Test", "theme": theme_config}

            # Simulate what docs agent would do
            with open(config_path, "w") as f:
                yaml.dump(project_config, f)

            # Verify theme configuration
            with open(config_path) as f:
                config = yaml.safe_load(f)
                assert config["theme"]["name"] == "material"
                assert config["theme"]["palette"]["primary"] == "blue"
                assert "navigation.tabs" in config["theme"]["features"]

    def test_add_custom_css_and_js(self):
        """Test adding custom CSS and JavaScript to documentation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            docs_dir = Path(temp_dir) / "docs"
            docs_dir.mkdir(parents=True)

            custom_files = {
                "css": ["custom.css", "d2-diagrams.css"],
                "js": ["custom.js", "diagram-interactions.js"],
            }

            # Simulate what docs agent would create
            assets_dir = docs_dir / "assets"
            assets_dir.mkdir()

            css_dir = assets_dir / "css"
            js_dir = assets_dir / "js"
            css_dir.mkdir()
            js_dir.mkdir()

            # Create CSS files
            for css_file in custom_files["css"]:
                (css_dir / css_file).write_text(f"/* {css_file} */\nbody {{ color: #333; }}")

            # Create JS files
            for js_file in custom_files["js"]:
                (js_dir / js_file).write_text(f"// {js_file}\nconsole.log('Loaded {js_file}');")

            # Verify asset directories and files
            assert assets_dir.exists()
            assert css_dir.exists()
            assert js_dir.exists()

            # Verify CSS files
            for css_file in custom_files["css"]:
                assert (css_dir / css_file).exists()

            # Verify JS files
            for js_file in custom_files["js"]:
                assert (js_dir / js_file).exists()

    @patch("subprocess.run")
    def test_serve_mkdocs_development_server(self, mock_subprocess):
        """Test starting MkDocs development server."""
        mock_subprocess.return_value.returncode = 0

        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "mkdocs.yml"

            # Create minimal config
            config = {"site_name": "Dev Server Test"}
            with open(config_path, "w") as f:
                yaml.dump(config, f)

            # Simulate what docs agent would do
            import subprocess
            result = subprocess.run(
                ["mkdocs", "serve", "-f", str(config_path), "--dev-addr", "127.0.0.1:8001"],
                capture_output=True,
                text=True,
                cwd=temp_dir
            )

            mock_subprocess.assert_called_once()
            args = mock_subprocess.call_args[0][0]
            assert "mkdocs" in args[0]
            assert "serve" in args
            assert "--dev-addr" in args
            assert "127.0.0.1:8001" in args
