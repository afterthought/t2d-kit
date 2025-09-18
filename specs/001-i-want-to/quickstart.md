# Quickstart Guide: t2d-kit

**Intelligent Documentation Generator**
*Transform requirements into beautiful diagrams and documentation using self-organizing agents*

## Installation

### Step 1: Install and Setup
```bash
# Install with uv package manager
uvx install t2d-kit

# Setup intelligent agents
t2d setup

# Output:
# ✅ t2d-kit setup complete!
#    Self-organizing agents installed to: ~/.claude/agents
#
# 🤖 Intelligent agents ready:
#    - Transform Agent: Converts simple recipes to detailed specs
#    - Diagram Agents: Generate D2, Mermaid, PlantUML diagrams
#    - Content Agents: Create documentation and presentations
#    - All agents self-activate based on "use proactively" instructions
```

### Step 2: Connect to Your Existing MkDocs Site
```bash
# t2d-kit integrates with your existing documentation site
cd your-existing-docs-project

# Start MCP server in your docs directory
t2d mcp .

# Add to Claude Desktop MCP settings:
{
  "mcpServers": {
    "t2d-kit": {
      "command": "t2d",
      "args": ["mcp", "."]
    }
  }
}

# The MCP server provides:
# - Recipe management within your existing project
# - Integration with existing MkDocs navigation
# - File-based state persistence for agents
# - Asset management in your docs/assets directory
```

### Step 3: Verify Installation
```bash
# Check all components and agent readiness
t2d verify

# ✓ Claude Code found
# ✓ Intelligent agents installed and configured
# ✓ Agent self-activation enabled
# ✓ mise dependency manager available
# ✓ D2 diagram tool ready
# ✓ Mermaid CLI ready
# ✓ MCP server functional
# ✓ File-based state management working
```

## Prerequisites

### Automatic Setup with mise

t2d-kit uses mise (mise-en-place) to automatically manage all tool dependencies:

```bash
# Install mise if not already present
curl https://mise.run | sh

# Clone the project and let mise handle dependencies
cd t2d-kit
mise install  # Installs all tools defined in .mise.toml

# Tools installed by mise:
# - Python 3.11+
# - Node.js 20+ (for Mermaid CLI)
# - Go 1.21+ (for D2)
# - Java 17+ (for PlantUML)
# - D2 CLI (via Go)
# - Mermaid CLI (via npm)
```

The `.mise.toml` configuration:
```toml
[tools]
python = "3.11"
node = "20"
go = "1.21"
java = "17"
"npm:@mermaid-js/mermaid-cli" = "latest"  # Installs mmdc
"go:oss.terrastruct.com/d2" = "latest"     # Installs d2

[tasks.setup-plantuml]
description = "Download PlantUML jar"
run = "curl -L https://github.com/plantuml/plantuml/releases/latest/download/plantuml.jar -o ~/.local/share/plantuml/plantuml.jar"
```

### Manual Installation (Alternative)

If you prefer manual installation:

```bash
# Install Go (for D2)
# macOS: brew install go
# Linux: sudo apt install golang-go

# Install D2
go install oss.terrastruct.com/d2@latest

# Install Node.js and Mermaid CLI
# macOS: brew install node
# Linux: sudo apt install nodejs npm
npm install -g @mermaid-js/mermaid-cli

# Optional: PlantUML (requires Java)
# macOS: brew install openjdk plantuml
# Linux: sudo apt install default-jre plantuml
```

## Intelligent Workflow

### Natural Language Development

Simply tell Claude what you want - the agents self-organize to complete complex tasks:

```
# Complete workflow in natural language:
"Create technical documentation for my e-commerce platform with architecture diagrams and API docs"

# Claude's intelligent agents will:
# 1. Transform Agent creates recipe.yaml → recipe.t2d.yaml automatically
# 2. Diagram Agents generate appropriate diagrams (D2 for architecture, Mermaid for flows)
# 3. Content Agents write documentation pages
# 4. Integration with your existing MkDocs site
# 5. All state persisted in files for transparency

# Iterative improvements:
"Add a sequence diagram showing the payment flow and update the API documentation"

# Agents self-activate to:
# 1. Generate the sequence diagram
# 2. Update relevant documentation pages
# 3. Maintain consistency across all outputs
```

