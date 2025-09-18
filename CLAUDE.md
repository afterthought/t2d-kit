# Claude Code Assistant Context

**Project**: t2d-kit - Multi-Framework Diagram Pipeline
**Type**: CLI Tool with Python Library Core
**Current Branch**: 001-i-want-to

## Quick Summary
t2d-kit is a command-line tool that processes YAML recipes to generate documentation and presentations with auto-routed diagrams. The system uses self-sufficient Claude Code agents that complete their entire lifecycle independently - NO ORCHESTRATOR NEEDED. Each agent handles its complete workflow: generator agents create source AND build assets, content agents create markdown AND build final outputs. The only Python code is a minimal CLI wrapper and FastMCP server. Agents coordinate through files and natural Claude delegation via "use proactively" descriptions.

## Tech Stack
- **Minimal Python**: CLI wrapper + FastMCP server
- **Core Engine**: Self-sufficient Claude Code agents (no orchestrator)
- **MCP Server**: FastMCP for YAML validation and manipulation
- **Diagram CLIs**: D2, Mermaid CLI (mmdc), PlantUML
- **Documentation**: MkDocs with native Mermaid support
- **Presentations**: Marp (not MarpKit) for slide generation
- **Distribution**: uvx with src layout
- **Package Structure**: Modern src/ layout with importlib.resources

## Key Commands
```bash
# Install
uvx install t2d-kit

# Setup Claude agents
t2d setup

# Start MCP server
t2d mcp .

# Create starter recipe (optional)
t2d setup --init

# Transform recipe (in Claude)
"Transform recipe.yaml"

# Process recipe (in Claude)
"Process recipe and generate all outputs"

## Project Structure
```
t2d-kit/
├── cli/
│   └── main.py          # Minimal CLI wrapper (env setup, invoke agents)
├── mcp/                 # MCP server for recipe file management
│   ├── server.py        # Read/write/validate user recipes
│   ├── models.py        # Pydantic models for validation
│   └── config.json      # MCP server configuration
├── agents/              # Self-sufficient Claude Code agents
│   ├── t2d-transform.md        # Recipe transformer (complete lifecycle)
│   ├── t2d-d2-generator.md     # D2: source → build → report
│   ├── t2d-mermaid-generator.md # Mermaid: source → build → report
│   ├── t2d-plantuml-generator.md # PlantUML: source → build → report
│   ├── t2d-docs-generator.md   # Docs: markdown → MkDocs → report
│   └── t2d-slides-generator.md # Slides: markdown → Marp → report
│   ├── t2d-orchestrate.md      # Process recipe.t2d.yaml (routing + coordination)
│   ├── t2d-d2-generator.md     # D2 diagram generator
│   ├── t2d-mermaid-generator.md # Mermaid diagram generator
│   ├── t2d-plantuml-generator.md # PlantUML diagram generator
│   ├── t2d-markdown-maintainer.md # General markdown content
│   ├── t2d-mkdocs-formatter.md # MkDocs-specific formatting
│   └── t2d-marp-slides.md      # Marp presentation slides
├── commands/            # Slash commands for Claude Desktop
│   ├── t2d-transform    # /t2d-transform command script
│   └── t2d-create       # /t2d-create command script
└── examples/            # Example recipes
    ├── recipe.yaml      # User recipe example
    └── recipe.t2d.yaml  # Processed recipe example

tests/
├── contract/
├── integration/
└── unit/
```

## Key Features
1. **Claude Orchestration**: Claude Code coordinates the entire workflow
2. **Minimal Python**: Only CLI wrapper and MCP server
3. **Claude Code Subagents**: Intelligent agents for all processing
4. **Two-File Recipe System**: User recipe.yaml → Agent-generated recipe.t2d.yaml
5. **Dual-mode Operation**: MCP for recipe editing, Desktop Commander for processing
6. **Consistent Architecture**: Both MkDocs and MarpKit reference the same markdown files
7. **Multi-format output**: SVG, PNG, inline markdown, collapsible source
8. **Dual output**: Generate both documentation (MkDocs) and presentations (MarpKit)
9. **Extensible**: Modify orchestration and agents via prompts, not code

## Recipe Format
```yaml
recipe:
  name: "Architecture"

  # Markdown files maintained by subagents
  content_files:
    - id: overview
      path: content/overview.md
      agent: markdown
    - id: architecture
      path: content/architecture.md
      agent: mkdocs
    - id: slides
      path: content/slides.md
      agent: marp

  diagram_specs:
    - type: c4_context
      framework: d2  # Auto-selected if omitted
      instructions: "Specific diagram instructions"

  outputs:
    assets_dir: docs/assets

    mkdocs:
      config_file: mkdocs.yml
      content_refs: [content/overview.md, content/architecture.md]

    marpkit:
      slide_files: [content/slides.md]
      theme: gaia
      export_pdf: true
```

## Framework Routing
- C4 diagrams → D2
- Sequence/Flowcharts → Mermaid
- ERD → Mermaid
- Gantt → Mermaid (only option)
- Architecture → D2
- Network → D2

## Architecture Highlights

### Claude-Centric Design
- **Claude Orchestrator**: Main workflow coordination via Claude Code command
- **Content Subagents**: Markdown maintenance via Claude Code prompts
- **Minimal Python**: Only for diagram generation and YAML parsing
- **Dynamic Workflow**: Claude adapts orchestration based on recipe content

### Dual-Mode Operation
- **Interactive Mode**: Claude Desktop + MCP for recipe creation/editing
- **Processing Mode**: Desktop Commander headless for batch execution
- **Claude Execution**: All orchestration and content generation via Claude Code

### Workflow
1. Create/edit recipe via MCP in Claude Desktop
2. CLI invokes Claude orchestrator via Desktop Commander
3. Claude orchestrator coordinates:
   - Calls Python services for YAML parsing
   - Calls Python generators for diagrams
   - Calls Claude subagents for content
   - Generates MkDocs/MarpKit configurations
4. Both outputs reference the same markdown files

## Current Phase
Implementing Phase 1: Design artifacts complete with markdown-first approach. Ready for task breakdown.

## Recent Changes
- Claude Code is now the main orchestrator, not just subagents
- Minimal Python services only for diagram generation
- All workflow coordination handled by Claude
- Orchestration logic defined in prompts, easily modifiable

## Testing Strategy
- Contract tests for all API endpoints
- Unit tests for each service component
- Integration tests for recipe processing
- Framework-specific generator tests

## Performance Goals
- Sub-10 second generation for standard docs
- <200ms recipe validation
- <5s per diagram generation
- Support 50+ recipes batch processing

---
*Context updated: 2025-01-16*