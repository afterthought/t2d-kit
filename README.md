# t2d-kit: Multi-Framework Diagram Pipeline

Transform requirements into beautiful diagrams and documentation using self-organizing AI agents.

[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Claude Code](https://img.shields.io/badge/claude-code-purple)](https://claude.ai/code)

## 🚀 Quick Start

```bash
# Install with uv
uvx install t2d-kit

# Setup agents
t2d setup

# Start MCP server for Claude Desktop
t2d mcp .

# Verify installation
t2d verify
```

## 📖 What is t2d-kit?

t2d-kit is an intelligent documentation generator that transforms Product Requirements Documents (PRDs) into comprehensive diagrams and documentation. Using self-organizing Claude Code agents, it automatically:

- 📊 **Generates Diagrams**: Architecture (C4), sequence, ERD, state, deployment diagrams
- 📝 **Creates Documentation**: Technical docs, API references, user guides
- 🎯 **Builds Presentations**: Professional slides with embedded diagrams
- 🤖 **Self-Organizes**: Agents coordinate autonomously without complex orchestration

## ✨ Features

### 🧠 Intelligent Agent Architecture
- **Transform Agent**: Converts simple recipes to detailed specifications
- **Diagram Generators**: D2, Mermaid, PlantUML agents for different diagram types
- **Content Generators**: Documentation and presentation agents
- **Natural Language**: Just tell Claude what you want

### 📐 Multiple Diagram Frameworks
- **D2**: Modern diagrams with excellent layout algorithms
- **Mermaid**: Web-ready diagrams with broad compatibility
- **PlantUML**: Formal UML diagrams for enterprise use

### 📚 Rich Output Formats
- **MkDocs**: Material-themed documentation sites
- **Marp**: Professional presentations with speaker notes
- **Multiple Formats**: SVG, PNG, PDF exports

## 🛠 Installation

### Prerequisites

```bash
# Install mise for dependency management
curl https://mise.run | sh

# Install Python dependencies
pip install -e .[dev]

# Install diagram tools
mise install
```

### Claude Desktop Integration

Add to your Claude Desktop config:

```json
{
  "mcpServers": {
    "t2d-kit": {
      "command": "t2d",
      "args": ["mcp", "."]
    }
  }
}
```

## 📄 Usage

### 1. Create a Recipe

```yaml
# recipe.yaml
recipe:
  name: "My System"
  prd:
    content: |
      We're building an e-commerce platform that allows users to browse products,
      add them to cart, and complete purchases with multiple payment options...

  instructions:
    diagrams:
      - type: "architecture"
        description: "High-level system architecture"
      - type: "database"
        description: "Entity relationships"

    documentation:
      style: "technical"
      audience: "developers"
```

### 2. Transform and Generate

```bash
# In Claude Desktop
"Transform my recipe.yaml file"
# Agents automatically create recipe.t2d.yaml

"Generate all diagrams and documentation"
# Agents create diagrams, docs, and presentations
```

### 3. View Results

```
output/
├── diagrams/
│   ├── architecture.svg
│   └── database.svg
├── docs/
│   ├── architecture.md
│   └── api.md
└── presentation/
    └── slides.html
```

## 🤝 How It Works

```mermaid
flowchart LR
    User[User] -->|writes| Recipe[recipe.yaml]
    Recipe -->|transform| Transform[Transform Agent]
    Transform -->|creates| Processed[recipe.t2d.yaml]
    Processed -->|triggers| Generators[Generator Agents]
    Generators -->|produce| Assets[Diagrams & Docs]
```

1. **Write Recipe**: Express requirements in simple YAML
2. **Transform**: Agent analyzes PRD and generates specifications
3. **Generate**: Diagram and content agents create assets
4. **Integrate**: Output integrates with existing documentation

## 📁 Project Structure

```
t2d-kit/
├── src/t2d_kit/
│   ├── models/        # Pydantic data models
│   ├── mcp/           # FastMCP server
│   ├── cli/           # CLI commands
│   └── agents/        # Claude Code agents
├── examples/          # Recipe examples
├── docs/              # Documentation
└── tests/             # Test suite
```

## 🧪 Development

```bash
# Run tests
pytest tests/

# Format code
mise run format

# Lint code
mise run lint

# Run with coverage
mise run test-cov
```

## 📚 Documentation

- [Quickstart Guide](docs/quickstart.md)
- [API Documentation](docs/api.md)
- [Agent Usage Guide](docs/agents.md)
- [Examples](examples/)

## 🤖 Agent Commands

Agents self-activate based on context, but you can also invoke them directly:

- `/t2d-transform recipe.yaml` - Transform user recipe
- `Generate D2 diagrams` - Activates D2 generator
- `Create documentation` - Activates docs generator
- `Build presentation` - Activates slides generator

## 🔧 Configuration

### MkDocs Integration

t2d-kit generates pages that integrate with existing MkDocs sites:

```python
mkdocs_config = MkDocsPageConfig(
    output_dir=Path("existing-site/docs"),
    pages_subdir=Path("generated"),
    nav_parent="API Documentation",
    use_admonitions=True,
    use_content_tabs=True
)
```

### Diagram Options

```python
d2_options = D2Options(
    layout_engine="elk",
    theme="cool-classics",
    sketch=True
)
```

## 🚦 Performance

- Recipe validation: < 200ms
- Diagram generation: < 5s per diagram
- Supports 10+ diagrams per recipe
- Parallel processing for efficiency

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) for details.

## 🙏 Acknowledgments

- Built with [Claude Code](https://claude.ai/code)
- Powered by [FastMCP](https://github.com/jlowin/fastmcp)
- Diagrams by [D2](https://d2lang.com), [Mermaid](https://mermaid.js.org), [PlantUML](https://plantuml.com)

---

**Made with ❤️ by the t2d-kit team**