**No orchestrator needed** - agents are self-sufficient and coordinate through file-based state management.

## Quick Start Example

### 1. Create Your Simple Recipe

Create a `recipe.yaml` file with your requirements (user-maintained, simple format):

```yaml
recipe:
  name: "E-Commerce Platform"
  version: "1.0.0"

  # Your requirements (any format - PRD, user stories, etc.)
  requirements: |
    # E-Commerce Platform Requirements

    ## Overview
    Modern e-commerce platform with microservices architecture.
    Users can browse products, manage cart, and complete purchases.

    ## Key Features
    - User authentication and profiles
    - Product catalog with search
    - Shopping cart and checkout
    - Payment processing (Stripe)
    - Order tracking
    - Admin dashboard

    ## Tech Stack
    - React frontend with TypeScript
    - Node.js microservices (Auth, Products, Orders, Payments)
    - PostgreSQL for persistence
    - Redis for caching
    - Kubernetes deployment

  # Simple instructions for what you want generated
  want:
    diagrams:
      - "system architecture showing microservices"
      - "user flow from browse to purchase"
      - "database relationships"

    documentation:
      audience: "developers"
      style: "technical"
      include_api_docs: true

    integration:
      existing_site: true  # Integrate with existing MkDocs site
      assets_dir: "docs/assets"
      pages_dir: "docs/features"
```

### Alternative Requirements Sources

#### Option 2: Reference External Files
```yaml
recipe:
  name: "E-Commerce Platform"
  requirements:
    file_path: "docs/requirements/prd.md"
    format: markdown
  # ... rest of recipe
```

#### Option 3: Use Existing PRD Documents
When you have requirements in external systems, just tell Claude:

```
"Create diagrams and documentation for my e-commerce platform.
First fetch the PRD document with UUID abc-123, then generate the architecture diagrams."
```

The agents will:
1. Automatically fetch the requirements using appropriate tools
2. Create a recipe.yaml based on those requirements
3. Generate all diagrams and documentation
4. Integrate with your existing site

### 2. Generate Everything with Natural Language

Simply tell Claude what you want - no complex commands needed:

```
# Natural language request:
"Generate technical documentation and diagrams for my e-commerce platform recipe"

# Claude's agents automatically:
# 1. Transform Agent reads recipe.yaml and creates detailed recipe.t2d.yaml
# 2. Diagram Agents generate appropriate diagrams based on content analysis
# 3. Content Agents create documentation pages
# 4. Everything integrates with your existing site structure
```

Behind the scenes, this generates `recipe.t2d.yaml` (agent-created, detailed specification):

```yaml
recipe:
  name: "E-Commerce Platform"
  version: "1.0.0"
  source_recipe: "recipe.yaml"
  generated_at: "2025-01-17T10:30:00Z"

  # Intelligent agent configuration (auto-generated)
  agents:
    transform_agent:
      use_proactively: true
      state_file: ".t2d/transform.state"

    diagram_agents:
      - agent: d2_generator
        use_proactively: true
        frameworks: ["d2"]
        specialties: ["architecture", "systems", "c4"]
        state_file: ".t2d/d2.state"

      - agent: mermaid_generator
        use_proactively: true
        frameworks: ["mermaid"]
        specialties: ["sequence", "flowchart", "erd"]
        state_file: ".t2d/mermaid.state"

    content_agents:
      - agent: mkdocs_maintainer
        use_proactively: true
        target_formats: ["mkdocs", "markdown"]
        integration: existing_site
        state_file: ".t2d/mkdocs.state"

  # Auto-discovered diagram requirements
  diagram_specs:
    - id: system-architecture
      type: architecture
      framework: d2  # Auto-selected based on complexity
      title: "E-Commerce Microservices Architecture"
      config:
        D2Options:
          layout: elk
          theme: "neutral"
          font_size: 14
      output_files:
        source: "docs/assets/system-architecture.d2"
        rendered: "docs/assets/system-architecture.svg"

    - id: user-flow
      type: sequence
      framework: mermaid  # Auto-selected for sequence diagrams
      title: "Shopping Flow"
      config:
        MermaidConfig:
          theme: "default"
          sequence:
            showSequenceNumbers: true
      output_files:
        source: "docs/assets/user-flow.mmd"
        rendered: "docs/assets/user-flow.svg"

    - id: database-schema
      type: erd
      framework: mermaid
      title: "Database Relationships"
      output_files:
        source: "docs/assets/database.mmd"
        rendered: "docs/assets/database.svg"

  # Integration with existing MkDocs site
  integration:
    existing_site: true
    mkdocs_config: "mkdocs.yml"  # Will be updated, not replaced
    pages:
      - id: architecture
        path: "docs/features/architecture.md"
        config:
          MkDocsPageConfig:
            title: "Platform Architecture"
            nav_position: 2
            tags: ["architecture", "microservices"]
        diagrams: ["system-architecture", "user-flow"]

      - id: database
        path: "docs/features/database.md"
        diagrams: ["database-schema"]

  # File-based state management
  state_management:
    base_dir: ".t2d"
    files:
      agent_states: ".t2d/agents.state"
      generation_log: ".t2d/generation.log"
      dependency_graph: ".t2d/deps.yaml"
```

