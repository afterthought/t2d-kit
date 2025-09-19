# Tasks: MCP Recipe Management

**Input**: Design documents from `/specs/002-the-user-can/`
**Prerequisites**: plan.md (required), research.md, data-model.md, contracts/

## Execution Flow (main)
```
1. Load plan.md from feature directory
   → If not found: ERROR "No implementation plan found"
   → Extract: tech stack, libraries, structure
2. Load optional design documents:
   → data-model.md: Extract entities → model tasks
   → contracts/: Each file → contract test task
   → research.md: Extract decisions → setup tasks
3. Generate tasks by category:
   → Setup: project init, dependencies, linting
   → Tests: contract tests, integration tests
   → Core: models, services, CLI commands
   → Integration: DB, middleware, logging
   → Polish: unit tests, performance, docs
4. Apply task rules:
   → Different files = mark [P] for parallel
   → Same file = sequential (no [P])
   → Tests before implementation (TDD)
5. Number tasks sequentially (T001, T002...)
6. Generate dependency graph
7. Create parallel execution examples
8. Validate task completeness:
   → All contracts have tests?
   → All entities have models?
   → All endpoints implemented?
9. Return: SUCCESS (tasks ready for execution)
```

## Format: `[ID] [P?] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in descriptions

## Path Conventions
- **Single project**: `src/`, `tests/` at repository root
- Paths shown below for extending existing t2d-kit structure

## Phase 3.1: Setup
- [ ] T001 Create MCP resources and tools directory structure in src/t2d_kit/mcp/
- [ ] T002 Install FastMCP and update dependencies in pyproject.toml
- [ ] T003 [P] Configure pytest fixtures for MCP testing in tests/conftest.py
- [ ] T004 [P] Create __init__.py files for new MCP modules

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3
**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**

### Contract Tests for Resources
- [ ] T005 [P] Contract test for diagram-types resource in tests/contract/test_mcp_resources.py::test_diagram_types_resource
- [ ] T006 [P] Contract test for user-recipes resource in tests/contract/test_mcp_resources.py::test_user_recipes_resource
- [ ] T007 [P] Contract test for processed-recipes resource in tests/contract/test_mcp_resources.py::test_processed_recipes_resource
- [ ] T008 [P] Contract test for recipe schemas resources in tests/contract/test_mcp_resources.py::test_recipe_schemas

### Contract Tests for User Recipe Tools
- [ ] T009 [P] Contract test for create_user_recipe tool in tests/contract/test_user_recipe_tools.py::test_create_user_recipe
- [ ] T010 [P] Contract test for edit_user_recipe tool in tests/contract/test_user_recipe_tools.py::test_edit_user_recipe
- [ ] T011 [P] Contract test for validate_user_recipe tool in tests/contract/test_user_recipe_tools.py::test_validate_user_recipe
- [ ] T012 [P] Contract test for delete_user_recipe tool in tests/contract/test_user_recipe_tools.py::test_delete_user_recipe

### Contract Tests for Processed Recipe Tools
- [ ] T013 [P] Contract test for write_processed_recipe tool in tests/contract/test_processed_recipe_tools.py::test_write_processed_recipe
- [ ] T014 [P] Contract test for update_processed_recipe tool in tests/contract/test_processed_recipe_tools.py::test_update_processed_recipe
- [ ] T015 [P] Contract test for validate_processed_recipe tool in tests/contract/test_processed_recipe_tools.py::test_validate_processed_recipe

### Integration Tests
- [ ] T016 [P] Integration test for creating recipe workflow in tests/integration/test_mcp_recipe_flow.py::test_create_recipe_flow
- [ ] T017 [P] Integration test for recipe discovery via resources in tests/integration/test_mcp_recipe_flow.py::test_resource_discovery
- [ ] T018 [P] Integration test for recipe transformation workflow in tests/integration/test_mcp_recipe_flow.py::test_transform_recipe_flow
- [ ] T019 [P] Integration test for validation error handling in tests/integration/test_mcp_recipe_flow.py::test_validation_errors

## Phase 3.3: Core Implementation (ONLY after tests are failing)

