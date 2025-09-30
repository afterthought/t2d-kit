"""Schema formatting utilities for agent-friendly schema documentation."""

import json
from typing import Any, Dict, List, Tuple


def format_schema_markdown(schema: Dict[str, Any], model_name: str) -> str:
    """Format JSON schema as human-readable markdown for agents.

    Args:
        schema: Pydantic JSON schema dict
        model_name: Name of the model (e.g., "UserRecipe", "ProcessedRecipe")

    Returns:
        Markdown formatted schema documentation
    """
    lines = [
        f"# {model_name} Schema",
        "",
        f"**Description:** {schema.get('description', 'No description available')}",
        "",
    ]

    # Add title if present
    if 'title' in schema and schema['title'] != model_name:
        lines.extend([
            f"**Title:** {schema['title']}",
            "",
        ])

    # Extract properties and required fields
    properties = schema.get('properties', {})
    required_fields = set(schema.get('required', []))

    # Categorize fields
    required = []
    optional = []

    for field_name, field_schema in properties.items():
        field_info = _format_field(field_name, field_schema)
        if field_name in required_fields:
            required.append(field_info)
        else:
            optional.append(field_info)

    # Required fields section
    if required:
        lines.extend([
            "## Required Fields",
            "",
        ])
        for field in required:
            lines.extend(field)
            lines.append("")

    # Optional fields section
    if optional:
        lines.extend([
            "## Optional Fields",
            "",
        ])
        for field in optional:
            lines.extend(field)
            lines.append("")

    # Add definitions section if present
    definitions = schema.get('$defs', {})
    if definitions:
        lines.extend([
            "## Type Definitions",
            "",
        ])
        for def_name, def_schema in definitions.items():
            lines.extend([
                f"### {def_name}",
                "",
            ])
            if 'description' in def_schema:
                lines.extend([
                    def_schema['description'],
                    "",
                ])

            # Add enum values if present
            if def_schema.get('type') == 'string' and 'enum' in def_schema:
                lines.extend([
                    "**Allowed values:**",
                ])
                for value in def_schema['enum']:
                    lines.append(f"  - `{value}`")
                lines.append("")

            # Add properties for object types
            if 'properties' in def_schema:
                def_required = set(def_schema.get('required', []))
                lines.append("**Properties:**")
                for prop_name, prop_schema in def_schema['properties'].items():
                    is_required = prop_name in def_required
                    prop_type = _get_type_description(prop_schema)
                    req_marker = "**required**" if is_required else "*optional*"
                    lines.append(f"  - `{prop_name}` ({prop_type}) - {req_marker}")
                    if 'description' in prop_schema:
                        lines.append(f"    {prop_schema['description']}")
                lines.append("")

    # Add examples if present
    examples = schema.get('examples', [])
    if examples:
        lines.extend([
            "## Examples",
            "",
        ])
        for i, example in enumerate(examples, 1):
            lines.extend([
                f"### Example {i}",
                "",
                "```yaml",
                json.dumps(example, indent=2),
                "```",
                "",
            ])

    # Add AI guidance if present
    ai_guidance = schema.get('ai_guidance', {})
    if ai_guidance:
        lines.extend([
            "## AI Agent Guidance",
            "",
        ])
        for key, value in ai_guidance.items():
            lines.append(f"**{key.replace('_', ' ').title()}:** {value}")
        lines.append("")

    # Add JSON schema at the end for reference
    lines.extend([
        "---",
        "",
        "## Full JSON Schema",
        "",
        "```json",
        json.dumps(schema, indent=2),
        "```",
    ])

    return "\n".join(lines)


def _format_field(field_name: str, field_schema: Dict[str, Any]) -> List[str]:
    """Format a single field as markdown lines."""
    lines = []

    # Field header
    field_type = _get_type_description(field_schema)
    lines.append(f"### `{field_name}` ({field_type})")
    lines.append("")

    # Description
    if 'description' in field_schema:
        lines.append(field_schema['description'])
        lines.append("")

    # Constraints
    constraints = _extract_constraints(field_schema)
    if constraints:
        lines.append("**Constraints:**")
        for constraint in constraints:
            lines.append(f"  - {constraint}")
        lines.append("")

    # Default value
    if 'default' in field_schema:
        lines.append(f"**Default:** `{field_schema['default']}`")
        lines.append("")

    # Examples
    if 'examples' in field_schema:
        lines.append("**Examples:**")
        for example in field_schema['examples']:
            lines.append(f"  - `{example}`")
        lines.append("")

    # Enum values
    if 'enum' in field_schema:
        lines.append("**Allowed values:**")
        for value in field_schema['enum']:
            lines.append(f"  - `{value}`")
        lines.append("")

    return lines


