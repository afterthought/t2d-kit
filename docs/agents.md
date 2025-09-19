# T2D Kit Agent Usage Guide

## Overview

The T2D Kit uses a **self-organizing agent architecture** that eliminates complex orchestration in favor of natural, intelligent delegation. Each agent is self-sufficient and handles complete workflows autonomously, coordinating through file-based state management rather than direct communication.

This architecture provides several key benefits:

- **Natural Language Activation**: Agents respond to conversational triggers automatically
- **Autonomous Execution**: Each agent completes entire workflows without manual coordination
- **File-Based Coordination**: Simple, reliable coordination through filesystem state
- **Parallel Processing**: Independent agents can work simultaneously for faster results
- **Resilient Operation**: Agent failures don't cascade or block other operations

## Core Architecture Principles

### Self-Organizing Agents
- **Proactive Activation**: Agents include "use proactively" instructions to auto-activate on relevant triggers
- **Complete Lifecycles**: Each agent handles end-to-end workflows from input to final output
- **Independent Operation**: No central orchestrator required
- **Smart Delegation**: Claude Code automatically selects appropriate agents based on context

### File-Based Coordination
Agents coordinate through the filesystem using several patterns:

```
.t2d-state/
├── transform.status          # Transform completion status
├── d2-generator.status       # D2 generation status
├── mermaid-generator.status  # Mermaid generation status
├── plantuml-generator.status # PlantUML generation status
├── docs-generator.status     # Documentation generation status
└── workflow.json            # Overall workflow state
```

Each state file contains standardized information:
```json
{
  "agent": "t2d-d2-generator",
  "status": "completed",
  "timestamp": "2024-01-15T10:30:00Z",
  "input_files": ["recipe.t2d.yaml"],
  "output_files": ["docs/assets/system.d2", "docs/assets/system.svg"],
  "errors": [],
  "next_agents": ["t2d-docs-generator"]
}
```

## Available Agents

The T2D Kit includes six specialized agents:

### 1. Transform Agent (`t2d-transform`)

**Purpose**: Converts user recipes into detailed processed recipes
**Input**: `recipe.yaml`
**Output**: `recipe.t2d.yaml`

**Activation Triggers**:
- "Transform my recipe.yaml"
- "Convert recipe to T2D format"
- "Process the recipe file"
- "Parse my system description"

**Complete Workflow**:
1. Reads and validates user recipe
2. Analyzes PRD content for components and relationships
3. Maps natural language requests to specific diagram types
4. Assigns optimal frameworks (D2, Mermaid, PlantUML)
5. Creates detailed specifications for generator agents
6. Writes complete processed recipe with generation notes

### 2. D2 Generator (`t2d-d2-generator`)

**Purpose**: Generates D2 diagrams and rendered assets
**Input**: `recipe.t2d.yaml` (D2 specifications)
**Output**: `.d2` files and rendered images (SVG, PNG)

**Activation Triggers**:
- "Generate D2 diagrams"
- "Create architecture diagrams"
- "Process D2 specifications"
- "Make D2 visuals"

**Complete Workflow**:
1. Reads processed recipe for D2 specifications
2. Generates syntactically correct D2 source code
3. Runs D2 CLI to build diagram assets
4. Handles multiple output formats automatically
5. Reports completion with file locations

**D2 Specializations**:
- System architecture diagrams
- Component relationships
- Network topologies
- Clear hierarchical layouts

### 3. Mermaid Generator (`t2d-mermaid-generator`)

**Purpose**: Generates Mermaid diagrams and rendered assets
**Input**: `recipe.t2d.yaml` (Mermaid specifications)
**Output**: `.mmd` files and rendered images

**Activation Triggers**:
- "Generate Mermaid diagrams"
- "Create flowcharts"
- "Make sequence diagrams"
- "Process Mermaid specifications"

**Complete Workflow**:
1. Reads processed recipe for Mermaid specifications
2. Creates appropriate Mermaid syntax for each diagram type
3. Runs Mermaid CLI (mmdc) to generate assets
4. Supports all major Mermaid diagram types
5. Reports completion and file locations

**Mermaid Specializations**:
- **Flowcharts**: Process flows and decision trees
- **Sequence Diagrams**: System interactions over time
- **ERD**: Database relationships and schemas
- **Gantt Charts**: Project timelines and dependencies
- **State Diagrams**: System state transitions