### 3. Agents Self-Execute Automatically

The agents are already working! Claude continues processing based on the "use proactively" configuration:

```
# Agents automatically coordinate:
#
# Transform Agent:
# ✓ Created recipe.t2d.yaml with intelligent analysis
# ✓ State saved to .t2d/transform.state
#
# D2 Generator Agent:
# ✓ Generated system-architecture.d2
# ✓ Compiled to docs/assets/system-architecture.svg
# ✓ State updated in .t2d/d2.state
#
# Mermaid Generator Agent:
# ✓ Generated user-flow.mmd and database-schema.mmd
# ✓ Compiled to SVG files in docs/assets/
# ✓ State updated in .t2d/mermaid.state
#
# MkDocs Maintainer Agent:
# ✓ Created docs/features/architecture.md
# ✓ Created docs/features/database.md
# ✓ Updated mkdocs.yml navigation (preserving existing content)
# ✓ Added page metadata and tags
# ✓ State saved to .t2d/mkdocs.state
#
# File System State:
# ✓ .t2d/agents.state - Overall coordination state
# ✓ .t2d/generation.log - Complete activity log
# ✓ .t2d/deps.yaml - Inter-diagram dependencies
```

### 4. View Your Integrated Documentation

The agents have created content that integrates seamlessly with your existing site:

**docs/features/architecture.md** (created by MkDocs Maintainer Agent):

```markdown
---
title: Platform Architecture
tags: [architecture, microservices]
---

# Platform Architecture

## Microservices Overview

![E-Commerce Microservices Architecture](../assets/system-architecture.svg)

Our e-commerce platform uses a microservices architecture with the following key services:

- **Auth Service**: User authentication and authorization
- **Product Service**: Product catalog and inventory management
- **Cart Service**: Shopping cart state management
- **Order Service**: Order processing and tracking
- **Payment Service**: Payment processing with Stripe integration

## User Shopping Flow

The complete user journey from product discovery to purchase:

![Shopping Flow](../assets/user-flow.svg)

This sequence shows how users interact with our microservices:

1. Browse products through the Product Service
2. Add items to cart via Cart Service (cached in Redis)
3. Proceed through checkout workflow
4. Process payment through Payment Service and Stripe
5. Create order record in Order Service
6. Send confirmation notifications

## Database Schema

![Database Relationships](../assets/database.svg)

The database design supports the microservices architecture with clear service boundaries and optimized relationships for high-performance queries.
```

## Natural Language Interface

t2d-kit eliminates complex CLI commands in favor of natural language interaction with intelligent agents.

### Core Philosophy: "Just Tell Claude What You Want"

```
# Instead of memorizing commands, just describe your needs:

"Create architecture diagrams for my microservices platform"
→ Agents analyze requirements, choose appropriate frameworks, generate diagrams

"Add a sequence diagram showing the payment flow"
→ Mermaid Agent creates sequence diagram, MkDocs Agent updates documentation

"Generate API documentation with examples"
→ Content Agents create comprehensive API docs integrated with your existing site

"Update the database schema diagram to include the new user roles table"
→ Agents update ERD, regenerate affected documentation pages
```

