"""T020: StateManager for file-based coordination between agents."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Literal

from pydantic import Field, field_validator

from .base import T2DBaseModel


class StateManager(T2DBaseModel):
    """Manages file-based state for agent coordination."""

    state_dir: Path = Field(default=Path(".t2d-state"), description="Directory for state files")

    @field_validator("state_dir")
    @classmethod
    def ensure_state_dir(cls, v: Path) -> Path:
        """Create state directory if it doesn't exist."""
        v.mkdir(exist_ok=True)
        return v

    def write_state(self, key: str, data: dict) -> None:
        """Write state data to file."""
        state_file = self.state_dir / f"{key}.json"
        state_file.write_text(json.dumps(data, indent=2, default=str))

    def read_state(self, key: str) -> dict | None:
        """Read state data from file."""
        state_file = self.state_dir / f"{key}.json"
        if state_file.exists():
            return json.loads(state_file.read_text())
        return None

    def list_states(self) -> list[str]:
        """List all available state keys."""
        return [f.stem for f in self.state_dir.glob("*.json")]

    def delete_state(self, key: str) -> bool:
        """Delete a state file."""
        state_file = self.state_dir / f"{key}.json"
        if state_file.exists():
            state_file.unlink()
            return True
        return False

    # T047: Add error recovery to state management
    def recover_from_error(self, key: str) -> dict | None:
        """Attempt to recover state from a corrupted file."""
        state_file = self.state_dir / f"{key}.json"
        if not state_file.exists():
            return None

        try:
            # Try normal read first
            return json.loads(state_file.read_text())
        except json.JSONDecodeError:
            # Try to read backup if exists
            backup_file = self.state_dir / f"{key}.json.backup"
            if backup_file.exists():
                try:
                    return json.loads(backup_file.read_text())
                except json.JSONDecodeError:
                    pass

            # Try partial recovery - read line by line
            try:
                lines = state_file.read_text().splitlines()
                for i in range(len(lines), 0, -1):
                    try:
                        partial = "\n".join(lines[:i])
                        return json.loads(partial)
                    except json.JSONDecodeError:
                        continue
            except Exception:
                pass

        return None

    def write_state_with_backup(self, key: str, data: dict) -> None:
        """Write state with backup for recovery."""
        state_file = self.state_dir / f"{key}.json"
        backup_file = self.state_dir / f"{key}.json.backup"

        # Create backup of existing file if it exists
        if state_file.exists():
            backup_file.write_text(state_file.read_text())

        # Write new state
        self.write_state(key, data)

    def cleanup_old_states(self, max_age_days: int = 7) -> int:
        """Clean up state files older than specified days."""
        cutoff = datetime.now().timestamp() - (max_age_days * 24 * 60 * 60)
        cleaned = 0

        for state_file in self.state_dir.glob("*.json"):
            if state_file.stat().st_mtime < cutoff:
                state_file.unlink()
                cleaned += 1

        return cleaned


