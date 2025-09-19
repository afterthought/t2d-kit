"""
T014: Integration test for MkDocs documentation generation.
This test will fail initially until the MkDocs integration is implemented.
"""

import tempfile
from pathlib import Path
from unittest.mock import patch

import yaml

from t2d_kit.generators.mkdocs_generator import MkDocsGenerator
from t2d_kit.models.diagram_spec import DiagramSpec


class TestMkDocsIntegration:
    """Integration tests for MkDocs documentation generation."""

    def test_mkdocs_generator_initialization(self):
        """Test that MkDocsGenerator can be initialized."""
        generator = MkDocsGenerator()
        assert generator is not None
        assert hasattr(generator, "generate_docs")
        assert hasattr(generator, "create_mkdocs_config")
        assert hasattr(generator, "add_diagram_to_docs")

    def test_create_mkdocs_config(self):
        """Test creating MkDocs configuration file."""
        generator = MkDocsGenerator()

        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "mkdocs.yml"

            project_config = {
                "site_name": "T2D Kit Documentation",
                "site_description": "Text-to-Diagram Kit Documentation",
                "site_author": "T2D Kit",
                "theme": "material",
                "plugins": ["search", "d2"],
            }

            result_path = generator.create_mkdocs_config(config_path, project_config)

            assert result_path.exists()
            assert result_path.name == "mkdocs.yml"

            # Verify configuration content
            with open(result_path) as f:
                config = yaml.safe_load(f)
                assert config["site_name"] == "T2D Kit Documentation"
                assert config["theme"]["name"] == "material"
                assert "search" in config["plugins"]

    def test_generate_documentation_structure(self):
        """Test generating complete documentation structure."""
        generator = MkDocsGenerator()

        with tempfile.TemporaryDirectory() as temp_dir:
            docs_dir = Path(temp_dir) / "docs"

            project_info = {
                "name": "Test Project",
                "description": "Test documentation generation",
                "version": "1.0.0",
            }

            generator.generate_docs(docs_dir, project_info)

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

        diagram_spec = DiagramSpec(
            d2_content=d2_content,
            title="System Architecture",
            description="Main system components and connections",
        )

        generator = MkDocsGenerator()

        with tempfile.TemporaryDirectory() as temp_dir:
            docs_dir = Path(temp_dir) / "docs"
            docs_dir.mkdir(parents=True)
            diagrams_dir = docs_dir / "diagrams"
            diagrams_dir.mkdir()

            result_files = generator.add_diagram_to_docs(
                diagram_spec, docs_dir, diagram_name="architecture"
            )

            # Verify files were created
            assert len(result_files) >= 2  # At least .d2 and .md files

            d2_file = diagrams_dir / "architecture.d2"
            md_file = diagrams_dir / "architecture.md"

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
            d2_content = f"""
            component_a_{i}: Component A {i}
            component_b_{i}: Component B {i}
            component_a_{i} -> component_b_{i}: connection {i}
            """
            diagram = DiagramSpec(
                d2_content=d2_content,
                title=f"Diagram {i+1}",
                description=f"Test diagram number {i+1}",
            )
            diagrams.append(diagram)

        generator = MkDocsGenerator()

        with tempfile.TemporaryDirectory() as temp_dir:
            docs_dir = Path(temp_dir) / "docs"
            docs_dir.mkdir(parents=True)

            gallery_file = generator.generate_diagram_gallery(diagrams, docs_dir)

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

        generator = MkDocsGenerator()

        with tempfile.TemporaryDirectory() as temp_dir:
            docs_dir = Path(temp_dir) / "docs"
            docs_dir.mkdir(parents=True)

            # Create minimal documentation structure
            (docs_dir / "index.md").write_text("# Test Documentation")

            config_path = Path(temp_dir) / "mkdocs.yml"
            config = {"site_name": "Test Site", "docs_dir": str(docs_dir)}
            with open(config_path, "w") as f:
                yaml.dump(config, f)

            generator.build_site(config_path)

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

        generator = MkDocsGenerator()

        with tempfile.TemporaryDirectory() as temp_dir:
            docs_dir = Path(temp_dir) / "docs"
            docs_dir.mkdir(parents=True)

            api_file = generator.generate_api_documentation(diagrams_data, docs_dir)

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
        generator = MkDocsGenerator()

        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "mkdocs.yml"

            theme_config = {
                "name": "material",
                "palette": {"scheme": "default", "primary": "blue", "accent": "light blue"},
                "features": ["navigation.tabs", "navigation.sections", "toc.integrate"],
            }

            project_config = {"site_name": "Custom Theme Test", "theme": theme_config}

            result_path = generator.create_mkdocs_config(config_path, project_config)

            # Verify theme configuration
            with open(result_path) as f:
                config = yaml.safe_load(f)
                assert config["theme"]["name"] == "material"
                assert config["theme"]["palette"]["primary"] == "blue"
                assert "navigation.tabs" in config["theme"]["features"]

    def test_add_custom_css_and_js(self):
        """Test adding custom CSS and JavaScript to documentation."""
        generator = MkDocsGenerator()

        with tempfile.TemporaryDirectory() as temp_dir:
            docs_dir = Path(temp_dir) / "docs"
            docs_dir.mkdir(parents=True)

            custom_files = {
                "css": ["custom.css", "d2-diagrams.css"],
                "js": ["custom.js", "diagram-interactions.js"],
            }

            generator.add_custom_assets(docs_dir, custom_files)

            # Verify asset directories and files
            assets_dir = docs_dir / "assets"
            assert assets_dir.exists()

            css_dir = assets_dir / "css"
            js_dir = assets_dir / "js"
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

        generator = MkDocsGenerator()

        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "mkdocs.yml"

            # Create minimal config
            config = {"site_name": "Dev Server Test"}
            with open(config_path, "w") as f:
                yaml.dump(config, f)

            generator.serve_dev_server(config_path, port=8001)

            mock_subprocess.assert_called_once()
            args = mock_subprocess.call_args[0][0]
            assert "mkdocs" in args[0]
            assert "serve" in args
            assert "--dev-addr" in args
            assert "127.0.0.1:8001" in args
