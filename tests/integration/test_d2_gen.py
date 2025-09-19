"""
T013: Integration test for D2 diagram generation.
This test will fail initially until the D2 generation functionality is implemented.
"""
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from t2d_kit.generators.d2_generator import D2Generator
from t2d_kit.models.diagram_spec import DiagramSpec


class TestD2GenerationIntegration:
    """Integration tests for D2 diagram generation."""

    def test_d2_generator_initialization(self):
        """Test that D2Generator can be initialized."""
        generator = D2Generator()
        assert generator is not None
        assert hasattr(generator, 'generate')
        assert hasattr(generator, 'generate_svg')
        assert hasattr(generator, 'generate_png')

    def test_generate_d2_file(self):
        """Test generating D2 file from DiagramSpec."""
        d2_content = """
        user: User {
          shape: person
        }
        system: System {
          shape: rectangle
        }
        database: Database {
          shape: cylinder
        }

        user -> system: uses
        system -> database: queries
        """

        diagram_spec = DiagramSpec(
            d2_content=d2_content,
            title="System Architecture",
            description="Basic system diagram"
        )

        generator = D2Generator()

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "test_diagram.d2"
            result_path = generator.generate(diagram_spec, output_path)

            assert result_path.exists()
            assert result_path.suffix == ".d2"

            # Verify content was written correctly
            with open(result_path) as f:
                content = f.read()
                assert "user: User" in content
                assert "system: System" in content
                assert "database: Database" in content
                assert "user -> system" in content

    @patch('subprocess.run')
    def test_generate_svg_output(self, mock_subprocess):
        """Test generating SVG output from D2 file."""
        mock_subprocess.return_value.returncode = 0
        mock_subprocess.return_value.stdout = b"SVG generation successful"

        d2_content = "a -> b: connection"
        diagram_spec = DiagramSpec(
            d2_content=d2_content,
            title="Simple Diagram"
        )

        generator = D2Generator()

        with tempfile.TemporaryDirectory() as temp_dir:
            d2_path = Path(temp_dir) / "diagram.d2"
            svg_path = Path(temp_dir) / "diagram.svg"

            # Generate D2 file first
            generator.generate(diagram_spec, d2_path)

            # Generate SVG
            result_path = generator.generate_svg(d2_path, svg_path)

            mock_subprocess.assert_called_once()
            args = mock_subprocess.call_args[0][0]
            assert "d2" in args[0]  # d2 command
            assert str(d2_path) in args
            assert str(svg_path) in args

    @patch('subprocess.run')
    def test_generate_png_output(self, mock_subprocess):
        """Test generating PNG output from D2 file."""
        mock_subprocess.return_value.returncode = 0
        mock_subprocess.return_value.stdout = b"PNG generation successful"

        d2_content = "frontend -> backend: API calls"
        diagram_spec = DiagramSpec(
            d2_content=d2_content,
            title="Frontend Backend Diagram"
        )

        generator = D2Generator()

        with tempfile.TemporaryDirectory() as temp_dir:
            d2_path = Path(temp_dir) / "diagram.d2"
            png_path = Path(temp_dir) / "diagram.png"

            # Generate D2 file first
            generator.generate(diagram_spec, d2_path)

            # Generate PNG
            result_path = generator.generate_png(d2_path, png_path)

            mock_subprocess.assert_called_once()
            args = mock_subprocess.call_args[0][0]
            assert "d2" in args[0]  # d2 command
            assert str(d2_path) in args
            assert str(png_path) in args

    def test_generate_with_layout_options(self):
        """Test D2 generation with layout options."""
        d2_content = """
        a -> b -> c -> d
        """

        diagram_spec = DiagramSpec(
            d2_content=d2_content,
            title="Layout Test Diagram"
        )

        generator = D2Generator()

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "layout_test.d2"

            layout_options = {
                "layout": "elk",
                "theme": "dark",
                "sketch": True
            }

            result_path = generator.generate(
                diagram_spec,
                output_path,
                layout_options=layout_options
            )

            assert result_path.exists()

            # Verify layout options were applied
            with open(result_path) as f:
                content = f.read()
                # Layout options might be added as comments or directives
                assert "a -> b -> c -> d" in content

    @patch('subprocess.run')
    def test_d2_command_error_handling(self, mock_subprocess):
        """Test error handling when D2 command fails."""
        mock_subprocess.return_value.returncode = 1
        mock_subprocess.return_value.stderr = b"D2 syntax error"

        d2_content = "invalid -> -> syntax"  # Invalid D2 syntax
        diagram_spec = DiagramSpec(
            d2_content=d2_content,
            title="Invalid Diagram"
        )

        generator = D2Generator()

        with tempfile.TemporaryDirectory() as temp_dir:
            d2_path = Path(temp_dir) / "invalid.d2"
            svg_path = Path(temp_dir) / "invalid.svg"

            # Generate D2 file
            generator.generate(diagram_spec, d2_path)

            # Attempt to generate SVG (should handle error)
            with pytest.raises(RuntimeError, match="D2 generation failed"):
                generator.generate_svg(d2_path, svg_path)

    def test_generate_with_custom_styling(self):
        """Test D2 generation with custom styling."""
        d2_content = """
        frontend: Frontend App
        backend: Backend API
        database: Database

        frontend -> backend
        backend -> database
        """

        diagram_spec = DiagramSpec(
            d2_content=d2_content,
            title="Styled Diagram"
        )

        generator = D2Generator()

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "styled_diagram.d2"

            styling_options = {
                "frontend.style.fill": "lightblue",
                "backend.style.fill": "lightgreen",
                "database.style.fill": "orange",
                "database.shape": "cylinder"
            }

            result_path = generator.generate(
                diagram_spec,
                output_path,
                styling_options=styling_options
            )

            assert result_path.exists()

            with open(result_path) as f:
                content = f.read()
                assert "frontend" in content
                assert "backend" in content
                assert "database" in content

    def test_batch_generation(self):
        """Test generating multiple diagrams in batch."""
        diagrams = []
        for i in range(3):
            d2_content = f"component_{i}_a -> component_{i}_b: connection_{i}"
            diagram = DiagramSpec(
                d2_content=d2_content,
                title=f"Batch Diagram {i+1}"
            )
            diagrams.append(diagram)

        generator = D2Generator()

        with tempfile.TemporaryDirectory() as temp_dir:
            output_paths = []
            for i, diagram in enumerate(diagrams):
                output_path = Path(temp_dir) / f"batch_diagram_{i+1}.d2"
                result_path = generator.generate(diagram, output_path)
                output_paths.append(result_path)

            # Verify all files were generated
            assert len(output_paths) == 3
            for path in output_paths:
                assert path.exists()
                assert path.suffix == ".d2"

    def test_d2_validation_before_generation(self):
        """Test that D2 content is validated before generation."""
        # Valid D2 content
        valid_d2 = "a -> b: valid connection"
        valid_spec = DiagramSpec(
            d2_content=valid_d2,
            title="Valid Diagram"
        )

        # Invalid D2 content
        invalid_d2 = "a -> -> b: invalid syntax"
        invalid_spec = DiagramSpec(
            d2_content=invalid_d2,
            title="Invalid Diagram"
        )

        generator = D2Generator(validate_before_generation=True)

        with tempfile.TemporaryDirectory() as temp_dir:
            # Valid generation should work
            valid_path = Path(temp_dir) / "valid.d2"
            result = generator.generate(valid_spec, valid_path)
            assert result.exists()

            # Invalid generation should raise error
            invalid_path = Path(temp_dir) / "invalid.d2"
            with pytest.raises(ValueError, match="Invalid D2 syntax"):
                generator.generate(invalid_spec, invalid_path)

    @patch('subprocess.run')
    def test_output_format_options(self, mock_subprocess):
        """Test different output format options."""
        mock_subprocess.return_value.returncode = 0

        d2_content = "service -> database"
        diagram_spec = DiagramSpec(
            d2_content=d2_content,
            title="Format Test"
        )

        generator = D2Generator()

        with tempfile.TemporaryDirectory() as temp_dir:
            d2_path = Path(temp_dir) / "format_test.d2"
            generator.generate(diagram_spec, d2_path)

            # Test different formats
            formats = ['svg', 'png', 'pdf']
            for fmt in formats:
                output_path = Path(temp_dir) / f"diagram.{fmt}"
                method = getattr(generator, f'generate_{fmt}')
                method(d2_path, output_path)

                # Verify D2 command was called with correct format
                mock_subprocess.assert_called()
                args = mock_subprocess.call_args[0][0]
                assert str(output_path) in args
