"""T031: Create CLI main entry with Click."""

import click
from rich.console import Console

from t2d_kit._version import __version__

console = Console()


@click.group()
@click.version_option(__version__, prog_name="t2d")
def cli():
    """t2d-kit: Transform requirements into beautiful diagrams and documentation.

    Use self-organizing agents to generate diagrams from PRDs.
    """
    pass


# Import commands to register them
from .mcp_cmd import mcp_command
from .setup import setup_command
from .verify import verify_command

# Register commands
cli.add_command(setup_command)
cli.add_command(mcp_command)
cli.add_command(verify_command)

if __name__ == "__main__":
    cli()
