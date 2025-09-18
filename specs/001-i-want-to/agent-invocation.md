# Natural Language Agent Invocation

## Overview

The T2D Kit uses a simplified architecture that enables natural language agent invocation without requiring a central orchestrator. Each agent includes "use proactively" instructions in their descriptions, allowing them to self-activate when they detect relevant context or trigger phrases in user messages.

This approach eliminates the complexity of explicit orchestration while maintaining the intelligence and coordination needed for complex workflows. Agents communicate through shared state files and coordinate their activities based on file system changes and completion signals.

## Agent Activation Patterns

### 1. Direct Slash Commands

Agents can be invoked directly using their designated slash commands:

```
/t2d-transform recipe.yaml
/t2d-d2-generator
/t2d-mermaid-generator
/t2d-plantuml-generator
/t2d-docs-generator
/t2d-project-init
```

### 2. Natural Language Invocation

Agents activate automatically when they detect relevant phrases in natural language:

```
"Transform my recipe.yaml file"
"Process the recipe to generate diagrams"
"Generate D2 diagrams from recipe.t2d.yaml"
"Create documentation for my project"
"Initialize a new T2D project"
"Convert my system description to T2D format"
```

### 3. Proactive Activation

Agents self-activate when they detect relevant context in the conversation or file system:

- **t2d-transform** activates when user mentions recipe transformation or has a recipe.yaml file
- **t2d-d2-generator** activates when D2 diagrams need processing or recipe.t2d.yaml contains D2 specs
- **t2d-docs-generator** activates when documentation needs creation or generated assets are available
- **t2d-project-init** activates when user wants to start a new project or mentions initialization

## Agent Descriptions and Triggers

### Transform Agent (t2d-transform)

- **Slash Command**: `/t2d-transform`
- **Natural Language Triggers**:
  - "transform recipe"
  - "convert recipe"
  - "process recipe"
  - "turn recipe.yaml into T2D format"
  - "parse my system description"
- **Proactive Activation**:
  - When user has recipe.yaml and mentions transformation
  - When user asks about converting system descriptions
  - When workflow requires recipe.t2d.yaml generation
- **Required Tools**: File read/write, YAML parsing
- **Input**: recipe.yaml
- **Output**: recipe.t2d.yaml

### D2 Generator (t2d-d2-generator)

- **Slash Command**: `/t2d-d2-generator`
- **Natural Language Triggers**:
  - "generate D2 diagrams"
  - "process D2"
  - "create architecture diagrams"
  - "make D2 visuals"
  - "render D2 charts"
- **Proactive Activation**:
  - When recipe.t2d.yaml contains D2 diagram specifications
  - When user mentions D2 diagrams after transformation
  - When workflow requires diagram generation
- **Required Tools**: File operations, D2 CLI
- **Input**: recipe.t2d.yaml (D2 sections)
- **Output**: Generated .d2 files and rendered images

### Mermaid Generator (t2d-mermaid-generator)

- **Slash Command**: `/t2d-mermaid-generator`
- **Natural Language Triggers**:
  - "generate Mermaid diagrams"
  - "create Mermaid charts"
  - "process Mermaid"
  - "make flowcharts"
  - "render Mermaid visuals"
- **Proactive Activation**:
  - When recipe.t2d.yaml contains Mermaid specifications
  - When user requests flowcharts or sequence diagrams
  - When comprehensive diagram generation is requested
- **Required Tools**: File operations, Mermaid CLI
- **Input**: recipe.t2d.yaml (Mermaid sections)
- **Output**: Generated .mmd files and rendered images

### PlantUML Generator (t2d-plantuml-generator)

- **Slash Command**: `/t2d-plantuml-generator`
- **Natural Language Triggers**:
  - "generate PlantUML diagrams"
  - "create UML diagrams"
  - "process PlantUML"
  - "make class diagrams"
  - "render UML charts"
- **Proactive Activation**:
  - When recipe.t2d.yaml contains PlantUML specifications
  - When user needs formal UML diagrams
  - When technical documentation requires UML
- **Required Tools**: File operations, PlantUML
- **Input**: recipe.t2d.yaml (PlantUML sections)
- **Output**: Generated .puml files and rendered images

### Documentation Generator (t2d-docs-generator)

- **Slash Command**: `/t2d-docs-generator`
- **Natural Language Triggers**:
  - "generate documentation"
  - "create docs"
  - "build documentation"
  - "make README"
  - "document the project"