def _get_type_description(field_schema: Dict[str, Any]) -> str:
    """Extract human-readable type description from field schema."""
    # Handle anyOf/allOf/oneOf
    if 'anyOf' in field_schema:
        types = [_get_type_description(s) for s in field_schema['anyOf']]
        return ' | '.join(types)

    if 'allOf' in field_schema:
        types = [_get_type_description(s) for s in field_schema['allOf']]
        return ' & '.join(types)

    # Handle $ref
    if '$ref' in field_schema:
        ref = field_schema['$ref']
        return ref.split('/')[-1]  # Extract definition name

    # Handle array
    if field_schema.get('type') == 'array':
        if 'items' in field_schema:
            item_type = _get_type_description(field_schema['items'])
            return f"array[{item_type}]"
        return "array"

    # Handle object
    if field_schema.get('type') == 'object':
        return "object"

    # Simple type
    field_type = field_schema.get('type', 'any')

    # Add format if present
    if 'format' in field_schema:
        field_type += f" ({field_schema['format']})"

    return field_type


def _extract_constraints(field_schema: Dict[str, Any]) -> List[str]:
    """Extract validation constraints from field schema."""
    constraints = []

    # String constraints
    if 'minLength' in field_schema:
        constraints.append(f"Minimum length: {field_schema['minLength']}")
    if 'maxLength' in field_schema:
        constraints.append(f"Maximum length: {field_schema['maxLength']}")
    if 'pattern' in field_schema:
        constraints.append(f"Pattern: `{field_schema['pattern']}`")

    # Number constraints
    if 'minimum' in field_schema:
        constraints.append(f"Minimum: {field_schema['minimum']}")
    if 'maximum' in field_schema:
        constraints.append(f"Maximum: {field_schema['maximum']}")
    if 'exclusiveMinimum' in field_schema:
        constraints.append(f"Exclusive minimum: {field_schema['exclusiveMinimum']}")
    if 'exclusiveMaximum' in field_schema:
        constraints.append(f"Exclusive maximum: {field_schema['exclusiveMaximum']}")

    # Array constraints
    if 'minItems' in field_schema:
        constraints.append(f"Minimum items: {field_schema['minItems']}")
    if 'maxItems' in field_schema:
        constraints.append(f"Maximum items: {field_schema['maxItems']}")
    if 'uniqueItems' in field_schema:
        constraints.append("Items must be unique")

    return constraints


def format_schema_agent_friendly(schema: Dict[str, Any], model_name: str) -> str:
    """Format schema in a concise, agent-friendly format.

    This format is optimized for quick parsing by Claude Code agents.

    Args:
        schema: Pydantic JSON schema dict
        model_name: Name of the model

    Returns:
        Concise formatted schema
    """
    lines = [
        f"{model_name} Schema",
        "=" * (len(model_name) + 7),
        "",
    ]

    properties = schema.get('properties', {})
    required_fields = set(schema.get('required', []))

    # Required fields
    required = [name for name in properties.keys() if name in required_fields]
    if required:
        lines.extend([
            "Required Fields:",
        ])
        for field_name in required:
            field_schema = properties[field_name]
            field_type = _get_type_description(field_schema)
            desc = field_schema.get('description', '')
            lines.append(f"  • {field_name}: {field_type}")
            if desc:
                lines.append(f"    {desc}")
        lines.append("")

    # Optional fields
    optional = [name for name in properties.keys() if name not in required_fields]
    if optional:
        lines.extend([
            "Optional Fields:",
        ])
        for field_name in optional:
            field_schema = properties[field_name]
            field_type = _get_type_description(field_schema)
            desc = field_schema.get('description', '')
            default = field_schema.get('default')
            default_str = f" (default: {default})" if default is not None else ""
            lines.append(f"  • {field_name}: {field_type}{default_str}")
            if desc:
                lines.append(f"    {desc}")
        lines.append("")

    return "\n".join(lines)