"""Tests for code analyzer."""

from pathlib import Path

from code_viz.analyzer import CodeAnalyzer, ImportVisitor


class TestImportVisitor:
    """Tests for ImportVisitor."""

    def test_visit_import(self) -> None:
        """Test parsing regular imports."""
        import ast

        code = "import os\nimport sys as system"
        tree = ast.parse(code)
        visitor = ImportVisitor()
        visitor.visit(tree)

        assert len(visitor.imports) == 2
        assert visitor.imports[0].name == "os"
        assert visitor.imports[1].name == "sys"  # alias stores original name

    def test_visit_import_from(self) -> None:
        """Test parsing from imports."""
        import ast

        code = "from collections import OrderedDict\nfrom typing import List, Dict"
        tree = ast.parse(code)
        visitor = ImportVisitor()
        visitor.visit(tree)

        assert len(visitor.imports) == 3
        assert visitor.imports[0].name == "OrderedDict"
        assert visitor.imports[0].module == "collections"

    def test_visit_class(self) -> None:
        """Test parsing class definitions."""
        import ast

        code = "class Foo:\n    pass\nclass Bar:\n    pass"
        tree = ast.parse(code)
        visitor = ImportVisitor()
        visitor.visit(tree)

        assert len(visitor.classes) == 2
        assert "Foo" in visitor.classes
        assert "Bar" in visitor.classes

    def test_visit_function(self) -> None:
        """Test parsing function definitions."""
        import ast

        code = "def foo():\n    pass\ndef bar():\n    pass"
        tree = ast.parse(code)
        visitor = ImportVisitor()
        visitor.visit(tree)

        assert len(visitor.functions) == 2
        assert "foo" in visitor.functions
        assert "bar" in visitor.functions


class TestCodeAnalyzer:
    """Tests for CodeAnalyzer."""

    def test_analyze_empty_project(self, tmp_path: Path) -> None:
        """Test analyzing empty project."""
        analyzer = CodeAnalyzer(tmp_path)
        graph = analyzer.analyze()

        assert len(analyzer.modules) == 0
        assert graph.number_of_nodes() == 0

    def test_analyze_single_module(self, tmp_path: Path) -> None:
        """Test analyzing single Python file."""
        (tmp_path / "main.py").write_text("""
import os
from typing import List

def main():
    pass

class MyClass:
    pass
""")

        analyzer = CodeAnalyzer(tmp_path)
        _graph = analyzer.analyze()  # noqa: F841

        assert "main" in analyzer.modules
        module = analyzer.modules["main"]
        assert len(module.imports) == 2
        assert len(module.classes) == 1
        assert len(module.functions) == 1

    def test_resolve_internal_import(self, tmp_path: Path) -> None:
        """Test resolving internal module imports."""
        (tmp_path / "utils.py").write_text("""
def helper():
    pass
""")
        (tmp_path / "main.py").write_text("""
from utils import helper

def main():
    helper()
""")

        analyzer = CodeAnalyzer(tmp_path)
        graph = analyzer.analyze()  # noqa: F841

        assert graph.has_edge("main", "utils")

    def test_get_graph_data(self, tmp_path: Path) -> None:
        """Test exporting graph data."""
        (tmp_path / "mod.py").write_text("x = 1\n")

        analyzer = CodeAnalyzer(tmp_path)
        _graph = analyzer.analyze()  # noqa: F841
        data = analyzer.get_graph_data()

        assert "nodes" in data
        assert "links" in data
        assert "stats" in data
        assert data["stats"]["total_modules"] == 1


class TestEdgeCases:
    """Tests for edge cases."""

    def test_syntax_error_file(self, tmp_path: Path) -> None:
        """Test handling of files with syntax errors."""
        (tmp_path / "broken.py").write_text("def foo(:\n    pass")

        analyzer = CodeAnalyzer(tmp_path)
        _graph = analyzer.analyze()  # noqa: F841

        assert len(analyzer.modules) == 0

    def test_relative_import(self, tmp_path: Path) -> None:
        """Test handling of relative imports."""
        pkg = tmp_path / "pkg"
        pkg.mkdir()
        (pkg / "__init__.py").write_text("")
        (pkg / "sub.py").write_text("x = 1")
        (pkg / "main.py").write_text("from .sub import x")

        analyzer = CodeAnalyzer(tmp_path)
        _graph = analyzer.analyze()  # noqa: F841

        # Should have modules pkg.sub and pkg.main
        assert any("pkg" in m for m in analyzer.modules)
