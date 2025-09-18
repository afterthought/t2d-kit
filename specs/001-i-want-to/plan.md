# Implementation Plan: Multi-Framework Diagram Pipeline

**Branch**: `001-i-want-to` | **Date**: 2025-01-16 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-i-want-to/spec.md`

## Execution Flow (/plan command scope)
```
1. Load feature spec from Input path
   → If not found: ERROR "No feature spec at {path}"
2. Fill Technical Context (scan for NEEDS CLARIFICATION)
   → Detect Project Type from context (web=frontend+backend, mobile=app+api)
   → Set Structure Decision based on project type
3. Fill the Constitution Check section based on the content of the constitution document.
4. Evaluate Constitution Check section below
   → If violations exist: Document in Complexity Tracking
   → If no justification possible: ERROR "Simplify approach first"
   → Update Progress Tracking: Initial Constitution Check
5. Execute Phase 0 → research.md
   → If NEEDS CLARIFICATION remain: ERROR "Resolve unknowns"
6. Execute Phase 1 → data-model.md, quickstart.md, CLAUDE.md (agent context file)
7. Re-evaluate Constitution Check section
   → If new violations: Refactor design, return to Phase 1
   → Update Progress Tracking: Post-Design Constitution Check
8. Plan Phase 2 → Describe task generation approach (DO NOT create tasks.md)
9. STOP - Ready for /tasks command
```

**IMPORTANT**: The /plan command STOPS at step 7. Phases 2-4 are executed by other commands:
- Phase 2: /tasks command creates tasks.md
- Phase 3-4: Implementation execution (manual or via tools)

## Summary
A multi-framework diagram generation pipeline that processes YAML recipes to automatically create documentation-ready diagrams. The system is entirely Claude Code-driven, with Claude as the orchestrator and all subagents (diagram generators and content maintainers) executed via Desktop Commander.

**Key Architecture Points** (see detailed docs):
- **Two-File Recipe System** ([transformation-workflow.md](transformation-workflow.md)): User recipe.yaml → Agent-generated recipe.t2d.yaml
- **Python Components** ([mcp-server.md](mcp-server.md)): MCP server for file operations, minimal CLI wrapper
- **Claude Code Components**: Transform agent, orchestrator, diagram generators, content maintainers
- **Installation** ([installation-setup.md](installation-setup.md)): uvx package with `t2d setup` to install agent files to ~/.claude
- **Dependency Management**: mise for tool versions (Go, Node, Java)

Built as a CLI tool with easy installation via uvx, with MCP server for Claude Desktop recipe manipulation and Desktop Commander for headless processing.

## Technical Context
**Language/Version**: Python 3.11+ (minimal - CLI wrapper only)
**Primary Dependencies**: Click (CLI wrapper), MCP, Claude Code, d2 CLI, Mermaid CLI, MkDocs, MarpKit
**Storage**: File-based (YAML recipes, generated markdown/diagrams)
**Testing**: pytest
**Target Platform**: Cross-platform CLI (Linux, macOS, Windows)
**Project Type**: single (CLI tool with library core)
**Performance Goals**: Sub-10 second generation time for standard documentation sets
**Constraints**: <200ms recipe validation, <5s per diagram generation, support 10+ diagram types
**Scale/Scope**: Support processing of complex recipes with 10+ diagrams per recipe

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Since the constitution template is not yet filled out, applying general best practices:

- ✅ **Library-First**: Core functionality as importable Python library
- ✅ **CLI Interface**: Primary interaction through CLI with text in/out
- ✅ **Simplicity**: Start with core features, avoid over-engineering
- ✅ **Modularity**: Separate concerns (recipe parsing, routing, generation, output)
- ✅ **Testability**: Each component independently testable

## Project Structure

### Documentation (this feature)
```
specs/001-i-want-to/
├── plan.md                      # This file (/plan command output)
├── research.md                  # Phase 0 output (/plan command)
├── data-model.md                # Phase 1 output (/plan command)
├── quickstart.md                # Phase 1 output (/plan command)
├── mcp-server.md                # MCP server specification (/plan command)
├── installation-setup.md        # Installation and agent setup (/plan command)
├── transformation-workflow.md   # Two-file recipe workflow (/plan command)
└── tasks.md                     # Phase 2 output (/tasks command - NOT created by /plan)
```

### Source Code (repository root)
```
# Option 1: Single project (DEFAULT)
t2d-kit/
├── cli/
│   └── main.py          # Minimal CLI wrapper (env setup, invoke agents)
├── mcp/                 # MCP server for recipe file management
│   ├── server.py        # Read/write/validate user recipes
│   ├── models.py        # Pydantic models for validation
│   └── config.json      # MCP server configuration
├── agents/              # Claude Code subagents (Markdown with YAML frontmatter)
│   ├── t2d-transform.md        # Transform user recipe → processed recipe
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