class ProcessingState(T2DBaseModel):
    """Tracks the state of recipe processing."""

    recipe_path: Path
    started_at: datetime
    completed_at: datetime | None = None

    # Track what's been processed
    diagrams_completed: list[str] = Field(default_factory=list)
    content_files_created: list[Path] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)

    # Current phase
    phase: Literal["transforming", "generating", "documenting", "complete", "error"] = (
        "transforming"
    )

    def add_completed_diagram(self, diagram_id: str) -> None:
        """Mark a diagram as completed."""
        if diagram_id not in self.diagrams_completed:
            self.diagrams_completed.append(diagram_id)

    def add_content_file(self, file_path: Path) -> None:
        """Track a created content file."""
        if file_path not in self.content_files_created:
            self.content_files_created.append(file_path)

    def add_error(self, error: str) -> None:
        """Record an error."""
        self.errors.append(error)
        self.phase = "error"

    def complete(self) -> None:
        """Mark processing as complete."""
        self.completed_at = datetime.utcnow()
        self.phase = "complete"

    def is_complete(self) -> bool:
        """Check if processing is complete."""
        return self.completed_at is not None

    def has_errors(self) -> bool:
        """Check if there are any errors."""
        return len(self.errors) > 0

    def get_progress_summary(self) -> dict[str, Any]:
        """Get a summary of processing progress."""
        return {
            "phase": self.phase,
            "diagrams_completed": len(self.diagrams_completed),
            "content_files_created": len(self.content_files_created),
            "errors": len(self.errors),
            "is_complete": self.is_complete(),
            "has_errors": self.has_errors(),
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


class DiagramGenerationState(T2DBaseModel):
    """State for diagram generation agents."""

    diagram_id: str
    framework: str  # Using str instead of FrameworkType to avoid import
    status: Literal["pending", "generating", "complete", "failed"] = "pending"
    output_files: list[Path] = Field(default_factory=list)
    error_message: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None

    def mark_started(self) -> None:
        """Mark generation as started."""
        self.status = "generating"
        self.started_at = datetime.utcnow()

    def mark_complete(self, files: list[Path]) -> None:
        """Mark generation as complete with output files."""
        self.status = "complete"
        self.output_files = files
        self.completed_at = datetime.utcnow()

    def mark_failed(self, error: str) -> None:
        """Mark generation as failed."""
        self.status = "failed"
        self.error_message = error
        self.completed_at = datetime.utcnow()


class ContentGenerationState(T2DBaseModel):
    """State for content generation agents."""

    content_type: Literal["documentation", "presentation"]
    status: Literal["waiting", "gathering", "generating", "complete", "failed"] = "waiting"
    diagrams_found: list[Path] = Field(default_factory=list)
    output_path: Path | None = None
    error_message: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None

    def mark_started(self) -> None:
        """Mark content generation as started."""
        self.status = "generating"
        self.started_at = datetime.utcnow()

    def add_diagram(self, path: Path) -> None:
        """Add a discovered diagram."""
        if path not in self.diagrams_found:
            self.diagrams_found.append(path)

    def mark_complete(self, output_path: Path) -> None:
        """Mark content generation as complete."""
        self.status = "complete"
        self.output_path = output_path
        self.completed_at = datetime.utcnow()

    def mark_failed(self, error: str) -> None:
        """Mark content generation as failed."""
        self.status = "failed"
        self.error_message = error
        self.completed_at = datetime.utcnow()


class AgentCoordinationState(T2DBaseModel):
    """State for coordinating multiple agents working on a recipe."""

    recipe_name: str
    agents_working: dict[str, str] = Field(default_factory=dict)  # agent_id -> status
    completion_order: list[str] = Field(default_factory=list)
    dependencies: dict[str, list[str]] = Field(default_factory=dict)  # agent_id -> [dependency_ids]

    def register_agent(self, agent_id: str, status: str = "pending") -> None:
        """Register an agent as working on this recipe."""
        self.agents_working[agent_id] = status

    def update_agent_status(self, agent_id: str, status: str) -> None:
        """Update an agent's status."""
        if agent_id in self.agents_working:
            self.agents_working[agent_id] = status
            if status == "complete":
                self.completion_order.append(agent_id)

    def set_dependencies(self, agent_id: str, dependencies: list[str]) -> None:
        """Set dependencies for an agent."""
        self.dependencies[agent_id] = dependencies

    def can_agent_start(self, agent_id: str) -> bool:
        """Check if an agent can start based on dependencies."""
        if agent_id not in self.dependencies:
            return True

        deps = self.dependencies[agent_id]
        for dep in deps:
            if dep not in self.agents_working or self.agents_working[dep] != "complete":
                return False

        return True

    def get_ready_agents(self) -> list[str]:
        """Get list of agents that can start working."""
        ready = []
        for agent_id, status in self.agents_working.items():
            if status == "pending" and self.can_agent_start(agent_id):
                ready.append(agent_id)
        return ready

    def is_all_complete(self) -> bool:
        """Check if all agents have completed their work."""
        return all(status == "complete" for status in self.agents_working.values())
