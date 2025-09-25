"""MCP resource for diagram types discovery."""

from fastmcp import FastMCP

from t2d_kit.models.mcp_resources import DiagramTypeInfo

# Define available diagram types
DIAGRAM_TYPES = [
    DiagramTypeInfo(
        type_id="flowchart",
        name="Flowchart",
        framework="mermaid",
        description="Process flow visualization",
        example_usage="Show the order processing workflow",
        supported_frameworks=["mermaid", "d2"]
    ),
    DiagramTypeInfo(
        type_id="sequence",
        name="Sequence Diagram",
        framework="mermaid",
        description="Interaction sequences between components",
        example_usage="Show API call sequence",
        supported_frameworks=["mermaid", "plantuml"]
    ),
    DiagramTypeInfo(
        type_id="erd",
        name="Entity Relationship Diagram",
        framework="d2",
        description="Database schema visualization",
        example_usage="Show database tables and relationships",
        supported_frameworks=["d2", "plantuml"]
    ),
    DiagramTypeInfo(
        type_id="architecture",
        name="Architecture Diagram",
        framework="d2",
        description="High-level system architecture",
        example_usage="Show microservices and their connections",
        supported_frameworks=["d2", "mermaid"]
    ),
    DiagramTypeInfo(
        type_id="class",
        name="Class Diagram",
        framework="plantuml",
        description="Object-oriented class structure",
        example_usage="Show inheritance and relationships",
        supported_frameworks=["plantuml", "mermaid"]
    ),
    DiagramTypeInfo(
        type_id="state",
        name="State Machine Diagram",
        framework="mermaid",
        description="State transitions and behavior",
        example_usage="Show order lifecycle states",
        supported_frameworks=["mermaid", "plantuml"]
    ),
    DiagramTypeInfo(
        type_id="activity",
        name="Activity Diagram",
        framework="plantuml",
        description="Workflow with parallel activities",
        example_usage="Show business process flow",
        supported_frameworks=["plantuml", "mermaid"]
    ),
    DiagramTypeInfo(
        type_id="component",
        name="Component Diagram",
        framework="plantuml",
        description="Component structure and dependencies",
        example_usage="Show module organization",
        supported_frameworks=["plantuml", "d2"]
    ),
    DiagramTypeInfo(
        type_id="deployment",
        name="Deployment Diagram",
        framework="d2",
        description="System deployment topology",
        example_usage="Show server infrastructure",
        supported_frameworks=["d2", "plantuml"]
    ),
    DiagramTypeInfo(
        type_id="usecase",
        name="Use Case Diagram",
        framework="plantuml",
        description="User interactions with the system",
        example_usage="Show actor-system interactions",
        supported_frameworks=["plantuml", "mermaid"]
    ),
    DiagramTypeInfo(
        type_id="gantt",
        name="Gantt Chart",
        framework="mermaid",
        description="Project timeline and dependencies",
        example_usage="Show project milestones",
        supported_frameworks=["mermaid"]
    ),
    DiagramTypeInfo(
        type_id="mindmap",
        name="Mind Map",
        framework="mermaid",
        description="Hierarchical concept visualization",
        example_usage="Show feature breakdown",
        supported_frameworks=["mermaid"]
    ),
    DiagramTypeInfo(
        type_id="c4-context",
        name="C4 Context Diagram",
        framework="d2",
        description="System context with external entities",
        example_usage="Show system boundaries",
        supported_frameworks=["d2", "plantuml"]
    ),
    DiagramTypeInfo(
        type_id="c4-container",
        name="C4 Container Diagram",
        framework="d2",
        description="Container-level architecture",
        example_usage="Show applications and data stores",
        supported_frameworks=["d2", "plantuml"]
    ),
    DiagramTypeInfo(
        type_id="c4-component",
        name="C4 Component Diagram",
        framework="d2",
        description="Component-level design",
        example_usage="Show internal component structure",
        supported_frameworks=["d2", "plantuml"]
    ),
    DiagramTypeInfo(
        type_id="network",
        name="Network Diagram",
        framework="d2",
        description="Network topology and connections",
        example_usage="Show network architecture",
        supported_frameworks=["d2"]
    ),
    DiagramTypeInfo(
        type_id="dataflow",
        name="Data Flow Diagram",
        framework="d2",
        description="Data movement through system",
        example_usage="Show data processing pipeline",
        supported_frameworks=["d2", "mermaid"]
    ),
    DiagramTypeInfo(
        type_id="journey",
        name="User Journey Map",
        framework="mermaid",
        description="User experience journey",
        example_usage="Show customer touchpoints",
        supported_frameworks=["mermaid"]
    ),
    DiagramTypeInfo(
        type_id="timeline",
        name="Timeline Diagram",
        framework="mermaid",
        description="Events over time",
        example_usage="Show project history",
        supported_frameworks=["mermaid"]
    ),
    DiagramTypeInfo(
        type_id="pie",
        name="Pie Chart",
        framework="mermaid",
        description="Proportional data visualization",
        example_usage="Show resource allocation",
        supported_frameworks=["mermaid"]
    )
]


# Categorize diagram types
DIAGRAM_CATEGORIES = {
    "structural": ["erd", "class", "component", "deployment", "c4-context", "c4-container", "c4-component"],
    "behavioral": ["sequence", "state", "activity", "usecase", "dataflow"],
    "architectural": ["architecture", "c4-context", "c4-container", "c4-component", "network", "deployment"],
    "process": ["flowchart", "activity", "journey", "dataflow"],
    "planning": ["gantt", "timeline", "mindmap"],
    "data": ["erd", "dataflow", "pie"]
}


async def register_diagram_types_resource(server: FastMCP) -> None:
    """Register the diagram types resource with the MCP server.

    Args:
        server: FastMCP server instance
    """

    @server.resource("diagram-types://")
    async def diagram_types() -> list:
        """Available diagram types for t2d-kit.

        Returns an array of diagram type definitions with frameworks and examples.
        """
        # Return just the diagram types array
        return [diagram_type.model_dump() for diagram_type in DIAGRAM_TYPES]