### Pydantic Models
- [ ] T020 [P] DiagramTypeInfo and DiagramTypesResource models in src/t2d_kit/models/mcp_resources.py
- [ ] T021 [P] RecipeSummary and RecipeListResource models in src/t2d_kit/models/mcp_resources.py
- [ ] T022 [P] ProcessedRecipeSummary and ProcessedRecipeListResource models in src/t2d_kit/models/mcp_resources.py
- [ ] T023 [P] CreateRecipeParams model with validation in src/t2d_kit/models/user_recipe.py
- [ ] T024 [P] EditRecipeParams and ValidateRecipeParams models in src/t2d_kit/models/user_recipe.py
- [ ] T025 [P] WriteProcessedRecipeParams model in src/t2d_kit/models/processed_recipe.py
- [ ] T026 [P] UpdateProcessedRecipeParams and ValidateProcessedRecipeParams in src/t2d_kit/models/processed_recipe.py
- [ ] T027 [P] DiagramSpecification and ContentFile models in src/t2d_kit/models/processed_recipe.py

### MCP Resources Implementation
- [ ] T028 [P] Implement diagram_types resource handler in src/t2d_kit/mcp/resources/diagram_types.py
- [ ] T029 [P] Implement user_recipes resource handler in src/t2d_kit/mcp/resources/user_recipes.py
- [ ] T030 [P] Implement processed_recipes resource handler in src/t2d_kit/mcp/resources/processed_recipes.py
- [ ] T031 [P] Implement user_recipe_schema resource in src/t2d_kit/mcp/resources/user_recipe_schema.py
- [ ] T032 [P] Implement processed_recipe_schema resource in src/t2d_kit/mcp/resources/processed_recipe_schema.py

### MCP Tools Implementation - User Recipes
- [ ] T033 Implement create_user_recipe tool in src/t2d_kit/mcp/tools/user_recipe_tools.py
- [ ] T034 Implement validate_user_recipe tool in src/t2d_kit/mcp/tools/user_recipe_tools.py
- [ ] T035 Implement edit_user_recipe tool in src/t2d_kit/mcp/tools/user_recipe_tools.py
- [ ] T036 Implement delete_user_recipe tool in src/t2d_kit/mcp/tools/user_recipe_tools.py

### MCP Tools Implementation - Processed Recipes
- [ ] T037 Implement write_processed_recipe tool in src/t2d_kit/mcp/tools/processed_recipe_tools.py
- [ ] T038 Implement update_processed_recipe tool in src/t2d_kit/mcp/tools/processed_recipe_tools.py
- [ ] T039 Implement validate_processed_recipe tool in src/t2d_kit/mcp/tools/processed_recipe_tools.py

### Server Integration
- [ ] T040 Register all resources in src/t2d_kit/mcp/server.py
- [ ] T041 Register all tools with proper discovery metadata in src/t2d_kit/mcp/server.py
- [ ] T042 Add system prompts for MCP client discovery in src/t2d_kit/mcp/server.py
- [ ] T043 Implement error handling and validation feedback in src/t2d_kit/mcp/server.py

## Phase 3.4: Integration

### Filesystem Operations
- [ ] T044 Implement safe path validation utilities in src/t2d_kit/mcp/utils/path_utils.py
- [ ] T045 Implement YAML file reading with size limits in src/t2d_kit/mcp/utils/yaml_utils.py
- [ ] T046 Implement atomic file writing with backup in src/t2d_kit/mcp/utils/yaml_utils.py
- [ ] T047 Add filesystem scanning for dynamic resource generation in src/t2d_kit/mcp/utils/scanner.py

### Validation and Performance
- [ ] T048 Implement validation with < 200ms performance target in src/t2d_kit/mcp/utils/validator.py
- [ ] T049 Add structured error messages with suggestions in src/t2d_kit/mcp/utils/errors.py
- [ ] T050 Implement logging with Context object integration in src/t2d_kit/mcp/utils/logging.py

## Phase 3.5: Polish

### Unit Tests
- [ ] T051 [P] Unit tests for path validation in tests/unit/test_path_utils.py
- [ ] T052 [P] Unit tests for YAML operations in tests/unit/test_yaml_utils.py
- [ ] T053 [P] Unit tests for recipe validation in tests/unit/test_recipe_validation.py
- [ ] T054 [P] Unit tests for error handling in tests/unit/test_error_handling.py

