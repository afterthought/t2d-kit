# Research: MCP Resources and Tools for Recipe Management

**Date**: 2025-09-18
**Feature**: User Recipe File Management
**Branch**: 002-the-user-can

## Research Findings

### 1. MCP Resource vs Tool Distinction

**Decision**: Use Resources for read-only data discovery, Tools for write operations
**Rationale**:
- Resources are designed for exposing discoverable, read-only data with URIs
- Tools are for operations that modify state or perform actions
- This separation follows MCP protocol design principles

**Alternatives considered**:
- All functionality as tools: Rejected - loses discoverability benefits
- All functionality as resources: Rejected - resources are read-only by design
- Mixed approach: Selected - best matches MCP protocol intent

### 2. FastMCP Resource Registration Patterns

**Decision**: Use URI-based resource registration with dynamic content generation
**Rationale**:
- FastMCP supports `@mcp.resource()` decorator with URI templates
- URIs provide hierarchical navigation (e.g., `recipes://`, `recipes://example`)
- Dynamic generation allows real-time filesystem scanning

**Alternatives considered**:
- Static resource lists: Rejected - doesn't reflect filesystem changes
- Database-backed resources: Rejected - adds unnecessary complexity
- Filesystem scanning: Selected - matches existing architecture

### 3. MCP Resource Discovery Metadata

**Decision**: Rich metadata with descriptions, mime types, and examples
**Rationale**:
- Metadata helps MCP clients understand resource purpose
- Examples in metadata improve discoverability
- Mime types enable proper content handling

**Implementation approach**:
```python
@mcp.resource("diagram-types://")
async def list_diagram_types():
    return Resource(
        uri="diagram-types://",
        name="Available Diagram Types",
        description="List of all supported diagram types with examples",
        mimeType="application/json",
        metadata={
            "examples": ["flowchart", "sequence", "erd"],
            "total_count": 30
        }
    )
```

### 4. Dynamic Resource Generation from Filesystem

**Decision**: Scan recipe directory on each resource request
**Rationale**:
- Ensures resources always reflect current filesystem state
- No caching complexity or staleness issues
- Performance acceptable for expected recipe counts (<1000)

**Alternatives considered**:
- File watching with cache: Rejected - adds complexity
- Static registration: Rejected - doesn't handle new files
- On-demand scanning: Selected - simple and reliable

### 5. MCP Tool Discovery System Prompts

**Decision**: Embed discovery hints in tool descriptions and server info
**Rationale**:
- System prompts in server info help clients understand capabilities
- Tool descriptions with examples improve discoverability
- Structured metadata enables better client integration

**Implementation approach**:
```python
@mcp.tool(
    name="create_recipe",
    description="Create a new recipe file with validation. Use this to start a new t2d-kit recipe for diagram generation.",
    parameters={
        "name": "Recipe name (will be used as filename)",
        "prd_content": "Product requirements document content",
        "diagrams": "List of diagram specifications"
    }
)
```

### 6. YAML Validation with Pydantic

**Decision**: Use Pydantic models for YAML validation with FastMCP
**Rationale**:
- Pydantic provides robust validation with clear error messages
- Already used in t2d-kit for model definitions
- FastMCP has built-in Pydantic support

**Implementation approach**:
```python
from pydantic import BaseModel, Field, validator

class UserRecipe(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    prd: PRDContent
    instructions: UserInstructions

    @validator('name')
    def validate_name_format(cls, v):
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9_-]*$', v):
            raise ValueError('Invalid name format')
        return v
```

### 7. File System Safety Patterns

**Decision**: Restricted operations with path validation
**Rationale**:
- Prevent path traversal attacks
- Limit operations to designated recipe directory
- Validate all paths before operations

**Safety measures**:
- Use `pathlib.Path.resolve()` to prevent traversal
- Check paths are within allowed directory
- Validate filenames against pattern
- Set maximum file size (1MB)

### 8. MCP Error Handling and Feedback

**Decision**: Structured error responses with actionable messages
**Rationale**:
- MCP supports error codes and messages
- Structured errors help clients handle failures
- User-friendly messages improve experience

**Error categories**:
- Validation errors: Include field-specific messages
- File system errors: Safe, sanitized messages
- Permission errors: Clear access requirements
- Size limit errors: Include limits and current size

## System Prompt Strategy

**Decision**: Multi-level discovery approach
**Components**:

1. **Server-level prompt** (in server initialization):
```python
server = FastMCP(
    "t2d-kit Recipe Manager",
    description="""
    MCP server for t2d-kit recipe management.

    Resources:
    - diagram-types:// - Discover available diagram types
    - recipes:// - Browse existing recipes
    - recipe-schema:// - Get recipe YAML schema

    Tools:
    - create_recipe - Create new recipe files
    - edit_recipe - Modify existing recipes
    - validate_recipe - Check recipe validity
    - delete_recipe - Remove recipe files
    """
)
```

2. **Resource-level metadata**:
- Clear names and descriptions
- Example URIs in metadata
- Expected response format documentation

3. **Tool-level hints**:
- Action-oriented descriptions
- Parameter explanations with examples
- Success/error response examples

## Performance Considerations

**Validation performance target**: < 200ms
- Achieved through Pydantic's optimized validation
- No external API calls during validation
- File operations are the main bottleneck

**File operation target**: < 100ms
- Direct filesystem operations without intermediaries
- Async I/O where beneficial
- Batch operations when possible

## Security Considerations

1. **Path validation**: All paths validated and sandboxed
2. **File size limits**: 1MB maximum enforced
3. **YAML safe loading**: Use `yaml.safe_load()` only
4. **No code execution**: Pure data validation only
5. **Resource isolation**: Each operation is isolated

## Implementation Priority

1. **Core resources first**: Enable discovery
2. **Validation tool**: Critical for user experience
3. **Create tool**: Primary user action
4. **Edit/delete tools**: Complete CRUD operations
5. **System prompts**: Polish discovery experience

## Conclusion

All technical unknowns have been resolved through research. The approach uses:
- MCP resources for discovery and read-only data
- MCP tools for write operations
- FastMCP framework for implementation
- Pydantic for validation
- System prompts at multiple levels for discoverability

No remaining NEEDS CLARIFICATION items.