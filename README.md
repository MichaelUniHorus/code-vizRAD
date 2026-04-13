# 🔍 code-viz

> **Understand any codebase in 60 seconds**

[![PyPI version](https://badge.fury.io/py/code-viz.svg)](https://badge.fury.io/py/code-viz)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Interactive visualization of code dependencies. Transform your codebase into an explorable force-directed graph.

![Demo](https://raw.githubusercontent.com/yourusername/code-viz/main/examples/demo.gif)

## ✨ Features

- 🎯 **Instant Insights** — See module dependencies, hot spots, and architecture at a glance
- 🔍 **Smart Search** — Find any module instantly, filter by name or path
- 🎨 **Beautiful Visuals** — Dark theme, color-coded by activity level, sized by code volume
- 💾 **Export** — Save as PNG for documentation and sharing
- 🚀 **Zero Config** — Works out of the box with any Python project

## 📦 Installation

```bash
pip install code-viz
```

Or with [pipx](https://pypa.github.io/pipx/) (recommended):

```bash
pipx install code-viz
```

## 🚀 Quick Start

### Analyze current directory

```bash
code-viz analyze .
```

This opens your browser with an interactive graph.

### Analyze specific project

```bash
code-viz analyze /path/to/your/project
```

### Start live server

```bash
code-viz analyze . --serve
```

Server runs on `http://localhost:8080` with auto-reload support.

### Quick stats without visualization

```bash
code-viz stats .
```

Shows summary and identifies high-coupling modules.

## 🎮 Interactive Controls

| Control | Action |
|---------|--------|
| **Drag** | Move nodes around |
| **Scroll** | Zoom in/out |
| **Click** | Hold and drag background to pan |
| **Hover** | See module details (classes, functions, metrics) |
| **Search** | Filter modules by name |
| **Sliders** | Adjust graph physics (charge, link distance) |

## 📊 Output Example

```
📁 Analyzing: /home/user/my-project
📊 Output: /home/user/my-project/code_viz_output

✅ Analysis complete!

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┓
┃ Metric                          ┃ Value         ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━┩
│ Total Modules                   │ 42            │
│ Total Dependencies              │ 156           │
│ Average Connections             │ 7.4           │
│ Max Connections                 │ 23            │
└─────────────────────────────────┴───────────────┘

🔥 Top Connected Modules:
  1. core.engine (23 connections)
  2. api.routes (18 connections)
  3. models.base (15 connections)

🌐 Opened: /home/user/my-project/code_viz_output/code-viz.html
```

## 🔧 Advanced Usage

### Export JSON for custom processing

```bash
code-viz analyze . --format json
```

### Custom output directory

```bash
code-viz analyze . --output ./docs/graphs
```

### Disable auto-open browser

```bash
code-viz analyze . --no-open
```

### Custom port for server

```bash
code-viz analyze . --serve --port 3000
```

## 🛣️ Roadmap

- [ ] TypeScript/JavaScript support
- [ ] Go modules support
- [ ] Rust crates support
- [ ] VS Code extension
- [ ] GitHub Action for PR visualization
- [ ] Export to SVG/PDF
- [ ] 3D visualization mode
- [ ] Diff view between commits

## 🤝 Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

MIT License — see [LICENSE](LICENSE) file.

---

<p align="center">
Made with ❤️ for developers who love to understand their code
</p>