### Agent Self-Activation

Agents are configured with `use_proactively: true` and automatically activate when Claude recognizes relevant tasks:

- **Transform Agent**: Activates when Claude sees recipe files or requirements
- **Diagram Agents**: Activate when architectural or flow discussions occur
- **Content Agents**: Activate when documentation needs arise
- **Integration Agents**: Maintain consistency across your existing site

### File-Based State Management

All agent coordination happens through transparent file states:

```bash
# View agent states (all human-readable)
ls .t2d/
# agents.state      - Current agent coordination
# generation.log    - Complete activity history
# deps.yaml         - Inter-component dependencies
# transform.state   - Transform agent progress
# d2.state         - D2 diagram generation state
# mermaid.state    - Mermaid diagram generation state
# mkdocs.state     - Documentation integration state
```

### Simple Setup Commands

```bash
# One-time setup of intelligent agents
t2d setup

# Connect to your existing documentation project
t2d mcp .

# Verify everything is working
t2d verify
```

## Simplified Architecture

t2d-kit uses a minimal Python foundation with intelligent Claude agents providing all the complexity.

### Python Components (Minimal Infrastructure)

**CLI Wrapper**: Just setup and MCP server startup
```python
@cli.command()
def setup():
    """Install intelligent agents to ~/.claude/agents/"""
    # Copies self-organizing agent configurations

@cli.command()
def mcp(working_dir):
    """Start MCP server for file operations"""
    # Provides file I/O for agents in your existing project
```

**MCP Server**: File operations and recipe validation
```python
class T2DMCPServer:
    async def read_recipe(path: str) -> Recipe:
        # File I/O with Pydantic validation

    async def manage_state(agent_id: str, state: dict):
        # Transparent state persistence for agents
```

### Agent Intelligence (Where the Magic Happens)

All the intelligence lives in self-organizing Claude agents:

- **Transform Agent**: Analyzes requirements, creates detailed specifications
- **Diagram Framework Agents**: D2, Mermaid, PlantUML generators that self-select based on content
- **Content Integration Agents**: Maintain your existing MkDocs site structure
- **State Coordination**: File-based coordination without complex orchestration

**Key insight**: Instead of building complex Python orchestration logic, t2d-kit uses Claude's natural intelligence with minimal infrastructure.

## Integration with Existing Sites

### Seamless MkDocs Integration

t2d-kit is designed to enhance your existing documentation, not replace it:

```json
// Claude Desktop MCP settings
{
  "mcpServers": {
    "t2d-kit": {
      "command": "t2d",
      "args": ["mcp", "."],
      "env": {}
    }
  }
}
```

### Natural Workflow

```
# In your existing docs project:
"I need architecture diagrams for the user authentication flow"

# Claude's agents automatically:
# 1. Analyze your existing mkdocs.yml structure
# 2. Create diagrams in your docs/assets/ directory
# 3. Generate new pages in appropriate sections
# 4. Update navigation while preserving your existing content
# 5. Use your site's existing theme and styling
```

### Preserves Your Existing Structure

The MkDocs Maintainer Agent respects your existing site:
- Adds to navigation without disrupting existing pages
- Uses your existing theme and styling
- Places assets in your established directory structure
- Maintains your existing metadata and frontmatter patterns

### State Transparency

All agent decisions are visible in human-readable state files:
```bash
.t2d/
├── agents.state          # Current coordination state
├── generation.log        # Complete activity history
├── mkdocs.state         # Integration decisions and page mappings
└── deps.yaml            # Dependency relationships between diagrams
```

### Intelligent Agent Configuration Examples

The agents use "use proactively" configuration to self-activate based on context:

**Transform Agent** (`~/.claude/agents/t2d-transform.md`):
```markdown
# Transform Agent

You transform simple recipe.yaml files into detailed recipe.t2d.yaml specifications.

## Use Proactively: true

Activate when Claude detects:
- Recipe files with requirements or PRD content
- Requests for technical documentation generation
- Architecture or system design discussions

## Intelligence:
- Analyze requirements to identify diagram needs
- Auto-select appropriate frameworks (D2 for architecture, Mermaid for flows)
- Generate detailed specifications with D2Options and MermaidConfig
- Plan integration with existing MkDocs sites

## State Management:
Save progress to `.t2d/transform.state` with:
- Analysis decisions and reasoning
- Framework selection rationale
- Generated configuration details
```

