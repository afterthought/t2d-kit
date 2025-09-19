# Claude Code Context: t2d-kit

## Project Overview

t2d-kit is a Multi-Framework Diagram Pipeline that transforms Product Requirements Documents (PRDs) into comprehensive diagrams and documentation using self-organizing Claude Code agents.

## Architecture

### Simplified Agent Architecture
- **No Orchestrator**: Agents self-organize based on "use proactively" instructions
- **Natural Delegation**: Claude automatically selects the right agent
- **File-Based Coordination**: Agents communicate through `.t2d-state/` directory
- **Complete Autonomy**: Each agent handles its entire workflow independently

### Core Components

1. **MCP Server** (`src/t2d_kit/mcp/`)
   - FastMCP-based server for recipe management
   - Tools: read_user_recipe, write_processed_recipe, validate_recipe, watch_recipe_changes
   - Integrates with Claude Desktop

2. **CLI** (`src/t2d_kit/cli/`)
   - Commands: setup, mcp, verify
   - Manages agent installation and environment setup

3. **Models** (`src/t2d_kit/models/`)
   - Pydantic v2 models with strict validation
   - T2DBaseModel base class with enhanced validation
   - UserRecipe, ProcessedRecipe, DiagramSpecification, etc.

4. **Agents** (`src/t2d_kit/agents/`)
   - 6 self-sufficient agents (transform, d2, mermaid, plantuml, docs, slides)
   - Each agent has complete lifecycle management
   - Activated by "use proactively" triggers

## Key Design Decisions

### Two-File Recipe System
- `recipe.yaml`: User-maintained, simple, high-level
- `recipe.t2d.yaml`: Agent-generated, detailed, executable
- Separation of user intent from implementation details

### Agent Invocation Patterns
```
User: "Transform my recipe"
→ t2d-transform agent activates automatically

User: "Generate all diagrams"
→ Multiple generator agents activate in parallel
```

### State Management
- File-based state in `.t2d-state/` directory
- JSON files for each processing stage
- Error recovery with backup files
- No complex in-memory state

## Development Patterns

### When Adding New Features
1. Update models in `enhanced-models.md` specification first
2. Implement model in `src/t2d_kit/models/`
3. Add MCP tool if needed
4. Update agent descriptions for proactive activation

### Testing Approach
- TDD: Write failing tests first
- Unit tests for models and tools
- Integration tests for workflows
- Performance tests for requirements (<200ms validation)

### Agent Development
Agents should:
- Be self-sufficient (complete workflow)
- Use "use proactively" in description
- Handle errors gracefully
- Report completion clearly

## File Organization

```
src/t2d_kit/
├── models/          # Data models (Pydantic)
│   ├── base.py     # T2DBaseModel
│   ├── user_recipe.py
│   ├── processed_recipe.py
│   └── ...
├── mcp/            # MCP server
│   └── server.py   # FastMCP tools
├── cli/            # CLI commands
│   ├── main.py
│   ├── setup.py
│   └── verify.py
└── agents/         # Claude Code agents
    ├── t2d-transform.md
    ├── t2d-d2-generator.md
    └── ...
```

## Performance Requirements
- Recipe validation: < 200ms
- Diagram generation: < 5s per diagram
- Support 10+ diagrams per recipe
- Parallel processing where possible

## Integration Points

### Claude Desktop
- MCP server runs in stdio mode
- Config in `claude_desktop_config.json`
- Agents installed to `~/.claude/agents/`

### External Tools
- **mise**: Manages tool versions (Python, Node, Go, Java)
- **D2**: Modern diagram renderer
- **Mermaid CLI (mmdc)**: Web-compatible diagrams
- **PlantUML**: Enterprise UML diagrams

## Common Workflows

### Recipe Transformation
1. User creates `recipe.yaml`
2. Transform agent reads and analyzes PRD
3. Generates detailed `recipe.t2d.yaml`
4. Creates state in `.t2d-state/processing.json`

### Diagram Generation
1. Generator agents read `recipe.t2d.yaml`
2. Filter for their framework (D2, Mermaid, PlantUML)
3. Generate source files and render assets
4. Update state files with completion

### Documentation Generation
1. Docs agent reads processed recipe
2. Gathers generated diagrams
3. Creates markdown with embedded diagrams
4. Integrates with existing MkDocs sites

## Error Handling

### State Recovery
- Backup files for critical state
- Partial recovery from corrupted JSON
- Clean state directory with `cleanup_old_states()`

### Agent Failures
- Continue processing other diagrams
- Report partial success
- Clear error messages in state files

## Best Practices

1. **Keep Agents Simple**: One responsibility per agent
2. **Use File State**: Don't pass complex objects
3. **Fail Gracefully**: Always try to produce partial output
4. **Natural Language**: Support conversational activation
5. **Validate Early**: Use Pydantic models for validation

## Testing the System

```bash
# Verify installation
t2d verify

# Run unit tests
pytest tests/unit/

# Run integration tests
pytest tests/integration/

# Run performance tests
pytest tests/performance/

# Full test suite with coverage
mise run test-cov
```

## Debugging Tips

1. Check `.t2d-state/` for processing status
2. Use `--verbose` flag for detailed output
3. Examine MCP server logs for tool errors
4. Verify agent activation with natural language tests

---

*This document provides context for Claude Code when working with the t2d-kit project.*