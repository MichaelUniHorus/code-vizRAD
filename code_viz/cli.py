"""CLI interface for code-viz."""

from __future__ import annotations

import sys
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.text import Text

from code_viz.analyzer import CodeAnalyzer
from code_viz.render import GraphRenderer

console = Console()


def print_banner() -> None:
    """Print welcome banner."""
    banner = """
    ╔═══════════════════════════════════════╗
    ║         🔍 CODE-VIZ v0.1.0            ║
    ║   Interactive code dependency graph     ║
    ╚═══════════════════════════════════════╝
    """
    console.print(Text(banner, style="bold cyan"))


@click.group()
@click.version_option(version="0.1.0", prog_name="code-viz")
def main() -> None:
    """code-viz: Visualize your code dependencies interactively."""
    print_banner()


@main.command()
@click.argument("path", type=click.Path(exists=True, path_type=Path), default=Path("."))
@click.option(
    "--output",
    "-o",
    type=click.Path(path_type=Path),
    help="Output directory for HTML file",
)
@click.option(
    "--serve",
    "-s",
    is_flag=True,
    help="Start HTTP server for live view",
)
@click.option(
    "--port",
    "-p",
    default=8080,
    help="Port for HTTP server (default: 8080)",
)
@click.option(
    "--no-open",
    is_flag=True,
    help="Don't open browser automatically",
)
@click.option(
    "--format",
    "-f",
    type=click.Choice(["html", "json"]),
    default="html",
    help="Output format",
)
@click.option(
    "--3d",
    is_flag=True,
    help="Use 3D visualization mode",
)
def analyze(
    path: Path,
    output: Path | None,
    serve: bool,
    port: int,
    no_open: bool,
    format: str,
    _3d: bool,
) -> None:
    """Analyze code dependencies and generate visualization."""
    target_path = path.resolve()
    output_dir = output or target_path / "code_viz_output"

    console.print(f"\n[bold blue]📁 Analyzing:[/] {target_path}")
    console.print(f"[bold blue]📊 Output:[/] {output_dir}\n")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        # Phase 1: Parse
        task1 = progress.add_task("[cyan]Parsing source files...", total=None)
        analyzer = CodeAnalyzer(target_path)

        try:
            _graph = analyzer.analyze()  # noqa: F841
        except Exception as e:
            console.print(f"\n[bold red]❌ Error analyzing code:[/] {e}")
            sys.exit(1)

        progress.update(task1, completed=True)

        # Phase 2: Build data
        task2 = progress.add_task("[cyan]Building graph data...", total=None)
        data = analyzer.get_graph_data()
        progress.update(task2, completed=True)

    # Print stats
    stats = data["stats"]
    console.print("\n[bold green]✅ Analysis complete![/]\n")

    table = Table(title="📈 Project Statistics", show_header=False)
    table.add_column("Metric", style="cyan", width=25)
    table.add_column("Value", style="magenta", width=15)

    table.add_row("Total Modules", str(stats["total_modules"]))
    table.add_row("Total Dependencies", str(stats["total_dependencies"]))
    table.add_row("Average Connections", f"{stats['avg_degree']:.1f}")
    table.add_row("Max Connections", str(stats["max_degree"]))

    console.print(table)

    # Find hot modules
    hot_modules = sorted(
        data["nodes"],
        key=lambda x: x["degree"],
        reverse=True,
    )[:5]

    if hot_modules:
        console.print("\n[bold yellow]🔥 Top Connected Modules:[/]")
        for i, mod in enumerate(hot_modules, 1):
            console.print(f"  {i}. [cyan]{mod['id']}[/] ({mod['degree']} connections)")

    # Output
    if format == "json":
        import json

        output_file = output_dir / "code-viz.json"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
        console.print(f"\n[bold green]💾 Saved to:[/] {output_file}")

    else:  # html
        renderer = GraphRenderer(output_dir)
        mode = "3d" if _3d else "2d"

        if serve:
            console.print(f"\n[bold green]🚀 Starting server at http://localhost:{port}[/]")
            renderer.serve(data, port=port, auto_open=not no_open)
            console.print("[dim]Press Ctrl+C to stop[/]")
            try:
                while True:
                    pass
            except KeyboardInterrupt:
                console.print("\n[bold yellow]👋 Server stopped[/]")
        else:
            output_file = renderer.render(data, auto_open=not no_open, mode=mode)
            console.print(f"\n[bold green]🌐 Opened:[/] {output_file}")


@main.command()
@click.argument("path", type=click.Path(exists=True, path_type=Path), default=Path("."))
def stats(path: Path) -> None:
    """Show quick statistics without generating visualization."""
    target_path = path.resolve()
    console.print(f"\n[bold blue]📁 Analyzing:[/] {target_path}\n")

    analyzer = CodeAnalyzer(target_path)
    _graph = analyzer.analyze()  # noqa: F841
    data = analyzer.get_graph_data()

    stats = data["stats"]

    # Summary panel
    summary = f"""
[bold]Modules:[/] {stats['total_modules']}
[bold]Dependencies:[/] {stats['total_dependencies']}
[bold]Avg Degree:[/] {stats['avg_degree']:.1f}
[bold]Max Degree:[/] {stats['max_degree']}
    """

    console.print(Panel(summary, title="📊 Summary", border_style="cyan"))

    # Show modules with warnings (high coupling)
    high_coupling = [n for n in data["nodes"] if n["degree"] > stats["avg_degree"] * 2]
    if high_coupling:
        console.print("\n[bold yellow]⚠️  High Coupling Detected:[/]")
        for mod in high_coupling[:10]:
            console.print(f"  • [cyan]{mod['id']}[/] - {mod['degree']} connections")


@main.command()
def init() -> None:
    """Initialize configuration file."""
    config_path = Path(".codevizrc")

    if config_path.exists():
        console.print("[bold yellow]⚠️  .codevizrc already exists[/]")
        return

    config_content = """# code-viz configuration
# https://github.com/yourusername/code-viz

[exclude]
patterns = [
    "**/tests/**",
    "**/__pycache__/**",
    "**/venv/**",
    "**/.venv/**",
    "**/node_modules/**",
    "**/.git/**",
    "**/migrations/**",
]

[graph]
max_nodes = 200
min_node_size = 3
max_node_size = 30
"""

    config_path.write_text(config_content, encoding="utf-8")
    console.print(f"[bold green]✅ Created:[/] {config_path}")


if __name__ == "__main__":
    main()
