"""MCP resources for recipe schemas."""

from fastmcp import FastMCP

from t2d_kit.models.mcp_resources import RecipeSchemaResource, SchemaField


def extract_fields_from_model(model_class, prefix="") -> list[SchemaField]:
    """Extract schema fields from a Pydantic model.

    Args:
        model_class: Pydantic model class
        prefix: Field name prefix for nested fields

    Returns:
        List of SchemaField objects
    """
    fields = []

    for field_name, field_info in model_class.model_fields.items():
        full_name = f"{prefix}.{field_name}" if prefix else field_name

        # Get type information
        field_type = str(field_info.annotation)
        if "Optional" in field_type:
            field_type = field_type.replace("Optional[", "").replace("]", "") + " (optional)"

        # Build constraints
        constraints = {}
        if hasattr(field_info, "min_length"):
            constraints["min_length"] = field_info.min_length
        if hasattr(field_info, "max_length"):
            constraints["max_length"] = field_info.max_length
        if hasattr(field_info, "ge"):
            constraints["min"] = field_info.ge
        if hasattr(field_info, "le"):
            constraints["max"] = field_info.le

        fields.append(SchemaField(
            name=full_name,
            type=field_type,
            required=field_info.is_required(),
            description=field_info.description or "",
            default=field_info.default if not field_info.is_required() else None,
            constraints=constraints if constraints else None,
            example=None  # Could be populated from field metadata
        ))

    return fields


async def register_schema_resources(server: FastMCP) -> None:
    """Register schema resources with the MCP server.

    Args:
        server: FastMCP server instance
    """

    @server.resource("user-recipe-schema://")
    async def get_user_recipe_schema() -> dict:
        """Get the schema for user recipes.

        Returns the complete schema definition for creating and validating
        user recipe files, including all fields, types, and constraints.
        """
        from t2d_kit.models.user_recipe import UserRecipe

        # Extract fields from model
        fields = extract_fields_from_model(UserRecipe)

        # Example recipes
        examples = {
            "minimal": {
                "name": "my-system",
                "version": "1.0.0",
                "prd": {
                    "content": "# My System\\n\\nSystem description..."
                },
                "instructions": {
                    "diagrams": [
                        {
                            "type": "flowchart",
                            "description": "Main workflow"
                        }
                    ]
                }
            },
            "complete": {
                "name": "ecommerce-platform",
                "version": "2.0.0",
                "prd": {
                    "file_path": "./docs/prd.md",
                    "format": "markdown"
                },
                "instructions": {
                    "diagrams": [
                        {
                            "type": "architecture",
                            "description": "System architecture",
                            "framework_preference": "d2"
                        },
                        {
                            "type": "erd",
                            "description": "Database schema",
                            "framework_preference": "d2"
                        },
                        {
                            "type": "sequence",
                            "description": "Order processing flow",
                            "framework_preference": "mermaid"
                        }
                    ],
                    "documentation": {
                        "style": "technical",
                        "audience": "developers",
                        "sections": ["Overview", "API", "Deployment"],
                        "detail_level": "detailed",
                        "include_code_examples": True
                    },
                    "presentation": {
                        "audience": "stakeholders",
                        "max_slides": 20,
                        "style": "business",
                        "include_speaker_notes": True
                    }
                },
                "preferences": {
                    "default_framework": "mermaid",
                    "diagram_style": "modern",
                    "color_scheme": "blue",
                    "theme": "light"
                }
            }
        }

        # Validation rules
        validation_rules = [
            "Recipe name must start with a letter and contain only alphanumeric, hyphens, underscores",
            "Version must follow semantic versioning (e.g., 1.0.0)",
            "PRD must provide either content or file_path, not both",
            "At least one diagram must be specified",
            "Diagram types must be valid (see diagram-types:// resource)",
            "Framework preferences must be one of: mermaid, d2, plantuml, auto",
            "File paths must not contain path traversal sequences (..)",
            "PRD content is limited to 1MB",
            "Documentation style must be one of: technical, business, tutorial, reference",
            "Presentation style must be one of: technical, business, educational"
        ]

        resource = RecipeSchemaResource(
            version="1.0.0",
            fields=fields,
            examples=examples,
            validation_rules=validation_rules
        )

        return {
            "uri": "user-recipe-schema://",
            "name": "User Recipe Schema",
            "description": "Complete schema definition for user recipe files",
            "mimeType": "application/json",
            "content": resource.model_dump()
        }

    @server.resource("processed-recipe-schema://")
    async def get_processed_recipe_schema() -> dict:
        """Get the schema for processed recipes.

        Returns the complete schema definition for processed recipe files,
        which are generated by the t2d-transform agent.
        """
        from t2d_kit.models.processed_recipe import ProcessedRecipe

        # Extract fields from model
        fields = extract_fields_from_model(ProcessedRecipe)

        # Example recipes
        examples = {
            "minimal": {
                "name": "my-system",
                "version": "1.0.0",
                "source_recipe": "./recipes/my-system.yaml",
                "generated_at": "2024-01-15T10:30:00Z",
                "content_files": [
                    {
                        "id": "main-doc",
                        "path": "docs/index.md",
                        "type": "documentation",
                        "agent": "t2d-docs",
                        "base_prompt": "Generate main documentation",
                        "diagram_refs": ["flow-001"],
                        "last_updated": "2024-01-15T10:30:00Z"
                    }
                ],
                "diagram_specs": [
                    {
                        "id": "flow-001",
                        "type": "flowchart",
                        "framework": "mermaid",
                        "agent": "t2d-mermaid-generator",
                        "title": "Main Workflow",
                        "instructions": "Generate flowchart showing main workflow",
                        "output_file": "docs/assets/main-flow",
                        "output_formats": ["svg", "png"],
                        "options": {}
                    }
                ],
                "diagram_refs": [
                    {
                        "id": "flow-001",
                        "title": "Main Workflow",
                        "type": "flowchart",
                        "expected_path": "docs/assets/main-flow.svg",
                        "status": "pending"
                    }
                ],
                "outputs": {
                    "assets_dir": "docs/assets"
                }
            }
        }

        # Validation rules
        validation_rules = [
            "All fields from ProcessedRecipe are required",
            "generated_at must be a valid ISO timestamp",
            "source_recipe must point to an existing user recipe file",
            "Each diagram_spec must have a unique id",
            "Each content_file must have a unique id",
            "diagram_refs must match diagram_specs by id",
            "content_file diagram_refs must reference valid diagram ids",
            "Framework must be one of: mermaid, d2, plantuml",
            "Output formats must be valid for the framework",
            "Agent names must follow the pattern: t2d-{framework}-generator",
            "Status in diagram_refs must be: pending, generated, or failed"
        ]

        resource = RecipeSchemaResource(
            version="1.0.0",
            fields=fields,
            examples=examples,
            validation_rules=validation_rules
        )

        return {
            "uri": "processed-recipe-schema://",
            "name": "Processed Recipe Schema",
            "description": "Complete schema definition for processed recipe files",
            "mimeType": "application/json",
            "content": resource.model_dump()
        }
