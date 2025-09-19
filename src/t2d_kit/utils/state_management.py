"""State management utilities for t2d-kit processing."""

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

DEFAULT_STATE_DIR = Path("./.t2d-state")


class StateManager:
    """Manager for t2d-kit processing state."""

    def __init__(self, state_dir: Path | None = None):
        """Initialize state manager.

        Args:
            state_dir: Directory for state files (defaults to ./.t2d-state)
        """
        self.state_dir = state_dir or DEFAULT_STATE_DIR
        self.state_dir.mkdir(parents=True, exist_ok=True)

    def save_processing_state(self, recipe_name: str, state: dict[str, Any]) -> Path:
        """Save processing state for a recipe.

        Args:
            recipe_name: Name of the recipe being processed
            state: State dictionary to save

        Returns:
            Path to saved state file
        """
        state_file = self.state_dir / f"{recipe_name}.processing.json"

        # Add timestamp
        state["last_updated"] = datetime.now().isoformat()

        # Create backup if file exists
        if state_file.exists():
            backup_file = self.state_dir / f"{recipe_name}.processing.backup.json"
            shutil.copy2(state_file, backup_file)

        # Save state
        with open(state_file, "w") as f:
            json.dump(state, f, indent=2, default=str)

        return state_file

    def load_processing_state(self, recipe_name: str) -> dict[str, Any] | None:
        """Load processing state for a recipe.

        Args:
            recipe_name: Name of the recipe

        Returns:
            State dictionary if found, None otherwise
        """
        state_file = self.state_dir / f"{recipe_name}.processing.json"

        if not state_file.exists():
            return None

        try:
            with open(state_file) as f:
                return json.load(f)
        except (OSError, json.JSONDecodeError):
            # Try backup
            backup_file = self.state_dir / f"{recipe_name}.processing.backup.json"
            if backup_file.exists():
                try:
                    with open(backup_file) as f:
                        return json.load(f)
                except (OSError, json.JSONDecodeError):
                    pass
            return None

    def update_diagram_status(
        self,
        recipe_name: str,
        diagram_id: str,
        status: str,
        message: str | None = None
    ) -> bool:
        """Update the status of a specific diagram.

        Args:
            recipe_name: Name of the recipe
            diagram_id: ID of the diagram
            status: New status (pending, processing, complete, failed)
            message: Optional status message

        Returns:
            True if updated successfully, False otherwise
        """
        state = self.load_processing_state(recipe_name)
        if not state:
            state = {"diagrams": {}}

        if "diagrams" not in state:
            state["diagrams"] = {}

        state["diagrams"][diagram_id] = {
            "status": status,
            "updated_at": datetime.now().isoformat()
        }

        if message:
            state["diagrams"][diagram_id]["message"] = message

        self.save_processing_state(recipe_name, state)
        return True

    def get_diagram_status(self, recipe_name: str, diagram_id: str) -> dict[str, Any] | None:
        """Get the status of a specific diagram.

        Args:
            recipe_name: Name of the recipe
            diagram_id: ID of the diagram

        Returns:
            Status dictionary if found, None otherwise
        """
        state = self.load_processing_state(recipe_name)
        if not state or "diagrams" not in state:
            return None

        return state["diagrams"].get(diagram_id)

    def list_processing_states(self) -> list[dict[str, Any]]:
        """List all processing states.

        Returns:
            List of state summaries
        """
        states = []

        for state_file in self.state_dir.glob("*.processing.json"):
            recipe_name = state_file.stem.replace(".processing", "")

            try:
                state = self.load_processing_state(recipe_name)
                if state:
                    states.append({
                        "recipe_name": recipe_name,
                        "last_updated": state.get("last_updated", "unknown"),
                        "diagram_count": len(state.get("diagrams", {})),
                        "file_path": str(state_file)
                    })
            except Exception:
                # Skip corrupted files
                pass

        return sorted(states, key=lambda s: s.get("last_updated", ""), reverse=True)

    def cleanup_old_states(self, days: int = 30) -> int:
        """Clean up old state files.

        Args:
            days: Remove states older than this many days

        Returns:
            Number of files removed
        """
        removed = 0
        cutoff = datetime.now().timestamp() - (days * 86400)

        for state_file in self.state_dir.glob("*.json"):
            if state_file.stat().st_mtime < cutoff:
                try:
                    state_file.unlink()
                    removed += 1
                except Exception:
                    pass

        return removed

    def clear_state(self, recipe_name: str) -> bool:
        """Clear all state for a recipe.

        Args:
            recipe_name: Name of the recipe

        Returns:
            True if cleared, False if not found
        """
        state_file = self.state_dir / f"{recipe_name}.processing.json"
        backup_file = self.state_dir / f"{recipe_name}.processing.backup.json"

        found = False

        if state_file.exists():
            state_file.unlink()
            found = True

        if backup_file.exists():
            backup_file.unlink()
            found = True

        return found