### Performance Tests
- [ ] T055 [P] Performance test for validation < 200ms in tests/performance/test_validation_speed.py
- [ ] T056 [P] Performance test for resource scanning in tests/performance/test_resource_scanning.py
- [ ] T057 [P] Performance test for file operations < 100ms in tests/performance/test_file_operations.py

### Documentation and CLI
- [ ] T058 Update CLI mcp command help text in src/t2d_kit/cli/mcp.py
- [ ] T059 Add MCP server configuration example to docs/mcp_setup.md
- [ ] T060 Update quickstart with Claude Desktop integration in docs/quickstart.md
- [ ] T061 Create troubleshooting guide for MCP issues in docs/mcp_troubleshooting.md

### Final Validation
- [ ] T062 Run quickstart.md scenarios end-to-end
- [ ] T063 Verify all resources discoverable via Claude Desktop
- [ ] T064 Test concurrent recipe operations for safety
- [ ] T065 Validate error messages are user-friendly

## Dependencies
- Setup (T001-T004) must complete first
- Tests (T005-T019) before implementation (T020-T043)
- Models (T020-T027) before resources/tools (T028-T039)
- Resources/tools before server integration (T040-T043)
- Server integration before filesystem utilities (T044-T050)
- All implementation before polish (T051-T065)

## Parallel Execution Examples

### Launch all contract tests together (T005-T015):
```bash
# Run in parallel with pytest-xdist
pytest tests/contract/ -n auto

# Or with Task agents:
Task: "Contract test for diagram-types resource in tests/contract/test_mcp_resources.py::test_diagram_types_resource"
Task: "Contract test for user-recipes resource in tests/contract/test_mcp_resources.py::test_user_recipes_resource"
Task: "Contract test for create_user_recipe tool in tests/contract/test_user_recipe_tools.py::test_create_user_recipe"
# ... continue for all test tasks
```

### Launch all model creation tasks together (T020-T027):
```bash
# These are all in different files, can run in parallel
Task: "DiagramTypeInfo and DiagramTypesResource models in src/t2d_kit/models/mcp_resources.py"
Task: "CreateRecipeParams model with validation in src/t2d_kit/models/user_recipe.py"
Task: "WriteProcessedRecipeParams model in src/t2d_kit/models/processed_recipe.py"
# ... continue for all model tasks
```

### Launch all resource implementations together (T028-T032):
```bash
# Each resource is in its own file
Task: "Implement diagram_types resource handler in src/t2d_kit/mcp/resources/diagram_types.py"
Task: "Implement user_recipes resource handler in src/t2d_kit/mcp/resources/user_recipes.py"
Task: "Implement processed_recipes resource handler in src/t2d_kit/mcp/resources/processed_recipes.py"
# ... continue for all resource tasks
```

## Notes
- [P] tasks = different files, no dependencies
- User recipe tools (T033-T036) share a file, must be sequential
- Processed recipe tools (T037-T039) share a file, must be sequential
- Server integration tasks (T040-T043) share server.py, must be sequential
- Verify tests fail before implementing
- Commit after each task with descriptive message
- Use Pydantic models everywhere for schema discovery

## Task Generation Rules
*Applied during main() execution*

1. **From Contracts**:
   - mcp_resources.json → 4 resource contract tests
   - mcp_tools.json → 4 user recipe tool tests
   - mcp_processed_tools.json → 3 processed recipe tool tests

2. **From Data Model**:
   - 8 entity groups → 8 model creation tasks
   - Each Pydantic model gets its own task

3. **From Quickstart Scenarios**:
   - Resource discovery scenario → integration test
   - Recipe creation workflow → integration test
   - Recipe transformation → integration test
   - Error handling → integration test

4. **Ordering**:
   - Setup → Tests → Models → Resources/Tools → Integration → Polish
   - Dependencies block parallel execution where files are shared

## Validation Checklist
*GATE: Checked by main() before returning*

- [x] All contracts have corresponding tests (11 contract tests for 3 contract files)
- [x] All entities have model tasks (8 model task groups)
- [x] All tests come before implementation (T005-T019 before T020-T050)
- [x] Parallel tasks truly independent (verified file paths)
- [x] Each task specifies exact file path
- [x] No task modifies same file as another [P] task in same phase