### 4. PlantUML Generator (`t2d-plantuml-generator`)

**Purpose**: Generates PlantUML diagrams for formal documentation
**Input**: `recipe.t2d.yaml` (PlantUML specifications)
**Output**: `.puml` files and rendered assets

**Activation Triggers**:
- "Generate PlantUML diagrams"
- "Create UML diagrams"
- "Make class diagrams"
- "Process PlantUML specifications"

**Complete Workflow**:
1. Reads processed recipe for PlantUML specifications
2. Creates formal UML syntax for technical diagrams
3. Runs PlantUML CLI to generate multiple formats
4. Handles SVG, PNG, and PDF output formats
5. Reports completion and validates outputs

**PlantUML Specializations**:
- **Class Diagrams**: Object-oriented design patterns
- **Component Diagrams**: System architecture components
- **Deployment Diagrams**: Infrastructure and environments
- **Activity Diagrams**: Business process flows
- **Use Case Diagrams**: Functional requirements

### 5. Documentation Generator (`t2d-docs-generator`)

**Purpose**: Creates comprehensive markdown documentation
**Input**: `recipe.t2d.yaml` and generated diagram assets
**Output**: README.md, technical documentation, MkDocs sites

**Activation Triggers**:
- "Generate documentation"
- "Create docs from recipe"
- "Build documentation site"
- "Document the project"

**Complete Workflow**:
1. Reads processed recipe specifications
2. Discovers and catalogs generated diagram files
3. Creates structured markdown with embedded diagrams
4. Builds MkDocs sites when configured
5. Reports documentation locations and access URLs

**Documentation Features**:
- Contextual diagram embedding
- Proper markdown structure and navigation
- Accessibility considerations (alt-text)
- Multiple output formats (standalone, MkDocs)

### 6. Presentation Generator (`t2d-slides-generator`)

**Purpose**: Creates slide presentations using Marp
**Input**: `recipe.t2d.yaml` and diagram assets
**Output**: Marp markdown, HTML, PDF, PowerPoint presentations

**Activation Triggers**:
- "Generate presentation"
- "Create slides from recipe"
- "Make presentation"
- "Build slide deck"

**Complete Workflow**:
1. Reads presentation specifications from recipe
2. Gathers and optimizes diagrams for slides
3. Creates Marp-formatted markdown with proper layouts
4. Exports to multiple presentation formats
5. Reports presentation files and access information

## Natural Language Invocation Examples

### Single Agent Activation

```
"Transform my recipe.yaml file"
→ Activates t2d-transform agent only

"Generate D2 diagrams from my processed recipe"
→ Activates t2d-d2-generator agent only

"Create documentation for my project"
→ Activates t2d-docs-generator agent only
```

### Multi-Agent Workflows

```
"Process my recipe and generate all diagrams"
→ Activates t2d-transform, then parallel diagram generators

"Transform recipe.yaml and create complete documentation"
→ Activates full pipeline: transform → generators → docs

"Generate diagrams and presentations from my recipe"
→ Activates generators and presentation agent
```

### Conditional Processing

```
"If my recipe has D2 specs, generate those diagrams"
→ Smart activation based on recipe contents

"Generate only architecture diagrams, skip flowcharts"
→ Selective agent activation based on requirements

"Create documentation with all available diagrams"
→ Documentation agent waits for diagram completion
```

## File-Based Coordination Patterns

### State Management

Agents coordinate through standardized state files that track:

- **Status**: pending, in_progress, completed, failed
- **Timestamps**: Start and completion times
- **Input/Output Files**: What was processed and generated
- **Dependencies**: What agents should run next
- **Errors**: Any issues encountered during processing

### Dependency Resolution

Agents automatically resolve dependencies through state checking:

```python
# Simplified dependency logic
def can_start(agent_name, required_agents):
    for required_agent in required_agents:
        state = read_state(f"{required_agent}.status")
        if not state or state["status"] != "completed":
            return False
    return True
```

### Parallel Execution

Independent agents can run simultaneously:

```
User: "Generate all diagrams from recipe.t2d.yaml"

System Response:
├─ t2d-d2-generator (starts immediately)
├─ t2d-mermaid-generator (starts immediately)
└─ t2d-plantuml-generator (starts immediately)

All agents process their specifications in parallel
```

