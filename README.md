# 🔍 code-viz

> **Understand any codebase in 60 seconds**

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Transform your codebase into an interactive force-directed graph. See dependencies, hotspots, and architecture at a glance.

Perfect for:
- **Onboarding** new team members
- **Legacy code** archaeology
- **Architecture reviews**
- **Refactoring planning**

## ✨ Features

- 🎯 **Instant Insights** — See module dependencies, hotspots, and architecture
- 🔍 **Smart Search** — Find any module instantly, filter by name or path
- 🎨 **Beautiful Visuals** — Dark theme, color-coded by activity, sized by code volume
- 💾 **Export** — Save as PNG for documentation
- 🚀 **Zero Config** — Works out of the box with any Python project

## 📦 Installation

```bash
# Clone the repository
git clone https://github.com/MichaelUniHorus/code-vizRAD.git
cd code-vizRAD

# Install dependencies
pip install -e .
```

## 🚀 Quick Start

```bash
code-viz analyze .
```

Opens your browser with an interactive graph.

### Live server with auto-reload

```bash
code-viz analyze . --serve
```

## 🎮 Interactive Controls

| Control | Action |
|---------|--------|
| **Drag** | Move nodes around |
| **Scroll** | Zoom in/out |
| **Hover** | See module details (classes, functions, metrics) |
| **Search** | Filter modules by name |
| **Export** | Save as PNG |

## 📊 What You'll See

```
📁 Analyzing: /home/user/my-project

✅ Analysis complete!

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┓
┃ Metric                          ┃ Value         ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━┩
│ Total Modules                   │ 42            │
│ Total Dependencies              │ 156           │
│ Average Connections             │ 7.4           │
└─────────────────────────────────┴───────────────┘

🔥 Top Connected Modules:
  1. core.engine (23 connections)
  2. api.routes (18 connections)
  3. models.base (15 connections)
```

## � Use Cases

### Django Projects

See how views connect to models and services:

```bash
code-viz analyze my_django_project
```

```
🔥 Top Connected Modules:
  1. blog.views (4 connections) → blog.models, blog.forms, blog.services
  2. blog.models (3 connections)
  3. blog.services (2 connections)
```

Perfect for understanding MVC patterns and data flow.

### Legacy Codebases

Quickly identify:
- **High coupling** modules (lots of connections)
- **Unused code** (no incoming connections)
- **Core modules** (many incoming connections)

### Architecture Reviews

Validate your design decisions:
- Are modules properly layered?
- Is there circular dependency?
- Which modules need refactoring?

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

## 🛣️ Roadmap

- [ ] TypeScript/JavaScript support
- [ ] Go modules support
- [ ] Rust crates support
- [ ] VS Code extension
- [ ] GitHub Action for PR visualization
- [ ] Export to SVG/PDF
- [ ] 3D visualization mode

## 🤝 Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

MIT License — see [LICENSE](LICENSE) file.

---

<p align="center">
Made with ❤️ for developers who love to understand their code
</p>
