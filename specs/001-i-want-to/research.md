# Research Findings: Multi-Framework Diagram Pipeline

**Date**: 2025-01-16
**Feature**: Multi-Framework Diagram Pipeline
**Branch**: 001-i-want-to

## Executive Summary
Research conducted to resolve technical unknowns for the t2d-kit diagram generation pipeline. Key decisions include Python 3.11+ with Click for CLI, distribution via uvx and npx wrapper, and MkDocs with native plugin support for diagram rendering.

## Research Areas

### 1. Python CLI Distribution via uvx
**Decision**: Use `uv` for Python package management and `uvx` for global tool installation
**Rationale**:
- Fast, Rust-based Python package manager
- Single-command global installation: `uvx install t2d-kit`
- Handles Python environment automatically
- Growing adoption in Python ecosystem
**Alternatives Considered**:
- pipx: Older, slower, less feature-rich
- pip global install: Dependency conflicts, not isolated
- Docker: Too heavyweight for CLI tool

### 2. Distribution Strategy
**Decision**: uvx-only distribution for simplicity
**Rationale**:
- Single distribution method reduces complexity
- uvx handles Python environment automatically
- Growing adoption in Python ecosystem
- Users who need diagram tools likely have Python tooling
**Alternatives Considered**:
- NPX wrapper: Adds unnecessary complexity for limited benefit
- Docker: Too heavyweight for CLI tool
- Standalone binary: Complex packaging, platform-specific issues

### 3. YAML Recipe Validation
**Decision**: Use Pydantic models with YAML schema validation
**Rationale**:
- Type-safe data models
- Automatic validation and error messages
- JSON Schema generation for documentation
- IDE autocomplete support
**Alternatives Considered**:
- Cerberus: Less type safety
- Manual validation: Error-prone
- JSON Schema only: No Python type hints

### 4. Documentation and Presentation Generation
**Decision**: Markdown-first approach with file references for both MkDocs and MarpKit
**Rationale**:
- Consistent architecture: both tools reference markdown files
- Content maintained by specialized subagents
- Reusable markdown content across formats
- Clean separation between content and presentation
**Implementation**:
- Markdown files created and maintained by subagents
- MkDocs references markdown files in mkdocs.yml
- MarpKit references markdown files for slide generation
- Orchestrator coordinates file generation and references
**Alternatives Considered**:
- Inline content generation: Less reusable, harder to maintain
- Direct API integration: Tighter coupling, less flexible
- Single tool only: Limits output flexibility

### 5. Claude Desktop/Desktop Commander Integration
**Decision**: Dual-mode integration with MCP for manipulation and Desktop Commander for processing
**Rationale**:
- MCP server for interactive recipe creation/editing in Claude Desktop
- Desktop Commander for headless batch processing
- Claude Code as subagents for content generation
- Clean separation between UI and processing
**Architecture**:
- **Claude Desktop + MCP**: Interactive recipe development
- **Desktop Commander**: Headless execution environment
- **Claude Code**: Content generation subagents
- **Python Core**: Diagram generation and orchestration
**Alternatives Considered**:
- REST API: No native integration
- Python-only agents: Less flexible content generation
- Single mode: Limited use cases

### 6. Batch Processing Strategy
**Decision**: Async processing with configurable worker pool
**Rationale**:
- Parallel diagram generation
- Memory-efficient for large batches
- Progress reporting capability
- Configurable concurrency limits
**Alternatives Considered**:
- Serial processing: Too slow
- Multiprocessing: Higher overhead
- External queue: Over-engineered

### 7. Fully Claude-Driven Architecture
**Decision**: Use Claude Code for everything - orchestration, routing, diagram generation, and content
**Rationale**:
- Maximum flexibility and adaptability
- No Python services to maintain (except minimal CLI wrapper)
- All logic in prompts, easily modifiable
- Consistent architecture with Claude handling all operations
- MCP provides file operations, eliminating need for Python parsers
**Implementation**:
```yaml
# Main orchestrator (Claude Code command)
orchestrator:
  type: claude_code_command
  template: commands/orchestrate.txt
  responsibilities:
    - Read and parse YAML via MCP
    - Apply routing rules (in prompt)
    - Invoke diagram generator agents
    - Call content maintainer agents
    - Coordinate output generation

# Diagram generator agents (use CLI tools)
diagram_generators:
  d2_agent:
    type: claude_code
    prompt: prompts/generators/d2_generator.txt
    tools: d2 CLI

  mermaid_agent:
    type: claude_code
    prompt: prompts/generators/mermaid_generator.txt
    tools: mmdc CLI

  plantuml_agent:
    type: claude_code
    prompt: prompts/generators/plantuml_generator.txt
    tools: plantuml CLI

# Content maintainer agents
content_agents:
  markdown_maintainer:
    prompt: prompts/content/markdown_maintainer.txt
  mkdocs_formatter:
    prompt: prompts/content/mkdocs_formatter.txt
  marp_slides:
    prompt: prompts/content/marp_slides.txt

# Minimal Python
python_code:
  - cli/main.py    # Just invokes Claude orchestrator
```

**Routing Rules in Orchestrator Prompt**:
```
When routing diagrams to frameworks, use these rules:
- C4 diagrams (context, container, component) → D2
- Sequence diagrams → Mermaid
- Flowcharts → Mermaid
- ERD → Mermaid
- Gantt → Mermaid (only option)
- Architecture → D2
- Network → D2
- State machines → Mermaid
- Class diagrams → PlantUML
- Allow user overrides if specified
```