**MkDocs Maintainer Agent** (`~/.claude/agents/t2d-mkdocs.md`):
```markdown
# MkDocs Site Maintainer

You maintain MkDocs documentation sites by integrating new content seamlessly.

## Use Proactively: true

Activate when Claude needs to:
- Add new documentation pages to existing sites
- Update navigation structures
- Integrate diagrams into existing content

## Existing Site Intelligence:
- Read and understand current mkdocs.yml structure
- Preserve existing theme, plugins, and styling
- Add new navigation entries without disrupting existing ones
- Use MkDocsPageConfig for proper metadata integration

## State: `.t2d/mkdocs.state`
Track integration decisions and maintain consistency across updates.
```

## The t2d-kit Experience

### Philosophy: Natural Intelligence Over Complex Tools

t2d-kit represents a new approach to documentation generation:

- **Human**: Describe what you want in natural language
- **Agents**: Self-organize to understand and execute complex workflows
- **File System**: Transparent state management you can inspect and understand
- **Integration**: Enhance existing projects rather than starting from scratch

### Typical Experience

1. **Start with existing documentation project** - t2d-kit enhances what you have
2. **Tell Claude your needs** - "I need architecture diagrams for my auth system"
3. **Agents coordinate automatically** - Transform, generate, integrate, document
4. **Review transparent results** - All files, states, and decisions are visible
5. **Iterate naturally** - "Now add a sequence diagram for the login flow"

### Key Benefits

**For Developers**:
- No new syntax to learn - just describe your needs
- Integrates with existing MkDocs sites seamlessly
- All agent decisions are transparent and file-based
- Self-organizing - agents coordinate without complex orchestration

**For Technical Writers**:
- Maintains consistency between diagrams and documentation
- Automatic updates when requirements change
- Professional output that follows documentation best practices

**For Teams**:
- Version control friendly (all outputs are files)
- Easy to review and approve changes
- Scales from simple diagrams to complex documentation systems

## Presentations with Marp Integration

### Natural Presentation Creation

```
# Tell Claude what you want:
"Create a presentation about our microservices architecture for the executive team"

# Claude's agents automatically:
# 1. Identify key diagrams needed for executive audience
# 2. Generate appropriate diagrams (high-level, business-focused)
# 3. Create Marp-formatted slides
# 4. Include speaker notes
# 5. Configure for PDF export
```

### Generated Marp Output

The Marp Agent creates presentation files that work with your existing workflow:

**slides/executive-overview.md**:
```markdown
---
marp: true
theme: default
paginate: true
---

# E-Commerce Platform Architecture
## Executive Overview

![bg right:60%](../docs/assets/system-architecture.svg)

Key benefits: Scalability, Security, Time-to-Market

<!-- Speaker notes: Emphasize the business value of microservices -->

---

# Customer Journey

![width:900px](../docs/assets/user-flow.svg)

Streamlined experience from browse to purchase

<!-- Walk through each step, emphasizing conversion optimization -->
```

### Automatic Presentation Configuration

The Marp Agent uses intelligent defaults:
- Executive audience → Clean, business-focused visuals
- Technical audience → Detailed diagrams with code examples
- PDF export enabled for distribution
- Speaker notes included based on audience type

## Seamless Site Integration

### Works with Your Existing MkDocs Site

t2d-kit is designed to enhance what you already have:

```bash
# In your existing documentation project
cd my-existing-docs-site

# Start t2d-kit MCP server
t2d mcp .

# Tell Claude what you need
"Add architecture diagrams to our API documentation"

# Agents automatically:
# - Analyze your existing mkdocs.yml
# - Preserve your theme, plugins, and structure
# - Add new content in appropriate sections
# - Generate diagrams compatible with your setup
```

### Intelligent MkDocs Configuration

The MkDocs Agent understands your existing setup and adds minimal configuration:

**Existing mkdocs.yml** (preserved):
```yaml
site_name: My API Documentation
theme:
  name: material
nav:
  - Home: index.md
  - API Reference: api/
  - Guides: guides/
```

**Updated mkdocs.yml** (enhanced by agents):
```yaml
site_name: My API Documentation
theme:
  name: material
nav:
  - Home: index.md
  - API Reference: api/
  - Architecture: features/architecture.md  # Added
  - Database: features/database.md          # Added
  - Guides: guides/

# Minimal additions for diagram support
markdown_extensions:
  - attr_list  # For diagram sizing
  - md_in_html  # For advanced layouts
```

### Respect Your Workflow

- Uses your existing asset directories
- Maintains your naming conventions
- Preserves your site theme and styling
- Adds only necessary configuration changes

## Advanced Usage Examples

### Complex Multi-System Documentation

```
# Natural language for complex scenarios:
"Document our entire platform including the authentication microservice,
payment processing system, and the new notification service. Include
database relationships, API flows, and deployment architecture."

# Agents coordinate to create:
# - Multiple architecture diagrams (D2 for complex systems)
# - Sequence diagrams for each service interaction (Mermaid)
# - Comprehensive ERD showing all service data relationships
# - API documentation with interactive examples
# - Deployment diagrams showing Kubernetes configuration
```

### Framework Intelligence

Agents automatically choose the best framework for each diagram type:

```yaml
# In the generated recipe.t2d.yaml, you'll see intelligent selections:
diagram_specs:
  - type: architecture
    framework: d2          # Auto-selected for complex systems
    config:
      D2Options:
        layout: elk        # Best for microservices
        theme: neutral

  - type: sequence
    framework: mermaid     # Auto-selected for interactions
    config:
      MermaidConfig:
        theme: default
        sequence:
          showSequenceNumbers: true

  - type: erd
    framework: mermaid     # Best syntax for database relationships
```

## Troubleshooting

### Understanding Agent Behavior

Since agents work intelligently, troubleshooting focuses on understanding their decisions:

**Check Agent States**:
```bash
# View current agent coordination
cat .t2d/agents.state

# See complete generation history
cat .t2d/generation.log

# Understand framework selection decisions
cat .t2d/transform.state
```

**Common Scenarios**:

```
# Agent didn't activate as expected:
"Why didn't the diagram agent create any sequence diagrams?"

# Claude will explain:
# - What it detected in the requirements
# - Why certain diagram types were or weren't identified
# - How to adjust requirements for different outcomes

# Framework selection questions:
"Why was D2 chosen instead of Mermaid for the architecture diagram?"

# Check .t2d/transform.state for the reasoning
```

**Verify Dependencies**:
```bash
# Check that required tools are available
t2d verify

# If missing tools:
mise install  # Installs all dependencies automatically
```

### Getting Help from Agents

Since agents are intelligent, you can ask them directly:

```
# In Claude Desktop:
"Explain why the MkDocs integration didn't update the navigation"

# Or:
"What would happen if I changed the requirements to emphasize security instead of scalability?"

# Agents can explain their reasoning and suggest improvements
```

## Next Steps

### Start Small, Think Big

1. **Begin with your existing documentation** - t2d-kit enhances what you have
2. **Try a simple request** - "Add a system architecture diagram to my docs"
3. **Observe the agent coordination** - Check `.t2d/` files to understand decisions
4. **Iterate naturally** - "Now add sequence diagrams for the user workflows"
5. **Scale up complexity** - Let agents handle multi-system documentation

### Learning Path

**Week 1**: Basic diagram generation
- Start with simple architecture or flow diagrams
- Understand how agents choose frameworks
- Get comfortable with natural language requests

**Week 2**: Site integration
- Integrate with your existing MkDocs site
- Explore how agents preserve your site structure
- Try presentation generation with Marp

**Week 3**: Advanced workflows
- Multi-system documentation
- Complex diagram relationships
- Custom requirements and iterations

### Community and Support

- **Examples**: Explore patterns in the `examples/` directory
- **Issues**: Report problems and improvements
- **Discussions**: Share usage patterns and learn from others

---

**Remember**: t2d-kit succeeds when you forget about the tools and focus on describing what you need. The agents handle the complexity so you can focus on your ideas.