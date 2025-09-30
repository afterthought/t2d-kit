"""Recipe management CLI commands for t2d-kit."""

import json
import sys
from pathlib import Path
import click
import yaml
from rich.console import Console
from rich.table import Table

from t2d_kit.models.user_recipe import UserRecipe
from t2d_kit.models.processed_recipe import ProcessedRecipe
from pydantic import ValidationError

console = Console()

# Recipe directories - hardcoded for simplicity and reliability
USER_RECIPES_DIR = Path("./recipes")
PROCESSED_RECIPES_DIR = Path("./.t2d-state/processed")


def ensure_directories():
    """Ensure recipe directories exist."""
    USER_RECIPES_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_RECIPES_DIR.mkdir(parents=True, exist_ok=True)


@click.group(name="recipe")
def recipe_command():
    """Manage t2d-kit recipe files."""
    pass


@recipe_command.command()
@click.option('--type', '-t', default='all', help='Recipe type: user, processed, or all')
@click.option('--json', 'json_output', is_flag=True, help='Output as JSON')
def list(type, json_output):
    """List available recipes."""
    recipes = {}

    if type in ["user", "all"]:
        if USER_RECIPES_DIR.exists():
            user_recipes = [
                p.stem for p in USER_RECIPES_DIR.glob("*.yaml")
                if not p.name.endswith(".backup")
            ]
            recipes["user"] = sorted(user_recipes)
        else:
            recipes["user"] = []

    if type in ["processed", "all"]:
        if PROCESSED_RECIPES_DIR.exists():
            processed_recipes = [
                p.name.replace(".t2d.yaml", "")
                for p in PROCESSED_RECIPES_DIR.glob("*.t2d.yaml")
                if not p.name.endswith(".backup")
            ]
            recipes["processed"] = sorted(processed_recipes)
        else:
            recipes["processed"] = []

    if json_output:
        print(json.dumps(recipes, indent=2))
    else:
        if "user" in recipes and recipes["user"]:
            table = Table(title="User Recipes")
            table.add_column("Name", style="cyan")
            for name in recipes["user"]:
                table.add_row(name)
            console.print(table)

        if "processed" in recipes and recipes["processed"]:
            table = Table(title="Processed Recipes")
            table.add_column("Name", style="green")
            for name in recipes["processed"]:
                table.add_row(name)
            console.print(table)

        if not any(recipes.values()):
            console.print("[yellow]No recipes found[/yellow]")


@recipe_command.command()
@click.argument('name')
@click.option('--type', '-t', default='user', help='Recipe type: user or processed')
@click.option('--json', 'json_output', is_flag=True, help='Output as JSON')
def load(name, type, json_output):
    """Load and display a recipe file."""
    if type == "user":
        recipe_path = USER_RECIPES_DIR / f"{name}.yaml"
        model_class = UserRecipe
    else:
        recipe_path = PROCESSED_RECIPES_DIR / f"{name}.t2d.yaml"
        model_class = ProcessedRecipe

    if not recipe_path.exists():
        error_msg = f"Recipe not found: {name}"
        if json_output:
            print(json.dumps({"error": error_msg}))
        else:
            console.print(f"[red]Error:[/red] {error_msg}")
        sys.exit(1)

    try:
        with open(recipe_path) as f:
            data = yaml.safe_load(f)

        # Validate with Pydantic
        recipe = model_class.model_validate(data)

        if json_output:
            print(json.dumps(recipe.model_dump(), indent=2, default=str))
        else:
            console.print(yaml.dump(recipe.model_dump(exclude_none=True),
                                   default_flow_style=False))

    except ValidationError as e:
        error_msg = f"Invalid recipe: {str(e)}"
        if json_output:
            print(json.dumps({"error": error_msg}))
        else:
            console.print(f"[red]Error:[/red] {error_msg}")
        sys.exit(1)
    except Exception as e:
        error_msg = f"Failed to load recipe: {str(e)}"
        if json_output:
            print(json.dumps({"error": error_msg}))
        else:
            console.print(f"[red]Error:[/red] {error_msg}")
        sys.exit(1)


@recipe_command.command()
@click.argument('name')
@click.option('--type', '-t', default='user', help='Recipe type: user or processed')
@click.option('--data', '-d', default='-', help='Recipe data (JSON/YAML string or \'-\' for stdin)')
@click.option('--force', '-f', is_flag=True, help='Overwrite existing file')
def save(name, type, data, force):
    """Save a recipe to file."""
    ensure_directories()

    # Read data
    if data == "-":
        data_str = sys.stdin.read()
    else:
        data_str = data

    try:
        # Try JSON first, then YAML
        try:
            recipe_data = json.loads(data_str)
        except json.JSONDecodeError:
            recipe_data = yaml.safe_load(data_str)
    except Exception as e:
        console.print(f"[red]Error:[/red] Invalid data format: {e}")
        sys.exit(1)

    # Validate and save based on type
    try:
        if type == "user":
            recipe = UserRecipe.model_validate(recipe_data)
            recipe.name = name
            recipe_path = USER_RECIPES_DIR / f"{name}.yaml"
        else:
            recipe = ProcessedRecipe.model_validate(recipe_data)
            recipe.name = name
            recipe_path = PROCESSED_RECIPES_DIR / f"{name}.t2d.yaml"

        # Create backup if file exists
        if recipe_path.exists() and not force:
            console.print(f"[yellow]Recipe already exists:[/yellow] {recipe_path}")
            console.print("Use --force to overwrite")
            sys.exit(1)

        if recipe_path.exists():
            backup_path = recipe_path.with_suffix(recipe_path.suffix + ".backup")
            recipe_path.rename(backup_path)

        # Save to file
        with open(recipe_path, 'w') as f:
            yaml.dump(recipe.model_dump(exclude_none=True, mode='json'), f,
                     default_flow_style=False, sort_keys=False)

        console.print(f"[green]✓[/green] Saved to: {recipe_path}")

    except ValidationError as e:
        console.print(f"[red]Validation error:[/red] {str(e)}")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Save failed:[/red] {str(e)}")
        sys.exit(1)