**Execution Flow**:
1. CLI wrapper invokes Claude orchestrator
2. Claude orchestrator handles everything:
   - Reads recipe file via MCP
   - Parses YAML structure
   - Routes diagrams based on rules
   - Invokes appropriate generator agents
   - Generator agents use CLI tools to create diagrams
   - Content agents create markdown
   - Outputs final files
3. Results returned to user

### 8. Slash Command Routing
**Decision**: Rule-based routing with override capability
**Rationale**:
- Predictable framework selection
- User can override when needed
- Extensible mapping configuration
- Clear fallback behavior
**Default Mappings**:
- Architecture diagrams → D2
- Sequence/Flowcharts → Mermaid
- Gantt charts → Mermaid (only option)
- ERD → Mermaid
- C4 diagrams → D2
- Network diagrams → D2
- State machines → Mermaid

### 9. Tool Dependency Management via mise
**Decision**: Use mise-en-place for managing tool versions and dependencies
**Rationale**:
- Declarative tool version management via `.mise.toml`
- Cross-platform support (Linux, macOS, Windows via WSL)
- Agents can bootstrap their own dependencies
- Consistent tool versions across environments
- No need for users to manually install d2, node, java
**Bootstrap Strategy**:
1. CLI wrapper checks for mise on first run
2. If missing, installs mise automatically
3. mise installs required tools based on `.mise.toml`
4. Claude agents can call `mise install` to ensure deps
**Implementation**:
```toml
# .mise.toml
[tools]
python = "3.11"
node = "20"
go = "1.21"
java = "17"  # for PlantUML
"npm:@mermaid-js/mermaid-cli" = "latest"  # Installs mmdc CLI
"go:oss.terrastruct.com/d2" = "latest"     # Installs d2 CLI

# Optional: PlantUML setup task since it's not a simple binary
[tasks.setup-plantuml]
description = "Download and setup PlantUML jar"
run = """
  mkdir -p ~/.local/share/plantuml
  curl -L https://github.com/plantuml/plantuml/releases/latest/download/plantuml.jar \
    -o ~/.local/share/plantuml/plantuml.jar
  echo "PlantUML jar installed to ~/.local/share/plantuml/"
"""
```
**Alternatives Considered**:
- Manual installation: Poor user experience
- Docker: Too heavyweight for CLI tool
- Package managers (brew/apt): Platform-specific
- Bundling: Complex packaging, large distribution

## Resolved Clarifications

### FR-016: Maximum Recipe File Size
**Decision**: 10MB limit per recipe file
**Rationale**:
- Covers 99.9% of use cases
- Prevents memory issues
- PRD content typically <1MB
- Configurable via environment variable

### FR-017: Asset Retention Period
**Decision**: Indefinite local storage, 30-day cache for rendered assets
**Rationale**:
- Source files kept permanently
- Rendered assets regeneratable
- Cache improves performance
- User controls deletion

### FR-018: Concurrent User Limit
**Decision**: Single-user CLI tool, no concurrent limit
**Rationale**:
- CLI runs in user context
- File locking for shared recipes
- Server mode future enhancement
- Batch processing handles multiple recipes

## Technology Stack Summary

### Core Dependencies
- **Python 3.11+**: Modern Python features, type hints
- **Click 8.1+**: CLI framework
- **Pydantic 2.0+**: Data validation
- **PyYAML 6.0+**: YAML parsing
- **Jinja2 3.0+**: Template engine
- **httpx**: Async HTTP for API future

### Dependency Management
- **mise (mise-en-place)**: Tool version management and dependency bootstrapping
- **Bootstrap strategy**: CLI wrapper checks and installs mise if needed
- **Tool management**: mise handles Python, Node, Go, Java versions per project

### Diagramming Tools (managed via mise)
- **D2**: Architecture diagrams (requires Go, installed via `go install`)
- **Mermaid CLI**: Flowcharts, sequence, ERD (requires Node, installed via npm)
- **PlantUML**: UML diagrams (requires Java, jar file or system package)

### Documentation & Presentation
- **MkDocs 1.5+**: Documentation framework
- **mkdocs-mermaid2-plugin**: Mermaid integration
- **mkdocs-d2-plugin**: D2 integration (custom or community)
- **MarpKit**: Presentation generation from Markdown
- **Marp CLI**: Converting Marp markdown to slides

### Development Tools
- **pytest 7.0+**: Testing framework
- **pytest-asyncio**: Async test support
- **black**: Code formatting
- **ruff**: Linting
- **mypy**: Type checking

### Distribution
- **uv**: Python package management and distribution
- **setuptools**: Python packaging
- **pyproject.toml**: Modern Python project configuration

## Implementation Considerations

### Performance Optimizations
1. Lazy loading of framework generators
2. Parallel diagram generation (asyncio)
3. Template caching for markdown generation
4. Incremental recipe processing

### Error Handling Strategy
1. Validation errors → Clear user messages
2. Framework errors → Fallback to Mermaid
3. File errors → Retry with backoff
4. Batch errors → Continue with working recipes

### Extensibility Points
1. New framework generators via plugin system
2. Custom diagram type mappings
3. Template customization
4. Output format plugins

## Next Steps
With research complete, proceed to Phase 1:
1. Create data models (data-model.md)
2. Define API contracts
3. Generate test specifications
4. Create quickstart guide
5. Update CLAUDE.md with project context

---
*Research completed: 2025-01-16*