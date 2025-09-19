# Tasks: Multi-Framework Diagram Pipeline

**Input**: Design documents from `/specs/001-i-want-to/`
**Prerequisites**: plan.md (required), research.md, data-model.md, quickstart.md

## Execution Flow (main)
```
1. Load plan.md from feature directory
   → If not found: ERROR "No implementation plan found"
   → Extract: tech stack (Python 3.11+, Click, FastMCP), structure (src layout)
2. Load optional design documents:
   → data-model.md: Extract entities → model tasks
   → quickstart.md: Extract test scenarios → integration tests
   → research.md: Extract decisions → setup tasks
3. Generate tasks by category:
   → Setup: project init, dependencies, linting
   → Tests: model tests, MCP tests, integration tests
   → Core: models, MCP server, CLI commands
   → Agents: Claude Code agent definitions
   → Integration: mise setup, agent installation
   → Polish: unit tests, examples, documentation
4. Apply task rules:
   → Different files = mark [P] for parallel
   → Same file = sequential (no [P])
   → Tests before implementation (TDD)
5. Number tasks sequentially (T001, T002...)
6. Generate dependency graph
7. Create parallel execution examples
8. Validate task completeness:
   → All entities have models?
   → All MCP tools implemented?
   → All agents defined?
9. Return: SUCCESS (tasks ready for execution)
```

## Format: `[ID] [P?] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in descriptions

## Path Conventions
- **Single project**: `src/`, `tests/` at repository root
- Python package: `src/t2d_kit/` for source code
- Agents: `src/t2d_kit/agents/` for Claude Code agent definitions
- Tests: `tests/unit/`, `tests/integration/`

## Phase 3.1: Setup
- [x] T001 Create Python project structure with src layout at repository root
- [x] T002 Initialize pyproject.toml with Click, FastMCP, Pydantic dependencies
- [x] T003 [P] Configure ruff for linting and black for formatting in pyproject.toml
- [x] T004 [P] Create .mise.toml with Python 3.11, Node 20, Go 1.21, Java 17 requirements
- [x] T005 [P] Setup pre-commit hooks for code quality checks

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3
**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**
- [x] T006 [P] Test UserRecipe model validation in tests/unit/test_user_recipe.py
- [x] T007 [P] Test ProcessedRecipe model validation in tests/unit/test_processed_recipe.py
- [x] T008 [P] Test DiagramSpecification validation in tests/unit/test_diagram_spec.py
- [x] T009 [P] Test MCP read_user_recipe tool in tests/unit/test_mcp_read.py
- [x] T010 [P] Test MCP write_processed_recipe tool in tests/unit/test_mcp_write.py
- [x] T011 [P] Test state management in tests/unit/test_state_manager.py
- [x] T012 [P] Integration test recipe transformation in tests/integration/test_transform.py
- [x] T013 [P] Integration test D2 diagram generation in tests/integration/test_d2_gen.py
- [x] T014 [P] Integration test MkDocs page generation in tests/integration/test_mkdocs.py

## Phase 3.3: Core Implementation (ONLY after tests are failing)

### Core Models
- [x] T015 [P] Create T2DBaseModel with validation in src/t2d_kit/models/base.py
- [x] T016 [P] Create UserRecipe model in src/t2d_kit/models/user_recipe.py
- [x] T017 [P] Create ProcessedRecipe model in src/t2d_kit/models/processed_recipe.py
- [x] T018 [P] Create DiagramSpecification model in src/t2d_kit/models/diagram.py
- [x] T019 [P] Create ContentFile model in src/t2d_kit/models/content.py
- [x] T020 [P] Create StateManager in src/t2d_kit/models/state.py
- [x] T021 [P] Create D2Options model in src/t2d_kit/models/d2_options.py
- [x] T022 [P] Create MermaidConfig model in src/t2d_kit/models/mermaid_config.py
- [x] T023 [P] Create MkDocsPageConfig model in src/t2d_kit/models/mkdocs_config.py
- [x] T024 [P] Create MarpConfig model in src/t2d_kit/models/marp_config.py

### MCP Server
- [x] T025 Create FastMCP server initialization in src/t2d_kit/mcp/server.py
- [x] T026 Implement read_user_recipe MCP tool in src/t2d_kit/mcp/server.py
- [x] T027 Implement write_processed_recipe MCP tool in src/t2d_kit/mcp/server.py
- [x] T028 Implement read_processed_recipe MCP tool in src/t2d_kit/mcp/server.py
- [x] T029 Implement validate_recipe MCP tool in src/t2d_kit/mcp/server.py
- [x] T030 Create MCP __main__.py entry point in src/t2d_kit/mcp/__main__.py

### CLI Commands
- [x] T031 Create CLI main entry in src/t2d_kit/cli/main.py with Click
- [x] T032 Implement 't2d setup' command in src/t2d_kit/cli/setup.py
- [x] T033 Implement 't2d mcp' server command in src/t2d_kit/cli/mcp_cmd.py
- [x] T034 Implement 't2d verify' command in src/t2d_kit/cli/verify.py
- [x] T035 Create package entry point in src/t2d_kit/__main__.py

