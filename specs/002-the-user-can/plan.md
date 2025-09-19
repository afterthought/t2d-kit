# Implementation Plan: User Recipe File Management

**Branch**: `002-the-user-can` | **Date**: 2025-09-18 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-the-user-can/spec.md`

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
6. Execute Phase 1 → contracts, data-model.md, quickstart.md, agent-specific template file (e.g., `CLAUDE.md` for Claude Code)
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
An MCP (Model Context Protocol) server enhancement that exposes **resources** for diagram types and recipes (both user and processed), plus **tools** for creating and managing both user recipe files and processed recipe files in the t2d-kit system. The MCP resources will allow clients to discover available diagram types, browse existing user recipes and processed recipes, and understand both recipe schemas. The MCP tools will enable users to create, validate, edit, and delete both user recipe files (`recipe.yaml`) and processed recipe files (`recipe.t2d.yaml`). Both resources and tools will include proper system prompts and discovery metadata to ensure MCP clients can easily find and use the functionality.

## Technical Context
**Language/Version**: Python 3.11+ (FastMCP framework)
**Primary Dependencies**: FastMCP, Pydantic v2, PyYAML, pathlib
**Storage**: Filesystem-based YAML files (.yaml, .yml extensions)
**Testing**: pytest with FastMCP test utilities
**Target Platform**: Cross-platform MCP server (stdio mode)
**Project Type**: single (MCP server tool within existing t2d-kit)
**Performance Goals**: Recipe validation < 200ms, file operations < 100ms
**Constraints**: 1MB max file size, YAML format only, no access controls
**Scale/Scope**: Support multiple recipe files, concurrent operations safe

**User-provided implementation details**: Let's make an MCP tool for creating the recipe. Let's make sure that system prompts help the MCP client properly discover the tool.

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Since the constitution template is not fully filled, applying general software engineering principles:

- ✅ **Library-First**: MCP tool as standalone component with clear interface
- ✅ **CLI Interface**: MCP provides text-based protocol (JSON-RPC over stdio)
- ✅ **Test-First**: Will generate contract tests before implementation
- ✅ **Integration Testing**: MCP tool integrates with existing t2d-kit models
- ✅ **Observability**: MCP provides structured logging and error reporting
- ✅ **Simplicity**: Single-purpose tool focused on recipe file management

## Project Structure

### Documentation (this feature)
```
specs/002-the-user-can/
├── plan.md              # This file (/plan command output)
├── research.md          # Phase 0 output (/plan command)
├── data-model.md        # Phase 1 output (/plan command)
├── quickstart.md        # Phase 1 output (/plan command)
├── contracts/           # Phase 1 output (/plan command)
└── tasks.md             # Phase 2 output (/tasks command - NOT created by /plan)
```

### Source Code (repository root)
```
# Option 1: Single project (DEFAULT) - extending existing t2d-kit structure
src/t2d_kit/
├── mcp/
│   ├── resources/
│   │   ├── __init__.py
│   │   ├── diagram_types.py         # Resource: Available diagram types
│   │   ├── user_recipes.py          # Resource: Existing user recipes
│   │   ├── processed_recipes.py     # Resource: Existing processed recipes
│   │   ├── user_recipe_schema.py    # Resource: User recipe YAML schema
│   │   └── processed_recipe_schema.py # Resource: Processed recipe schema
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── user_recipe_tools.py     # Tools: Create/edit/delete user recipes
│   │   └── processed_recipe_tools.py # Tools: Write/update processed recipes
│   └── server.py                     # Enhanced with resources & tools
├── models/
│   ├── user_recipe.py               # User recipe Pydantic models
│   └── processed_recipe.py          # Processed recipe Pydantic models
└── cli/

tests/
├── contract/
│   ├── test_mcp_resources.py        # Contract tests for resources
│   ├── test_user_recipe_tools.py    # Contract tests for user recipe tools
│   └── test_processed_recipe_tools.py # Contract tests for processed tools
├── integration/
│   └── test_mcp_recipe_flow.py      # End-to-end MCP tests
└── unit/
    └── test_recipe_validation.py    # Unit tests