- **Proactive Activation**:
  - When generated diagrams and assets are available
  - When user requests comprehensive documentation
  - When project setup is complete and docs are needed
- **Required Tools**: File operations, template processing
- **Input**: recipe.t2d.yaml, generated assets
- **Output**: README.md, technical documentation

### Project Initialization Agent (t2d-project-init)

- **Slash Command**: `/t2d-project-init`
- **Natural Language Triggers**:
  - "initialize T2D project"
  - "start new project"
  - "set up T2D"
  - "create project structure"
  - "bootstrap T2D project"
- **Proactive Activation**:
  - When user mentions starting a new project
  - When no T2D structure exists and user wants to begin
  - When user needs project scaffolding
- **Required Tools**: File operations, directory creation
- **Input**: Project requirements, user preferences
- **Output**: Project structure, initial files, configuration

## Workflow Examples

### Example 1: Complete Pipeline

**User Input:**
```
"I have a recipe.yaml file that describes my system. Transform it and generate all the diagrams and documentation."
```

**System Response:**
1. **t2d-transform** agent activates → reads recipe.yaml, creates recipe.t2d.yaml
2. **t2d-d2-generator** agent activates → processes D2 diagram specs, generates .d2 files and images
3. **t2d-mermaid-generator** agent activates → processes Mermaid specs, generates .mmd files and images
4. **t2d-plantuml-generator** agent activates → processes PlantUML specs, generates .puml files and images
5. **t2d-docs-generator** agent activates → creates comprehensive documentation with all generated assets

### Example 2: Selective Processing

**User Input:**
```
"Just generate the D2 diagrams from my processed recipe"
```

**System Response:**
- **t2d-d2-generator** agent activates and processes only D2 specifications from recipe.t2d.yaml
- Other generators remain inactive since they weren't requested

### Example 3: Incremental Workflow

**User Input:**
```
"Transform my recipe first, then I'll decide what diagrams to generate"
```

**System Response:**
1. **t2d-transform** agent activates → creates recipe.t2d.yaml
2. System waits for user's next instruction about diagram generation
3. User can then request specific diagram types or all diagrams

### Example 4: New Project Setup

**User Input:**
```
"I want to start a new T2D project for my microservices architecture"
```

**System Response:**
1. **t2d-project-init** agent activates → creates project structure
2. Agent creates template recipe.yaml with microservices examples
3. User can then transform and generate as needed

## File-Based Coordination

Agents coordinate through the file system without direct communication:

### State Files in `.t2d-state/`

```
.t2d-state/
├── transform.status          # Transform completion status
├── d2-generator.status       # D2 generation status
├── mermaid-generator.status  # Mermaid generation status
├── plantuml-generator.status # PlantUML generation status
├── docs-generator.status     # Documentation generation status
└── workflow.json            # Overall workflow state
```

### State File Format

```json
{
  "agent": "t2d-transform",
  "status": "completed",
  "timestamp": "2024-01-15T10:30:00Z",
  "input_files": ["recipe.yaml"],
  "output_files": ["recipe.t2d.yaml"],
  "errors": [],
  "next_agents": ["t2d-d2-generator", "t2d-mermaid-generator"]
}
```

### Coordination Patterns

1. **Agents read state** to understand what work has been completed
2. **Agents write state** to signal their completion and suggest next steps
3. **Dependent agents** check for prerequisite completion before activating
4. **Parallel agents** can work simultaneously on independent tasks

## Parallel Processing

Multiple agents can work simultaneously when tasks are independent:

**User Input:**
```
"Generate all diagrams from recipe.t2d.yaml"
```

**System Response:**
```
t2d-d2-generator, t2d-mermaid-generator, and t2d-plantuml-generator
activate in parallel, each processing their respective sections
```

### Parallel Processing Benefits

- **Faster completion** for independent tasks
- **Efficient resource utilization**
- **Reduced wait times** for comprehensive workflows
- **Scalable processing** as more generators are added

### Coordination During Parallel Processing

- Each agent writes to separate state files
- Agents check for file locks to avoid conflicts
- Documentation generator waits for all diagram generators to complete
- Progress can be monitored through individual state files

## Best Practices

### 1. Clear Intent
Be specific about what you want to accomplish:
- ✅ "Generate D2 diagrams from my recipe"
- ❌ "Do something with my files"

