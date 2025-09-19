# Quickstart: MCP Recipe Management

This guide demonstrates how to use the t2d-kit MCP server to create, manage, and process recipes for diagram generation.

## Prerequisites

1. **t2d-kit installed**: `pip install t2d-kit`
2. **MCP server running**: `t2d mcp`
3. **Claude Desktop configured** with MCP server

## 1. Discover Available Resources

### List Available Diagram Types

```python
# Via MCP client
resources = await client.list_resources()
diagram_types = await client.read_resource("diagram-types://")

# Expected response:
{
  "diagram_types": [
    {
      "type_id": "flowchart",
      "name": "Flowchart",
      "framework": "mermaid",
      "description": "Process flow visualization",
      "example_usage": "Show the order processing workflow",
      "supported_frameworks": ["mermaid", "d2"]
    },
    {
      "type_id": "sequence",
      "name": "Sequence Diagram",
      "framework": "mermaid",
      "description": "Interaction sequences between components",
      "example_usage": "Show API call sequence",
      "supported_frameworks": ["mermaid", "plantuml"]
    }
  ],
  "total_count": 30,
  "categories": {
    "structural": ["erd", "class", "component"],
    "behavioral": ["sequence", "state", "activity"],
    "architectural": ["c4-context", "deployment"]
  }
}
```

### Browse Existing Recipes

```python
# List all user recipes
user_recipes = await client.read_resource("user-recipes://")

# Get specific user recipe
recipe = await client.read_resource("user-recipes://ecommerce")

# List processed recipes
processed = await client.read_resource("processed-recipes://")
```

### Get Recipe Schema

```python
# User recipe schema
schema = await client.read_resource("user-recipe-schema://")

# Processed recipe schema
processed_schema = await client.read_resource("processed-recipe-schema://")
```

## 2. Create a User Recipe

### Step 1: Define Recipe Content

```python
from t2d_kit.models import DiagramRequest, DocumentationConfig

# Create recipe using MCP tool
result = await client.call_tool("create_user_recipe", {
    "name": "my-system",
    "prd_content": """
        # My System PRD

        ## Overview
        A system for managing customer orders...

        ## Features
        - User authentication
        - Order management
        - Payment processing
    """,
    "diagrams": [
        {
            "type": "flowchart",
            "description": "Order processing workflow",
            "framework": "mermaid"
        },
        {
            "type": "erd",
            "description": "Database schema",
            "framework": "d2"
        }
    ],
    "documentation_config": {
        "style": "technical",
        "audience": "developers",
        "sections": ["Overview", "Architecture", "API"],
        "format": "mkdocs"
    },
    "output_dir": "./recipes"
})

print(f"Recipe created: {result.file_path}")
```

### Step 2: Validate the Recipe

```python
# Validate existing recipe file
validation = await client.call_tool("validate_user_recipe", {
    "name": "my-system"
})

if validation.valid:
    print("Recipe is valid!")
else:
    for error in validation.errors:
        print(f"Error in {error.field}: {error.message}")
```

## 3. Process Recipe to Generate Specifications

### Step 1: Transform User Recipe to Processed Recipe

```python
# The transform agent reads the user recipe and generates detailed specs
processed_content = {
    "name": "my-system",
    "version": "1.0.0",
    "source_recipe": "./recipes/my-system.yaml",
    "generated_at": "2025-09-18T10:00:00Z",
    "diagram_specs": [
        {
            "id": "flow-001",
            "type": "flowchart",
            "framework": "mermaid",
            "agent": "t2d-mermaid-generator",
            "title": "Order Processing Flow",
            "instructions": "Create a detailed flowchart showing...",
            "output_file": "docs/assets/order-flow",
            "output_formats": ["svg", "png"]
        },
        {
            "id": "erd-001",
            "type": "erd",
            "framework": "d2",
            "agent": "t2d-d2-generator",
            "title": "Database Schema",
            "instructions": "Generate an ERD with tables for...",
            "output_file": "docs/assets/database",
            "output_formats": ["svg", "pdf"]
        }
    ],
    "content_files": [
        {
            "id": "overview",
            "path": "docs/overview.md",
            "type": "documentation",
            "agent": "t2d-docs",
            "base_prompt": "Create overview documentation...",
            "diagram_refs": ["flow-001", "erd-001"],
            "last_updated": "2025-09-18T10:00:00Z"
        }
    ],
    "diagram_refs": [
        {
            "id": "flow-001",
            "title": "Order Processing Flow",
            "type": "flowchart",
            "expected_path": "docs/assets/order-flow.svg",
            "status": "pending"
        },
        {
            "id": "erd-001",
            "title": "Database Schema",
            "type": "erd",
            "expected_path": "docs/assets/database.svg",
            "status": "pending"
        }
    ],
    "outputs": {
        "assets_dir": "docs/assets",
        "mkdocs": {
            "config_file": "mkdocs.yml",
            "site_name": "My System Documentation"
        }
    }
}

# Write processed recipe
result = await client.call_tool("write_processed_recipe", {
    "recipe_path": "./recipes/my-system.t2d.yaml",
    "content": processed_content,
    "validate": True
})
```