**Structure Decision**: Option 1 (Single project) - CLI tool with library core

## Phase 0: Outline & Research
1. **Extract unknowns from Technical Context** above:
   - Research best practices for Python CLI distribution via uvx
   - Research MkDocs plugin architecture for diagram integration
   - Research MarpKit presentation generation with embedded diagrams
   - Research Claude Desktop MCP server implementation
   - Research Desktop Commander headless execution for Claude Code agents
   - Resolve recipe file size limit (FR-016)
   - Resolve asset retention period (FR-017)
   - Resolve concurrent processing limits (FR-018)

2. **Generate and dispatch research agents**:
   ```
   Task: "Research Python packaging for uvx distribution"
   Task: "Find best practices for YAML recipe validation"
   Task: "Research MkDocs diagram plugin integration"
   Task: "Research MarpKit presentation features and diagram embedding"
   Task: "Research Claude Desktop MCP server patterns"
   Task: "Find optimal strategies for parallel diagram generation"
   ```

3. **Consolidate findings** in `research.md` using format:
   - Decision: [what was chosen]
   - Rationale: [why chosen]
   - Alternatives considered: [what else evaluated]

**Output**: research.md with all NEEDS CLARIFICATION resolved

## Phase 1: Design & Data Model
*Prerequisites: research.md complete*

1. **Extract entities from feature spec** → `data-model.md`:
   - Recipe: YAML configuration with markdown file references, diagram specs
   - MarkdownContent: Reusable markdown files maintained by subagents
   - DiagramSpecification: Type, framework, instructions, output format
   - FrameworkMapping: Diagram type to framework associations
   - OutputConfiguration: References to markdown files for MkDocs/MarpKit
   - ProcessingLog: Execution status and diagnostics

2. **Define CLI commands** (handled by Claude orchestrator):
   - `t2d create <recipe.yml>`: Process recipe file
   - `t2d setup`: Bootstrap mise dependencies

3. **Define test scenarios** from user stories:
   - Product manager creates architecture diagrams from PRD
   - Technical writer generates GitHub-ready documentation
   - Developer processes complex recipe with many diagrams
   - System handles unsupported diagram types
   - Agents bootstrap missing tools via mise

4. **Create quickstart guide** with examples:
   - Recipe YAML structure
   - Claude Code architecture explanation
   - MCP and Desktop Commander integration
   - mise dependency management

5. **Update agent context file**:
   - Create CLAUDE.md with project context
   - Add t2d-kit specific patterns and conventions

**Output**:
- data-model.md - Entity definitions and relationships
- quickstart.md - User guide with examples
- mcp-server.md - MCP server implementation spec
- installation-setup.md - Agent installation process
- transformation-workflow.md - Recipe transformation workflow
- CLAUDE.md - Agent context file

## Phase 2: Task Planning Approach
*This section describes what the /tasks command will do - DO NOT execute during /plan*

**Task Generation Strategy**:
- Minimal Python: CLI wrapper and MCP server
- Setup command to install agent files to ~/.claude
- MCP server for recipe management (read, write, validate YAML)
- Claude Code orchestrator (includes routing rules, uses MCP tools)
- Claude Code diagram generator agents (D2, Mermaid, PlantUML)
- Claude Code content maintainer agents
- Desktop Commander integration for headless execution
- Integration with CLI tools (d2, mmdc, plantuml)
- mise dependency bootstrapping
- Testing tasks (integration, end-to-end)

**Ordering Strategy**:
1. CLI wrapper implementation
2. MCP server configuration
3. Claude orchestrator command template
4. Claude generator agent prompts [P]
5. Claude content agent prompts [P]
6. Integration tests
7. Documentation and examples

**Estimated Output**: 25-30 numbered, ordered tasks in tasks.md

**IMPORTANT**: This phase is executed by the /tasks command, NOT by /plan

## Phase 3+: Future Implementation
*These phases are beyond the scope of the /plan command*

**Phase 3**: Task execution (/tasks command creates tasks.md)
**Phase 4**: Implementation (execute tasks.md following constitutional principles)
**Phase 5**: Validation (run tests, execute quickstart.md, performance validation)

## Complexity Tracking
*No violations identified - design follows simplicity and modularity principles*

## Progress Tracking
*This checklist is updated during execution flow*

**Phase Status**:
- [x] Phase 0: Research complete (/plan command)
- [x] Phase 1: Design complete (/plan command)
- [x] Phase 2: Task planning complete (/plan command - describe approach only)
- [ ] Phase 3: Tasks generated (/tasks command)
- [ ] Phase 4: Implementation complete
- [ ] Phase 5: Validation passed

**Gate Status**:
- [x] Initial Constitution Check: PASS
- [x] Post-Design Constitution Check: PASS
- [x] All NEEDS CLARIFICATION resolved
- [x] Complexity deviations documented

---
*Based on Constitution v2.1.1 - See `/memory/constitution.md`*