"""Code analyzer that builds dependency graph from Python source."""

from __future__ import annotations

import ast
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import networkx as nx


@dataclass
class ImportInfo:
    """Information about an import in a module."""

    name: str
    module: str | None = None
    is_from_import: bool = False
    level: int = 0  # Relative import level
    line: int = 0


@dataclass
class ModuleInfo:
    """Information about a Python module."""

    path: Path
    name: str
    imports: list[ImportInfo] = field(default_factory=list)
    classes: list[str] = field(default_factory=list)
    functions: list[str] = field(default_factory=list)
    line_count: int = 0


class ImportVisitor(ast.NodeVisitor):
    """AST visitor that extracts import information."""

    def __init__(self) -> None:
        self.imports: list[ImportInfo] = []
        self.classes: list[str] = []
        self.functions: list[str] = []

    def visit_Import(self, node: ast.Import) -> None:  # noqa: N802
        for alias in node.names:
            self.imports.append(
                ImportInfo(
                    name=alias.name,
                    module=None,
                    is_from_import=False,
                    level=0,
                    line=node.lineno if hasattr(node, "lineno") else 0,
                )
            )
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:  # noqa: N802
        module = node.module
        level = node.level

        for alias in node.names:
            self.imports.append(
                ImportInfo(
                    name=alias.name,
                    module=module,
                    is_from_import=True,
                    level=level,
                    line=node.lineno if hasattr(node, "lineno") else 0,
                )
            )
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:  # noqa: N802
        self.classes.append(node.name)
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:  # noqa: N802
        # Skip nested functions
        if not isinstance(node.parent, ast.ClassDef) if hasattr(node, "parent") else True:
            self.functions.append(node.name)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:  # noqa: N802
        if not isinstance(node.parent, ast.ClassDef) if hasattr(node, "parent") else True:
            self.functions.append(node.name)
        self.generic_visit(node)


class CodeAnalyzer:
    """Analyzes Python code and builds dependency graph."""

    def __init__(self, root_path: Path | str) -> None:
        self.root_path = Path(root_path).resolve()
        self.modules: dict[str, ModuleInfo] = {}
        self.graph: nx.DiGraph = nx.DiGraph()

    def analyze(self) -> nx.DiGraph:
        """Analyze all Python files in the project and build graph."""
        self._collect_modules()
        self._build_graph()
        return self.graph

    def _collect_modules(self) -> None:
        """Find and parse all Python modules."""
        for py_file in self.root_path.rglob("*.py"):
            # Skip common non-source directories
            if any(part.startswith(".") or part in {"__pycache__", "venv", ".venv", "node_modules"}
                   for part in py_file.parts):
                continue

            try:
                module_info = self._parse_file(py_file)
                if module_info:
                    self.modules[module_info.name] = module_info
            except (SyntaxError, UnicodeDecodeError, PermissionError):
                continue

    def _parse_file(self, path: Path) -> ModuleInfo | None:
        """Parse a single Python file."""
        try:
            with open(path, encoding="utf-8") as f:
                content = f.read()
        except UnicodeDecodeError:
            return None

        try:
            tree = ast.parse(content)
        except SyntaxError:
            return None

        # Calculate module name relative to root
        relative_path = path.relative_to(self.root_path)
        module_name = str(relative_path.with_suffix("")).replace(os.sep, ".")

        # Remove leading dot if path starts with .
        if module_name.startswith("."):
            module_name = module_name[1:]

        visitor = ImportVisitor()
        visitor.visit(tree)

        line_count = len(content.splitlines())

        return ModuleInfo(
            path=path,
            name=module_name,
            imports=visitor.imports,
            classes=visitor.classes,
            functions=visitor.functions,
            line_count=line_count,
        )

    def _build_graph(self) -> None:
        """Build NetworkX graph from module information."""
        # Add all modules as nodes
        for module_name, info in self.modules.items():
            self.graph.add_node(
                module_name,
                path=str(info.path.relative_to(self.root_path)),
                classes=info.classes,
                functions=info.functions,
                line_count=info.line_count,
                type="internal",
            )

        # Add edges based on imports
        for module_name, info in self.modules.items():
            for imp in info.imports:
                target = self._resolve_import(module_name, imp)
                if target:
                    if not self.graph.has_edge(module_name, target):
                        self.graph.add_edge(
                            module_name,
                            target,
                            weight=1,
                            imports=[imp.name],
                        )
                    else:
                        # Accumulate imports on existing edge
                        self.graph[module_name][target]["weight"] += 1
                        self.graph[module_name][target]["imports"].append(imp.name)

    def _resolve_import(self, source_module: str, imp: ImportInfo) -> str | None:
        """Resolve an import to a module name in the project."""
        if imp.is_from_import:
            if imp.level > 0:
                # Relative import
                parts = source_module.split(".")
                base = ".".join(parts[:-imp.level]) if imp.level < len(parts) else ""

                target = (f"{base}.{imp.module}" if base else imp.module) if imp.module else base
            else:
                # Absolute import
                target = imp.module or imp.name

            # Check if target exists in our modules
            if target in self.modules:
                return target

            # Try with the imported name as submodule
            full_target = f"{target}.{imp.name}" if target else imp.name
            if full_target in self.modules:
                return full_target

        else:
            # Regular import: check if it's in our project
            if imp.name in self.modules:
                return imp.name

            # Check if it's a subpackage
            for mod_name in self.modules:
                if mod_name.startswith(f"{imp.name}."):
                    return imp.name

        return None

    def get_graph_data(self) -> dict[str, Any]:
        """Export graph data for visualization."""
        nodes = []
        for node, data in self.graph.nodes(data=True):
            degree = self.graph.degree(node)
            in_degree = self.graph.in_degree(node)
            out_degree = self.graph.out_degree(node)

            nodes.append({
                "id": node,
                "path": data.get("path", ""),
                "type": data.get("type", "internal"),
                "classes": data.get("classes", []),
                "functions": data.get("functions", []),
                "line_count": data.get("line_count", 0),
                "degree": degree,
                "in_degree": in_degree,
                "out_degree": out_degree,
                "radius": min(5 + degree * 2, 30),  # For visualization
            })

        links = []
        for source, target, data in self.graph.edges(data=True):
            links.append({
                "source": source,
                "target": target,
                "weight": data.get("weight", 1),
                "imports": data.get("imports", []),
            })

        # Calculate some stats
        stats = {
            "total_modules": len(nodes),
            "total_dependencies": len(links),
            "avg_degree": sum(n["degree"] for n in nodes) / max(len(nodes), 1),
            "max_degree": max((n["degree"] for n in nodes), default=0),
        }

        return {
            "nodes": nodes,
            "links": links,
            "stats": stats,
            "root_path": str(self.root_path),
        }