### Step 2: Update Processed Recipe Status

```python
# After diagram generation, update status
await client.call_tool("update_processed_recipe", {
    "recipe_path": "./recipes/my-system.t2d.yaml",
    "diagram_refs": [
        {
            "id": "flow-001",
            "title": "Order Processing Flow",
            "type": "flowchart",
            "expected_path": "docs/assets/order-flow.svg",
            "status": "complete"  # Updated from "pending"
        }
    ],
    "generation_notes": ["Flowchart generated successfully"]
})
```

## 4. Edit Existing Recipes

### Edit User Recipe

```python
# Update diagram specifications
result = await client.call_tool("edit_user_recipe", {
    "name": "my-system",
    "diagrams": [
        {
            "type": "flowchart",
            "description": "Updated order workflow with payment",
            "framework": "mermaid"
        },
        {
            "type": "sequence",  # Added new diagram
            "description": "Payment API sequence",
            "framework": "mermaid"
        }
    ],
    "validate_before_save": True
})
```

### Update Processed Recipe

```python
# Add new diagram specification
result = await client.call_tool("update_processed_recipe", {
    "recipe_path": "./recipes/my-system.t2d.yaml",
    "diagram_specs": [
        # ... existing specs ...
        {
            "id": "seq-001",
            "type": "sequence",
            "framework": "mermaid",
            "agent": "t2d-mermaid-generator",
            "title": "Payment API Sequence",
            "instructions": "Show payment flow between...",
            "output_file": "docs/assets/payment-sequence",
            "output_formats": ["svg", "png"]
        }
    ]
})
```

## 5. Delete Recipes

```python
# Delete user recipe (requires confirmation)
result = await client.call_tool("delete_user_recipe", {
    "name": "old-system",
    "confirm": True
})

# Note: Processed recipes are typically not deleted directly
# They are regenerated when user recipes change
```

## 6. Complete Workflow Example

Here's a complete workflow from recipe creation to diagram generation:

```python
async def create_and_process_recipe():
    # 1. Create user recipe
    await client.call_tool("create_user_recipe", {
        "name": "api-gateway",
        "prd_content": "# API Gateway System\n...",
        "diagrams": [
            {"type": "architecture", "framework": "d2"},
            {"type": "sequence", "framework": "mermaid"}
        ]
    })

    # 2. Validate recipe
    validation = await client.call_tool("validate_user_recipe", {
        "name": "api-gateway"
    })

    if not validation.valid:
        raise ValueError("Recipe validation failed")

    # 3. Transform to processed recipe (via agent)
    # This would typically be done by the t2d-transform agent

    # 4. Generate diagrams (via generator agents)
    # Each framework agent processes its assigned diagrams

    # 5. Update documentation (via docs agent)
    # Documentation is generated with embedded diagrams

    return "Recipe processed successfully!"
```

## Testing the Implementation

### Test Resource Discovery

```bash
# List all resources
curl -X POST http://localhost:3000/mcp \
  -d '{"method": "resources/list"}'

# Read diagram types
curl -X POST http://localhost:3000/mcp \
  -d '{"method": "resources/read", "params": {"uri": "diagram-types://"}}'
```

### Test Recipe Creation

```bash
# Create a test recipe
curl -X POST http://localhost:3000/mcp \
  -d '{
    "method": "tools/call",
    "params": {
      "name": "create_user_recipe",
      "arguments": {
        "name": "test",
        "prd_content": "Test PRD",
        "diagrams": [{"type": "flowchart"}]
      }
    }
  }'
```

### Verify with Claude Desktop

1. Open Claude Desktop
2. Connect to t2d-kit MCP server
3. Ask: "Show me available diagram types"
4. Ask: "Create a recipe for an e-commerce system"
5. Verify resources and tools are discovered properly

## Troubleshooting

### Recipe Validation Fails

Check for:
- Required fields (name, prd, diagrams)
- Valid diagram types
- Proper YAML syntax
- File size < 1MB

### MCP Server Not Found

Ensure:
- Server is running: `t2d mcp`
- Claude Desktop config points to correct path
- Server logs show successful startup

### Resources Not Loading

Verify:
- Recipe directory exists and is readable
- YAML files are valid
- No file permission issues

## Next Steps

1. **Explore diagram types**: Use resource discovery to see all options
2. **Create templates**: Build reusable recipe templates
3. **Automate workflows**: Chain tools for end-to-end automation
4. **Monitor generation**: Track diagram generation status
5. **Customize agents**: Configure agent-specific settings

## Reference

- [User Recipe Schema](./contracts/mcp_tools.json)
- [Processed Recipe Schema](./contracts/mcp_processed_tools.json)
- [MCP Resources](./contracts/mcp_resources.json)
- [Data Model](./data-model.md)