### Agent Definitions
- [x] T036 [P] Create t2d-transform agent in src/t2d_kit/agents/t2d-transform.md
- [x] T037 [P] Create t2d-d2-generator agent in src/t2d_kit/agents/t2d-d2-generator.md
- [x] T038 [P] Create t2d-mermaid-generator agent in src/t2d_kit/agents/t2d-mermaid-generator.md
- [x] T039 [P] Create t2d-plantuml-generator agent in src/t2d_kit/agents/t2d-plantuml-generator.md
- [x] T040 [P] Create t2d-docs-generator agent in src/t2d_kit/agents/t2d-docs-generator.md
- [x] T041 [P] Create t2d-slides-generator agent in src/t2d_kit/agents/t2d-slides-generator.md

## Phase 3.4: Integration
- [x] T042 Setup agent installation logic in src/t2d_kit/cli/setup.py
- [x] T043 Implement mise dependency check in src/t2d_kit/cli/verify.py
- [x] T044 Connect MCP server to Claude Desktop config detection
- [x] T045 Add state directory management to StateManager
- [x] T046 Implement recipe file watching in MCP server
- [x] T047 Add error recovery to state management

## Phase 3.5: Polish
- [x] T048 [P] Create example recipe.yaml in examples/simple/recipe.yaml
- [x] T049 [P] Create complex recipe example in examples/complex/recipe.yaml
- [x] T050 [P] Add API documentation in docs/api.md
- [x] T051 [P] Create agent usage guide in docs/agents.md
- [x] T052 [P] Write performance tests in tests/performance/test_processing.py
- [x] T053 Update README.md with quickstart instructions
- [x] T054 Create CLAUDE.md context file for agent awareness
- [x] T055 Run quickstart.md validation scenarios

## Dependencies
- Setup (T001-T005) must complete first
- Tests (T006-T014) before implementation (T015-T041)
- Core models (T015-T024) can run in parallel
- MCP tools (T025-T030) must be sequential (same file)
- CLI commands (T031-T035) must be sequential (imports)
- Agents (T036-T041) can run in parallel
- Integration (T042-T047) after core implementation
- Polish (T048-T055) last

## Parallel Execution Examples

### Launch all model tests together (Phase 3.2):
```
Task: "Test UserRecipe model validation in tests/unit/test_user_recipe.py"
Task: "Test ProcessedRecipe model validation in tests/unit/test_processed_recipe.py"
Task: "Test DiagramSpecification validation in tests/unit/test_diagram_spec.py"
Task: "Test MCP read_user_recipe tool in tests/unit/test_mcp_read.py"
Task: "Test MCP write_processed_recipe tool in tests/unit/test_mcp_write.py"
Task: "Test state management in tests/unit/test_state_manager.py"
```

### Create all models in parallel (Phase 3.3):
```
Task: "Create T2DBaseModel with validation in src/t2d_kit/models/base.py"
Task: "Create UserRecipe model in src/t2d_kit/models/user_recipe.py"
Task: "Create ProcessedRecipe model in src/t2d_kit/models/processed_recipe.py"
Task: "Create DiagramSpecification model in src/t2d_kit/models/diagram.py"
Task: "Create ContentFile model in src/t2d_kit/models/content.py"
Task: "Create StateManager in src/t2d_kit/models/state.py"
Task: "Create D2Options model in src/t2d_kit/models/d2_options.py"
Task: "Create MermaidConfig model in src/t2d_kit/models/mermaid_config.py"
Task: "Create MkDocsPageConfig model in src/t2d_kit/models/mkdocs_config.py"
Task: "Create MarpConfig model in src/t2d_kit/models/marp_config.py"
```

### Define all agents simultaneously (Phase 3.3):
```
Task: "Create t2d-transform agent in src/t2d_kit/agents/t2d-transform.md"
Task: "Create t2d-d2-generator agent in src/t2d_kit/agents/t2d-d2-generator.md"
Task: "Create t2d-mermaid-generator agent in src/t2d_kit/agents/t2d-mermaid-generator.md"
Task: "Create t2d-plantuml-generator agent in src/t2d_kit/agents/t2d-plantuml-generator.md"
Task: "Create t2d-docs-generator agent in src/t2d_kit/agents/t2d-docs-generator.md"
Task: "Create t2d-slides-generator agent in src/t2d_kit/agents/t2d-slides-generator.md"
```

## Notes
- [P] tasks = different files, no shared dependencies
- MCP server tasks sequential (same file modifications)
- CLI tasks sequential (import dependencies)
- Verify tests fail before implementing models
- Commit after each task completion
- Agent files are markdown with YAML frontmatter

## Validation Checklist
*GATE: Checked before execution*

- [x] All entities have model tasks (UserRecipe, ProcessedRecipe, etc.)
- [x] All MCP tools have implementation tasks
- [x] All agents have definition tasks
- [x] Tests come before implementation (T006-T014 before T015-T041)
- [x] Parallel tasks are truly independent (different files)
- [x] Each task specifies exact file path
- [x] No [P] tasks modify the same file
- [x] Integration tests cover quickstart scenarios

---
*Generated from plan.md, data-model.md, and quickstart.md*
*Total tasks: 55 | Setup: 5 | Tests: 9 | Core: 26 | Agents: 6 | Integration: 6 | Polish: 8*