@recipe_command.command()
@click.option('--type', '-t', default='user', help='Schema type: user or processed')
@click.option('--format', '-f', default='yaml',
              type=click.Choice(['json', 'yaml', 'markdown', 'agent']),
              help='Output format: json, yaml, markdown (detailed), or agent (concise)')
def schema(type, format):
    """Display the JSON schema for recipe validation.

    Format options:
      - json: Raw JSON schema (for programmatic use)
      - yaml: YAML formatted schema (default, human-readable)
      - markdown: Detailed markdown documentation with examples
      - agent: Concise format optimized for Claude Code agents
    """
    try:
        if type == "user":
            schema_dict = UserRecipe.model_json_schema()
            model_name = "UserRecipe"
        else:
            schema_dict = ProcessedRecipe.model_json_schema()
            model_name = "ProcessedRecipe"

        if format == 'json':
            print(json.dumps(schema_dict, indent=2))
        elif format == 'markdown':
            from t2d_kit.utils.schema_formatter import format_schema_markdown
            print(format_schema_markdown(schema_dict, model_name))
        elif format == 'agent':
            from t2d_kit.utils.schema_formatter import format_schema_agent_friendly
            print(format_schema_agent_friendly(schema_dict, model_name))
        else:  # yaml
            console.print(f"[bold]Schema for {type} recipes:[/bold]\n")
            console.print(yaml.dump(schema_dict, default_flow_style=False))
    except Exception as e:
        console.print(f"[red]Error:[/red] Failed to get schema: {str(e)}")
        sys.exit(1)


@recipe_command.command()
@click.argument('name')
@click.option('--type', '-t', help='Recipe type: user or processed (auto-detected if not specified)')
@click.option('--json', 'json_output', is_flag=True, help='Output as JSON')
def validate(name, type, json_output):
    """Validate a recipe file against its schema."""
    recipe_path = Path(name)

    # Auto-detect type if not specified
    if not type:
        if ".t2d.yaml" in recipe_path.name:
            type = "processed"
        else:
            type = "user"

    # If just a name was provided, build the full path
    if not recipe_path.exists():
        if type == "user":
            recipe_path = USER_RECIPES_DIR / f"{name}.yaml"
        else:
            recipe_path = PROCESSED_RECIPES_DIR / f"{name}.t2d.yaml"

    if not recipe_path.exists():
        result = {
            "valid": False,
            "file": str(recipe_path),
            "error": f"Recipe file not found: {recipe_path}"
        }
        if json_output:
            print(json.dumps(result))
        else:
            console.print(f"[red]Error:[/red] {result['error']}")
        sys.exit(1)

    # Validate based on type
    try:
        with open(recipe_path) as f:
            data = yaml.safe_load(f)

        if type == "user":
            recipe = UserRecipe.model_validate(data)
            # Additional checks
            if recipe.prd.content and recipe.prd.file_path:
                raise ValueError("Recipe cannot have both prd.content and prd.file_path")
            if not recipe.prd.content and not recipe.prd.file_path:
                raise ValueError("Recipe must have either prd.content or prd.file_path")
            if not recipe.instructions.diagrams:
                raise ValueError("Recipe must have at least one diagram")
        else:
            recipe = ProcessedRecipe.model_validate(data)
            if not recipe.diagram_specs:
                raise ValueError("Processed recipe must have at least one diagram")

        result = {
            "valid": True,
            "file": str(recipe_path),
            "type": type
        }

        if json_output:
            print(json.dumps(result, indent=2))
        else:
            console.print(f"[green]✓[/green] {type.capitalize()} recipe is valid: {recipe_path}")

    except ValidationError as e:
        errors = []
        for error in e.errors():
            field = ".".join(str(x) for x in error['loc'])
            msg = error['msg']
            errors.append(f"{field}: {msg}")

        result = {
            "valid": False,
            "file": str(recipe_path),
            "type": type,
            "errors": errors
        }

        if json_output:
            print(json.dumps(result, indent=2))
        else:
            console.print(f"[red]✗[/red] Validation failed: {recipe_path}")
            for error in errors:
                console.print(f"  - {error}")
        sys.exit(1)

    except Exception as e:
        result = {
            "valid": False,
            "file": str(recipe_path),
            "type": type,
            "error": str(e)
        }

        if json_output:
            print(json.dumps(result, indent=2))
        else:
            console.print(f"[red]✗[/red] {type.capitalize()} recipe validation failed")
            console.print(f"  {str(e)}")
        sys.exit(1)