### Progress Monitoring

Track progress through state file timestamps:

```bash
# Check overall progress
ls -la .t2d-state/

# View specific agent status
cat .t2d-state/transform.status

# Monitor active agents
find .t2d-state -name "*.status" -exec grep -l "in_progress" {} \;
```

## Troubleshooting Common Issues

### Agent Not Activating

**Symptoms**:
- No response to natural language triggers
- Expected agent doesn't start working
- Silent failures without error messages

**Diagnostic Steps**:
1. **Check trigger phrases** - ensure they match documented patterns
2. **Verify input files** - agents need proper input files to activate
3. **Confirm tool availability** - check CLI tools are installed
4. **Review context** - ensure sufficient context for agent recognition

**Solutions**:

```bash
# Use explicit slash commands to bypass natural language detection
/t2d-transform recipe.yaml
/t2d-d2-generator

# Be more explicit in requests
"Use the t2d-d2-generator agent to process my recipe.t2d.yaml file"

# Check for missing dependencies
which d2 mmdc java  # Verify CLI tools are available
```

### Multiple Agents Activating Unexpectedly

**Symptoms**:
- Several agents start simultaneously when only one was expected
- Resource conflicts from parallel processing
- Overwhelmed system resources

**Understanding the Behavior**:
This is often **desired behavior** for efficiency:
- Parallel processing improves overall completion time
- Multiple diagram types can generate simultaneously
- Comprehensive workflows benefit from parallel execution

**Controlling Activation**:

```bash
# Request specific single agent
"Only generate D2 diagrams, not other diagram types"

# Use precise slash commands
/t2d-d2-generator

# Specify incremental workflow
"Transform my recipe first, then I'll decide what diagrams to generate"
```

### State File Conflicts

**Symptoms**:
- Agents report conflicting status information
- Incomplete or corrupted state data
- Stale state preventing new operations

**Diagnostic Steps**:

```bash
# Check state directory contents
ls -la .t2d-state/

# Look for partial or corrupted files
find .t2d-state -name "*.json" -exec cat {} \;

# Check for incomplete processes
ps aux | grep -E "(d2|mmdc|plantuml|mkdocs)"
```

**Recovery Solutions**:

```bash
# Clear all state (nuclear option)
rm -rf .t2d-state/

# Selective state cleanup
rm .t2d-state/problematic-agent.status

# Check and fix file permissions
chmod 755 .t2d-state/
chmod 644 .t2d-state/*.json
```

### File Permission Issues

**Symptoms**:
- "Permission denied" errors in agent logs
- Agents cannot read input files
- State files not updating properly

**Diagnostic Steps**:

```bash
# Check file permissions
ls -la recipe.yaml recipe.t2d.yaml
ls -la .t2d-state/

# Test write access
touch .t2d-state/test.tmp && rm .t2d-state/test.tmp
```

**Solutions**:

```bash
# Fix recipe file permissions
chmod 644 *.yaml

# Fix state directory permissions
chmod 755 .t2d-state/
chmod 644 .t2d-state/*.json

# Check ownership issues
chown $USER:$USER recipe.yaml .t2d-state/
```

### CLI Tool Dependencies

**Symptoms**:
- Diagram generation fails with "command not found"
- Partially generated assets
- Tool-specific error messages

**Required Tools**:
- **D2**: `brew install d2` or download from terrastruct.com
- **Mermaid**: `npm install -g @mermaid-js/mermaid-cli`
- **PlantUML**: Java + plantuml.jar
- **MkDocs**: `pip install mkdocs`
- **Marp**: `npm install -g @marp-team/marp-cli`

**Verification**:

```bash
# Check tool availability
which d2 mmdc java mkdocs marp

# Test basic functionality
d2 --version
mmdc --version
java -jar plantuml.jar -version
mkdocs --version
marp --version
```

### Recipe Format Issues

**Symptoms**:
- Transform agent fails to process recipe.yaml
- Invalid or incomplete recipe.t2d.yaml generation
- Agents cannot find expected specifications

**Common Issues**:
1. **YAML syntax errors**: Invalid indentation or structure
2. **Missing required fields**: Incomplete recipe specifications
3. **Invalid PRD references**: Broken file paths or URLs
4. **Specification mismatches**: Inconsistent diagram requests

**Solutions**:

```bash
# Validate YAML syntax
python -c "import yaml; print(yaml.safe_load(open('recipe.yaml')))"

# Check recipe structure against examples
cat recipe.yaml | head -20

# Verify PRD file accessibility
ls -la $(grep prd_path recipe.yaml | cut -d: -f2 | tr -d ' ')
```

### Network and Resource Issues

**Symptoms**:
- Slow agent processing
- Timeout errors during diagram generation
- Memory issues with large diagrams

**Optimization Strategies**:

```bash
# Monitor resource usage
top -p $(pgrep -f "d2\|mmdc\|java.*plantuml")

# Process diagrams in smaller batches
"Generate just the architecture diagrams first"
"Now generate the sequence diagrams"

# Check available disk space
df -h .
```

## Advanced Usage Patterns

### Incremental Workflows

Process complex projects in manageable stages:

```bash
# Stage 1: Transform and validate
"Transform my recipe.yaml and verify the specifications"

# Stage 2: Generate core diagrams
"Generate the architecture and system diagrams"

# Stage 3: Add detailed flows
"Now generate the sequence and state diagrams"

# Stage 4: Create deliverables
"Generate documentation and presentations with all diagrams"
```

### Template-Based Processing

Use consistent patterns across projects:

```bash
# Use organizational templates
"Generate diagrams using our microservices template"

# Apply consistent styling
"Create diagrams with the corporate color scheme"

# Follow documentation standards
"Generate documentation following our technical writing guidelines"
```

### Batch Processing

Handle multiple recipes or projects:

```bash
# Process multiple recipes
"Transform all recipe.yaml files in the current directory"

# Generate specific diagram types across projects
"Generate all D2 architecture diagrams in this workspace"

# Create consolidated documentation
"Build a documentation site from all processed recipes"
```

### Integration with Development Workflows

Embed T2D Kit into development processes:

```bash
# CI/CD integration
"Transform recipe and generate diagrams for the current branch"

# Documentation updates
"Regenerate documentation when PRD files change"

# Release documentation
"Create release presentation with current architecture diagrams"
```

## Integration with Claude Desktop

### MCP Server Configuration

The T2D Kit integrates with Claude Desktop through MCP servers:

```json
{
  "mcpServers": {
    "t2d-kit": {
      "command": "python",
      "args": ["-m", "t2d_kit.mcp.server"],
      "cwd": "/path/to/t2d-kit"
    }
  }
}
```

### Desktop Workflow

1. **Natural Conversation**: Type requests in natural language
2. **Automatic Delegation**: Claude Desktop activates appropriate agents
3. **Real-time Updates**: Progress shown in conversation
4. **Rich Media**: Generated diagrams displayed inline
5. **File Links**: Direct access to generated assets

### Headless Operation

For automated workflows:

```python
from t2d_kit import T2DWorkflow

# Programmatic workflow
workflow = T2DWorkflow()
await workflow.transform('recipe.yaml')
await workflow.generate_all()
await workflow.create_docs()
```

## Best Practices

### Clear Intent Communication

Be specific about desired outcomes:

```bash
# ✅ Good: Specific and actionable
"Generate D2 diagrams from my recipe for system architecture"

# ❌ Poor: Vague and ambiguous
"Do something with my files"
```

### Progress Monitoring

Track workflow progress actively:

```bash
# Check overall status
ls -la .t2d-state/

# Monitor specific agents
tail -f .t2d-state/d2-generator.status

# Verify outputs
find . -name "*.svg" -o -name "*.png" | head -10
```

### Error Recovery

Handle failures gracefully:

```bash
# Check for errors
grep -l "error\|failed" .t2d-state/*.status

# Restart from checkpoint
"Continue processing from where the D2 generator left off"

# Selective retry
"Regenerate only the failed architecture diagram"
```

### Resource Management

Optimize for available resources:

```bash
# Process large recipes incrementally
"Transform recipe first, then generate diagrams in batches"

# Monitor system resources
"Generate diagrams one framework at a time to avoid memory issues"

# Clean up intermediate files
"Remove generated assets older than 7 days"
```

This comprehensive guide provides the foundation for effectively using the T2D Kit's self-organizing agent architecture. The combination of natural language activation, autonomous execution, and file-based coordination creates a powerful yet intuitive system for transforming system descriptions into rich documentation and visualizations.