```

**Structure Decision**: Option 1 (Single project) - extending existing t2d-kit MCP server

## Phase 0: Outline & Research
1. **Extract unknowns from Technical Context**:
   - MCP resource vs tool distinction and best practices
   - FastMCP resource registration and URI patterns
   - MCP resource discovery mechanisms and metadata
   - Dynamic resource generation from filesystem
   - MCP tool discovery mechanisms and system prompts
   - YAML schema validation strategies
   - File system operations in MCP context
   - Error handling and validation feedback patterns

2. **Generate and dispatch research agents**:
   ```
   Task: "Research MCP resource patterns for exposing read-only data"
   Task: "Find FastMCP resource registration with URIs and metadata"
   Task: "Research MCP tool vs resource distinction and when to use each"
   Task: "Find patterns for dynamic MCP resource generation from files"
   Task: "Research MCP discovery prompts for resources and tools"
   Task: "Research YAML validation with Pydantic models"
   Task: "Find file system safety patterns for MCP operations"
   Task: "Research MCP error handling and user feedback"
   ```

3. **Consolidate findings** in `research.md` using format:
   - Decision: [what was chosen]
   - Rationale: [why chosen]
   - Alternatives considered: [what else evaluated]

**Output**: research.md with all NEEDS CLARIFICATION resolved

## Phase 1: Design & Contracts
*Prerequisites: research.md complete*

1. **Extract entities from feature spec** → `data-model.md`:
   - DiagramTypeResource (read-only resource)
   - UserRecipeResource (read-only resource)
   - ProcessedRecipeResource (read-only resource)
   - RecipeSchemaResource (read-only resource for both types)
   - UserRecipe entity with validation rules
   - ProcessedRecipe entity with detailed specifications
   - RecipeCreationRequest/Response models
   - ProcessedRecipeWriteRequest/Response models
   - ValidationError model for feedback
   - FileOperationResult model

2. **Generate API contracts** from functional requirements:
   **Resources (read-only)**:
   - `diagram-types://` - List all available diagram types
   - `user-recipes://` - List all user recipes
   - `user-recipes://{recipe_name}` - Get specific user recipe
   - `processed-recipes://` - List all processed recipes
   - `processed-recipes://{recipe_name}` - Get specific processed recipe
   - `user-recipe-schema://` - Get user recipe YAML schema
   - `processed-recipe-schema://` - Get processed recipe YAML schema

   **Tools (read-write)**:
   User Recipe Tools:
   - `create_user_recipe` tool contract
   - `validate_user_recipe` tool contract
   - `edit_user_recipe` tool contract
   - `delete_user_recipe` tool contract

   Processed Recipe Tools:
   - `write_processed_recipe` tool contract (from existing MCP server)
   - `update_processed_recipe` tool contract
   - `validate_processed_recipe` tool contract

   Output MCP schemas to `/contracts/`

3. **Generate contract tests** from contracts:
   - Test resource registration and URIs
   - Test resource discovery metadata
   - Test tool registration and discovery
   - Test recipe creation with valid/invalid data
   - Test validation feedback
   - Test file operations
   - Tests must fail (no implementation yet)

4. **Extract test scenarios** from user stories:
   - User discovers available diagram types via resources
   - User browses existing recipes via resources
   - User creates first recipe file using tool
   - User edits existing recipe using tool
   - User receives validation errors
   - User deletes recipe file using tool

5. **Update agent file incrementally**:
   - Run `.specify/scripts/bash/update-agent-context.sh claude`
   - Add MCP resource/tool development context
   - Update with FastMCP patterns
   - Keep under 150 lines

**Output**: data-model.md, /contracts/*, failing tests, quickstart.md, CLAUDE.md

## Phase 2: Task Planning Approach
*This section describes what the /tasks command will do - DO NOT execute during /plan*

**Task Generation Strategy**:
- Register MCP resources (diagram types, recipes, schema) task
- Implement diagram_types resource with discovery metadata task
- Implement recipes resource with URI patterns task
- Implement recipe_schema resource task
- Create MCP tool registration task
- Generate tool discovery metadata task
- Implement create_recipe tool task
- Implement validate_recipe tool task
- Implement edit_recipe tool task
- Implement delete_recipe tool task
- Add system prompts for resource/tool discovery task
- Create integration tests for resources task
- Create integration tests for tools task
- Document MCP resources and tools usage task

**Ordering Strategy**:
1. Resource registration and URIs [P]
2. Resource implementations [P]
3. Tool registration and discovery setup [P]
4. Core CRUD tool operations [P]
5. Validation and error handling
6. Integration with existing models
7. System prompts and documentation
8. Testing and validation

**Estimated Output**: 25-30 numbered, ordered tasks in tasks.md

**IMPORTANT**: This phase is executed by the /tasks command, NOT by /plan

## Phase 3+: Future Implementation
*These phases are beyond the scope of the /plan command*

**Phase 3**: Task execution (/tasks command creates tasks.md)
**Phase 4**: Implementation (execute tasks.md following constitutional principles)
**Phase 5**: Validation (run tests, execute quickstart.md, performance validation)

## Complexity Tracking
*No constitutional violations identified - design follows simplicity principles*

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
- [x] Complexity deviations documented (none required)

---
*Based on Constitution template - See `/memory/constitution.md`*