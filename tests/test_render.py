"""Tests for render module."""

from pathlib import Path

from code_viz.render import GraphRenderer


class TestGraphRenderer:
    """Tests for GraphRenderer."""

    def test_render_creates_file(self, tmp_path: Path) -> None:
        """Test that render creates HTML file."""
        renderer = GraphRenderer(tmp_path)

        data = {
            "nodes": [
                {"id": "main", "path": "main.py", "type": "internal",
                 "classes": [], "functions": ["main"], "line_count": 10,
                 "degree": 1, "in_degree": 0, "out_degree": 1},
                {"id": "utils", "path": "utils.py", "type": "internal",
                 "classes": [], "functions": ["helper"], "line_count": 5,
                 "degree": 1, "in_degree": 1, "out_degree": 0},
            ],
            "links": [
                {"source": "main", "target": "utils", "weight": 1, "imports": ["helper"]},
            ],
            "stats": {
                "total_modules": 2,
                "total_dependencies": 1,
                "avg_degree": 1.0,
                "max_degree": 1,
            },
            "root_path": str(tmp_path),
        }

        output = renderer.render(data, "test.html", auto_open=False)

        assert output.exists()
        content = output.read_text()
        assert "code-viz" in content
        assert "d3" in content.lower()

    def test_output_dir_created(self, tmp_path: Path) -> None:
        """Test that output directory is created if needed."""
        output_dir = tmp_path / "output" / "nested"
        _renderer = GraphRenderer(output_dir)  # noqa: F841

        assert output_dir.exists()