### 2. Check State
Monitor progress through state files:
```bash
# Check overall progress
ls -la .t2d-state/

# View specific agent status
cat .t2d-state/transform.status
```

### 3. Incremental Work
Process in stages when appropriate:
```
1. "Transform my recipe first"
2. "Now generate just the architecture diagrams"
3. "Add the sequence diagrams"
4. "Finally create the documentation"
```

### 4. Error Recovery
Handle failures gracefully:
- Check error messages in state files
- Clear problematic state files to retry
- Use specific commands to resume from checkpoints

## Troubleshooting

### Agent Not Activating

**Symptoms:**
- No response to natural language triggers
- Expected agent doesn't start
- Silent failures

**Solutions:**
1. **Check trigger phrases** - ensure they match agent descriptions
2. **Verify required files exist** - agents need input files to process
3. **Ensure tools are available** - check CLI tools installation
4. **Use explicit slash commands** - bypass natural language detection

**Example:**
```
# If "generate D2 diagrams" doesn't work, try:
/t2d-d2-generator

# Or be more explicit:
"Use the t2d-d2-generator agent to process my recipe.t2d.yaml file"
```

### Multiple Agents Activating

**Symptoms:**
- Several agents start simultaneously
- Unexpected parallel processing
- Resource conflicts

**This is often desired behavior:**
- Parallel processing improves efficiency
- Multiple diagram types can generate simultaneously
- Comprehensive workflows benefit from parallel execution

**To limit activation:**
```
# Be specific about single agent
"Only generate D2 diagrams, not other diagram types"

# Use slash commands for precision
/t2d-d2-generator
```

### State Conflicts

**Symptoms:**
- Agents report conflicting status
- Incomplete process states
- Stale state information

**Solutions:**
1. **Clear state directory:**
   ```bash
   rm -rf .t2d-state/
   ```
2. **Check for incomplete processes:**
   ```bash
   # Look for partial outputs
   ls -la *.t2d.yaml *.d2 *.mmd *.puml
   ```
3. **Restart workflow:**
   ```
   "Start fresh with my recipe.yaml file"
   ```

### File Permission Issues

**Symptoms:**
- Agents cannot read/write files
- Permission denied errors
- State files not updating

**Solutions:**
1. **Check file permissions:**
   ```bash
   ls -la recipe.yaml recipe.t2d.yaml
   ```
2. **Fix permissions:**
   ```bash
   chmod 644 *.yaml
   chmod 755 .t2d-state/
   ```
3. **Verify write access:**
   ```bash
   touch .t2d-state/test.tmp && rm .t2d-state/test.tmp
   ```

## Integration with Claude Desktop

### MCP Server Integration

The T2D Kit integrates seamlessly with Claude Desktop through MCP servers:

- **MCP server provides file operations** - read, write, directory manipulation
- **Claude agents handle intelligence** - parsing, generation, coordination
- **Desktop Commander enables headless operation** - automated workflows

### Configuration

```json
{
  "mcpServers": {
    "t2d-kit": {
      "command": "node",
      "args": ["./mcp-server.js"],
      "cwd": "/path/to/t2d-kit"
    }
  }
}
```

### Workflow in Claude Desktop

1. **User opens Claude Desktop**
2. **MCP server connects** and provides T2D tools
3. **User types natural language request**
4. **Agents activate automatically** based on triggers
5. **MCP tools handle file operations**
6. **Results appear in conversation** with file links

### Headless Operation

```javascript
// Example headless workflow
const workflow = new T2DWorkflow();
await workflow.transform('recipe.yaml');
await workflow.generateAll();
await workflow.createDocs();
```

### Benefits of Claude Desktop Integration

- **Visual interface** for complex workflows
- **File drag-and-drop** for easy input
- **Real-time progress** updates in conversation
- **Rich media display** of generated diagrams
- **Integrated debugging** through conversation history

## Advanced Usage Patterns

### Conditional Workflows

```
"If my recipe has D2 specs, generate D2 diagrams, otherwise just create basic documentation"
```

### Template-Based Generation

```
"Generate diagrams using the microservices template from my recipe"
```

### Custom Agent Combinations

```
"Transform my recipe, generate only architecture diagrams, and create technical documentation"
```

### Batch Processing

```
"Process all recipe.yaml files in the current directory"
```

This comprehensive agent invocation system enables both simple and complex workflows while maintaining the flexibility and intelligence that makes T2D Kit powerful for system documentation and visualization.