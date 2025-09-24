#!/usr/bin/env python3
"""Example of creating a user recipe using the MCP tools.

This script demonstrates the correct schema and parameters for creating
recipes through the t2d-kit MCP server.
"""

import asyncio
import json
from typing import Any, Dict

# Example recipe structures that follow the correct schema


def get_minimal_recipe() -> Dict[str, Any]:
    """Get a minimal valid recipe structure."""
    return {
        "name": "minimal-example",
        "prd_content": """# Minimal System

This is a simple system that processes data.

## Features
- Data input
- Processing
- Output generation
""",
        "diagrams": [
            {
                "type": "flowchart",
                "description": "Main data processing flow"
            }
        ]
    }


def get_complete_recipe() -> Dict[str, Any]:
    """Get a complete recipe with all optional fields."""
    return {
        "name": "ecommerce-platform",
        "prd_content": """# E-Commerce Platform

A comprehensive online shopping system with modern architecture.

## Overview
The platform provides a complete e-commerce solution including:
- Product catalog management
- Shopping cart functionality
- Order processing
- Payment integration
- Inventory management
- Customer accounts

## Technical Requirements
- Microservices architecture
- RESTful APIs
- React frontend
- PostgreSQL database
- Redis caching
- Docker deployment

## User Stories
1. As a customer, I want to browse products by category
2. As a customer, I want to add items to my cart
3. As a customer, I want to checkout securely
4. As an admin, I want to manage inventory
5. As an admin, I want to view sales reports
""",
        "diagrams": [
            {
                "type": "architecture",
                "description": "High-level system architecture showing all components",
                "framework_preference": "d2"
            },
            {
                "type": "erd",
                "description": "Database schema for products, orders, and users",
                "framework_preference": "d2"
            },
            {
                "type": "sequence",
                "description": "Order checkout process flow",
                "framework_preference": "mermaid"
            },
            {
                "type": "component",
                "description": "Frontend component hierarchy",
                "framework_preference": "plantuml"
            },
            {
                "type": "deployment",
                "description": "Container deployment architecture"
            }
        ],
        "documentation_config": {
            "style": "technical",
            "audience": "developers",
            "sections": ["Overview", "Architecture", "API Reference", "Deployment"],
            "detail_level": "detailed",
            "include_code_examples": True,
            "include_diagrams_inline": True
        }
    }


def get_recipe_with_external_prd() -> Dict[str, Any]:
    """Get a recipe that references an external PRD file."""
    return {
        "name": "system-with-external-prd",
        "prd_file_path": "./docs/requirements.md",
        "diagrams": [
            {
                "type": "architecture",
                "description": "System components and relationships"
            },
            {
                "type": "flowchart",
                "description": "Main business process"
            }
        ]
    }


def print_recipe_json(recipe: Dict[str, Any], title: str) -> None:
    """Print a recipe in JSON format for clarity."""
    print(f"\n{'='*60}")
    print(f"{title}")
    print('='*60)
    print(json.dumps(recipe, indent=2))
    print()


async def main():
    """Main function to demonstrate recipe structures."""

    print("T2D-Kit MCP Recipe Creation Examples")
    print("====================================")

    # Show minimal recipe
    minimal = get_minimal_recipe()
    print_recipe_json(minimal, "1. MINIMAL RECIPE")
    print("This is the simplest valid recipe with just required fields.")
    print("Use this when you want t2d-kit to infer most details from the PRD.")

    # Show complete recipe
    complete = get_complete_recipe()
    print_recipe_json(complete, "2. COMPLETE RECIPE")
    print("This recipe uses all available options for maximum control.")
    print("Specify framework preferences, documentation style, and more.")

    # Show recipe with external PRD
    external = get_recipe_with_external_prd()
    print_recipe_json(external, "3. RECIPE WITH EXTERNAL PRD")
    print("Use prd_file_path instead of prd_content for large PRDs.")
    print("The file path is relative to the current working directory.")

    print("\n" + "="*60)
    print("HOW TO USE WITH CLAUDE CODE")
    print("="*60)
    print("""
1. Ask Claude Code to create a recipe:
   "Create a t2d-kit recipe for my e-commerce system"

2. Provide the PRD content or file path

3. Claude Code will call the create_user_recipe tool with:
   - name: Your chosen recipe name
   - prd_content or prd_file_path: Your PRD
   - diagrams: List of diagram specifications

4. The tool will validate the recipe and save it to ./recipes/

5. The t2d-transform agent will automatically process it

Common Diagram Types:
- architecture: System overview
- flowchart: Process flows
- sequence: Interaction sequences
- erd: Database schemas
- component: Component relationships
- deployment: Infrastructure layout
- state: State machines
- class: Class structures

Framework Options:
- d2: Modern, declarative diagrams
- mermaid: Web-friendly diagrams
- plantuml: Enterprise UML diagrams
- auto: Let t2d-kit choose
""")

    print("\n" + "="*60)
    print("VALIDATION RULES")
    print("="*60)
    print("""
The MCP server validates:
- Recipe name: alphanumeric with hyphens/underscores
- Version: semantic versioning (e.g., "1.0.0")
- PRD: either content OR file_path, not both
- PRD size: max 1MB for embedded content
- Diagrams: at least one required
- Diagram types: must be recognized types
- Framework: must be d2, mermaid, plantuml, or auto
- File paths: no path traversal (..)
""")


if __name__ == "__main__":
    asyncio.run(main())