"""T011: Test StateManager for file-based state coordination between agents."""

import json
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import mock_open, patch

import pytest

from t2d_kit.models.state import StateManager


class TestStateManager:
    """Test cases for StateManager functionality."""

    def test_state_manager_initialization(self, tmp_path):
        """Test that StateManager can be initialized with proper directory setup."""
        state_dir = tmp_path / "test_state"
        state_manager = StateManager(state_dir=state_dir)

        assert state_manager is not None
        assert state_manager.state_dir == state_dir
        assert state_dir.exists()  # Should be created by validator
        assert state_dir.is_dir()

    def test_state_manager_default_initialization(self):
        """Test StateManager initialization with default state directory."""
        state_manager = StateManager()
        assert state_manager.state_dir == Path(".t2d-state")

    def test_write_and_read_state(self, tmp_path):
        """Test writing and reading state data."""
        state_dir = tmp_path / "test_state"
        state_manager = StateManager(state_dir=state_dir)

        test_data = {
            "agent_id": "test_agent",
            "status": "running",
            "data": {"key": "value", "number": 42}
        }

        # Write state
        state_manager.write_state("test_key", test_data)

        # Verify file was created
        state_file = state_dir / "test_key.json"
        assert state_file.exists()

        # Read state back
        retrieved_data = state_manager.read_state("test_key")
        assert retrieved_data == test_data

    def test_read_nonexistent_state(self, tmp_path):
        """Test reading state that doesn't exist returns None."""
        state_dir = tmp_path / "test_state"
        state_manager = StateManager(state_dir=state_dir)

        result = state_manager.read_state("nonexistent_key")
        assert result is None

    def test_delete_state(self, tmp_path):
        """Test deleting state files."""
        state_dir = tmp_path / "test_state"
        state_manager = StateManager(state_dir=state_dir)

        test_data = {"key": "value"}
        state_manager.write_state("delete_test", test_data)

        # Verify it exists
        assert state_manager.read_state("delete_test") == test_data

        # Delete it
        result = state_manager.delete_state("delete_test")
        assert result is True

        # Verify it's gone
        assert state_manager.read_state("delete_test") is None

    def test_delete_nonexistent_state(self, tmp_path):
        """Test deleting state that doesn't exist returns False."""
        state_dir = tmp_path / "test_state"
        state_manager = StateManager(state_dir=state_dir)

        result = state_manager.delete_state("nonexistent")
        assert result is False

    def test_list_states(self, tmp_path):
        """Test listing all available state keys."""
        state_dir = tmp_path / "test_state"
        state_manager = StateManager(state_dir=state_dir)

        # Create some test states
        test_keys = ["agent1", "agent2", "coordination"]
        for key in test_keys:
            state_manager.write_state(key, {"data": f"test_{key}"})

        # List states
        states = state_manager.list_states()
        assert set(states) == set(test_keys)

    def test_list_states_empty_directory(self, tmp_path):
        """Test listing states in empty directory."""
        state_dir = tmp_path / "test_state"
        state_manager = StateManager(state_dir=state_dir)

        states = state_manager.list_states()
        assert states == []

    def test_write_state_with_backup(self, tmp_path):
        """Test writing state with backup functionality."""
        state_dir = tmp_path / "test_state"
        state_manager = StateManager(state_dir=state_dir)

        # Write initial state
        initial_data = {"version": 1, "data": "initial"}
        state_manager.write_state("backup_test", initial_data)

        # Write new state with backup
        new_data = {"version": 2, "data": "updated"}
        state_manager.write_state_with_backup("backup_test", new_data)

        # Verify main file has new data
        assert state_manager.read_state("backup_test") == new_data

        # Verify backup file exists with old data
        backup_file = state_dir / "backup_test.json.backup"
        assert backup_file.exists()
        backup_content = json.loads(backup_file.read_text())
        assert backup_content == initial_data

    def test_recover_from_error_normal_file(self, tmp_path):
        """Test error recovery with normal (non-corrupted) file."""
        state_dir = tmp_path / "test_state"
        state_manager = StateManager(state_dir=state_dir)

        test_data = {"status": "normal", "data": "valid"}
        state_manager.write_state("recovery_test", test_data)

        # Recovery should return the normal data
        recovered = state_manager.recover_from_error("recovery_test")
        assert recovered == test_data

    def test_recover_from_error_corrupted_file_with_backup(self, tmp_path):
        """Test error recovery with corrupted file but valid backup."""
        state_dir = tmp_path / "test_state"
        state_manager = StateManager(state_dir=state_dir)

        # Create a backup file with valid data
        backup_data = {"status": "backup", "data": "from_backup"}
        backup_file = state_dir / "corrupt_test.json.backup"
        backup_file.write_text(json.dumps(backup_data))

        # Create a corrupted main file
        main_file = state_dir / "corrupt_test.json"
        main_file.write_text("{ invalid json")

        # Recovery should use backup
        recovered = state_manager.recover_from_error("corrupt_test")
        assert recovered == backup_data

    def test_recover_from_error_nonexistent_file(self, tmp_path):
        """Test error recovery with nonexistent file."""
        state_dir = tmp_path / "test_state"
        state_manager = StateManager(state_dir=state_dir)

        recovered = state_manager.recover_from_error("nonexistent")
        assert recovered is None

    def test_cleanup_old_states(self, tmp_path):
        """Test cleaning up old state files."""
        state_dir = tmp_path / "test_state"
        state_manager = StateManager(state_dir=state_dir)

        # Create some test files
        state_manager.write_state("recent", {"data": "recent"})
        state_manager.write_state("old", {"data": "old"})

        # Simulate old file by modifying its timestamp
        old_file = state_dir / "old.json"
        old_timestamp = (datetime.now() - timedelta(days=8)).timestamp()

        # Use os.utime to actually change the file timestamp
        import os
        os.utime(old_file, (old_timestamp, old_timestamp))

        # Clean up files older than 7 days
        cleaned_count = state_manager.cleanup_old_states(max_age_days=7)

        # Should have cleaned 1 file (the old one)
        assert cleaned_count == 1

        # Verify the old file is gone and recent file remains
        assert not old_file.exists()
        assert (state_dir / "recent.json").exists()

    def test_state_persistence_across_instances(self, tmp_path):
        """Test that state persists across different StateManager instances."""
        state_dir = tmp_path / "test_state"

        # Create first instance and write data
        manager1 = StateManager(state_dir=state_dir)
        test_data = {"persistent": True, "value": 123}
        manager1.write_state("persistence_test", test_data)

        # Create second instance and read data
        manager2 = StateManager(state_dir=state_dir)
        retrieved_data = manager2.read_state("persistence_test")

        assert retrieved_data == test_data

    def test_state_data_serialization(self, tmp_path):
        """Test that complex data structures are properly serialized."""
        state_dir = tmp_path / "test_state"
        state_manager = StateManager(state_dir=state_dir)

        complex_data = {
            "string": "test",
            "number": 42,
            "float": 3.14,
            "boolean": True,
            "null": None,
            "list": [1, 2, 3, "four"],
            "nested": {
                "inner": "value",
                "deep": {
                    "level": "three"
                }
            },
            "datetime": datetime.now()  # Should be converted to string
        }

        state_manager.write_state("complex_test", complex_data)
        retrieved_data = state_manager.read_state("complex_test")

        # Most data should match exactly
        assert retrieved_data["string"] == complex_data["string"]
        assert retrieved_data["number"] == complex_data["number"]
        assert retrieved_data["float"] == complex_data["float"]
        assert retrieved_data["boolean"] == complex_data["boolean"]
        assert retrieved_data["null"] == complex_data["null"]
        assert retrieved_data["list"] == complex_data["list"]
        assert retrieved_data["nested"] == complex_data["nested"]

        # Datetime should be serialized as string
        assert isinstance(retrieved_data["datetime"], str)

    def test_concurrent_state_access_simulation(self, tmp_path):
        """Test simulation of concurrent access to state files."""
        state_dir = tmp_path / "test_state"

        # Simulate multiple agents working with state
        manager1 = StateManager(state_dir=state_dir)
        manager2 = StateManager(state_dir=state_dir)

        # Agent 1 writes initial coordination state
        coord_state = {
            "active_agents": ["agent1"],
            "completed_tasks": [],
            "pending_tasks": ["task1", "task2"]
        }
        manager1.write_state("coordination", coord_state)

        # Agent 2 reads and updates state
        current_state = manager2.read_state("coordination")
        current_state["active_agents"].append("agent2")
        current_state["pending_tasks"].remove("task1")
        current_state["completed_tasks"].append("task1")
        manager2.write_state("coordination", current_state)

        # Agent 1 reads updated state
        final_state = manager1.read_state("coordination")

        assert "agent2" in final_state["active_agents"]
        assert "task1" in final_state["completed_tasks"]
        assert "task1" not in final_state["pending_tasks"]

    def test_recover_from_error_partial_recovery(self, tmp_path):
        """Test partial recovery from corrupted JSON file."""
        state_dir = tmp_path / "test_state"
        state_manager = StateManager(state_dir=state_dir)

        # Create a partially corrupted file (valid JSON at the beginning)
        partial_json = '''{"status": "partial", "data": "valid_part"}
        { corrupted part'''

        corrupt_file = state_dir / "partial_test.json"
        corrupt_file.write_text(partial_json)

        # Recovery should return the valid part
        recovered = state_manager.recover_from_error("partial_test")
        assert recovered is not None
        assert recovered["status"] == "partial"
        assert recovered["data"] == "valid_part"

    def test_write_state_with_backup_no_existing_file(self, tmp_path):
        """Test write_state_with_backup when no existing file exists."""
        state_dir = tmp_path / "test_state"
        state_manager = StateManager(state_dir=state_dir)

        # Write state with backup when no file exists
        test_data = {"initial": True, "data": "first_write"}
        state_manager.write_state_with_backup("new_file", test_data)

        # Verify main file has the data
        assert state_manager.read_state("new_file") == test_data

        # Backup file should not exist since there was no original file
        backup_file = state_dir / "new_file.json.backup"
        assert not backup_file.exists()

    def test_json_formatting(self, tmp_path):
        """Test that JSON files are properly formatted with indentation."""
        state_dir = tmp_path / "test_state"
        state_manager = StateManager(state_dir=state_dir)

        test_data = {
            "formatted": True,
            "nested": {
                "level": "two",
                "array": [1, 2, 3]
            }
        }

        state_manager.write_state("format_test", test_data)

        # Read raw file content to verify formatting
        state_file = state_dir / "format_test.json"
        raw_content = state_file.read_text()

        # Should contain indentation and newlines
        assert "  " in raw_content  # Indentation
        assert "\n" in raw_content  # Newlines

        # Should be valid JSON that can be parsed
        parsed = json.loads(raw_content)
        assert parsed == test_data
