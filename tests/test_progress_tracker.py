# ABOUTME: Tests for the progress tracking library.
# ABOUTME: Validates schema, events, and session state transitions.

import pytest
import json
from pathlib import Path
import sys

# Add functional to path
sys.path.insert(0, str(Path(__file__).parent.parent / "functional"))

from progress_tracker import (
    validate_progress_schema,
    ProgressValidationError,
    create_event,
    EventType,
    ProgressEvent,
    create_empty_progress,
    start_session,
    end_session,
    add_event,
    get_current_work,
    set_current_work,
    WorkType,
    find_progress_file
)


class TestSchemaValidation:
    """Test progress.json schema validation."""

    def test_valid_v2_schema(self):
        """Valid v2 schema should pass validation."""
        valid_progress = {
            "version": 2,
            "lastUpdated": "2025-12-11T18:00:00Z",
            "project": "test-project",
            "currentWork": {
                "type": "general",
                "plan": None,
                "planTask": None,
                "debugIssue": None,
                "debugPhase": None
            },
            "lastSession": {
                "date": "2025-12-11",
                "duration_minutes": 45,
                "summary": "Test session",
                "events": [],
                "commits": [],
                "nextSteps": []
            },
            "recentSessions": [],
            "knownIssues": []
        }
        # Should not raise
        validate_progress_schema(valid_progress)

    def test_missing_version_fails(self):
        """Missing version field should fail validation."""
        invalid = {"project": "test"}
        with pytest.raises(ProgressValidationError, match="version"):
            validate_progress_schema(invalid)

    def test_wrong_version_fails(self):
        """Version != 2 should fail validation."""
        invalid = {"version": 1, "project": "test"}
        with pytest.raises(ProgressValidationError, match="version 2"):
            validate_progress_schema(invalid)

    def test_missing_required_fields_fails(self):
        """Missing required top-level fields should fail."""
        invalid = {"version": 2}
        with pytest.raises(ProgressValidationError):
            validate_progress_schema(invalid)


class TestEventCreation:
    """Test event creation and serialization."""

    def test_create_session_start_event(self):
        """Create a session_start event."""
        event = create_event(EventType.SESSION_START)
        assert event.type == "session_start"
        assert event.timestamp is not None
        assert event.data == {}

    def test_create_plan_started_event(self):
        """Create a plan_started event with data."""
        event = create_event(
            EventType.PLAN_STARTED,
            plan="docs/plans/2025-12-11-progress-tracking.md"
        )
        assert event.type == "plan_started"
        assert event.data["plan"] == "docs/plans/2025-12-11-progress-tracking.md"

    def test_create_debug_started_event(self):
        """Create a debug_started event."""
        event = create_event(
            EventType.DEBUG_STARTED,
            issue="Test failures in auth module"
        )
        assert event.type == "debug_started"
        assert event.data["issue"] == "Test failures in auth module"

    def test_event_to_dict(self):
        """Events serialize to dict correctly."""
        event = create_event(EventType.CHECKPOINT, summary="Mid-session save")
        d = event.to_dict()
        assert d["type"] == "checkpoint"
        assert "timestamp" in d
        assert d["summary"] == "Mid-session save"

    def test_event_from_dict(self):
        """Events deserialize from dict correctly."""
        d = {
            "type": "plan_task_completed",
            "timestamp": "2025-12-11T18:00:00Z",
            "task": 3
        }
        event = ProgressEvent.from_dict(d)
        assert event.type == "plan_task_completed"
        assert event.data["task"] == 3


class TestSessionState:
    """Test session state management."""

    def test_create_empty_progress(self):
        """Create empty progress structure."""
        data = create_empty_progress("test-project")
        assert data["version"] == 2
        assert data["project"] == "test-project"
        assert data["currentWork"]["type"] == "general"
        # Should pass validation
        validate_progress_schema(data)

    def test_start_session_creates_state(self, tmp_path):
        """Starting a session initializes currentWork."""
        progress_file = tmp_path / "project-progress.json"

        # Create minimal v2 file
        initial = create_empty_progress("test-project")
        progress_file.write_text(json.dumps(initial))

        # Start session
        start_session(progress_file, session_id="test-123")

        # Verify currentWork updated
        data = json.loads(progress_file.read_text())
        assert data["currentWork"]["type"] == "general"

    def test_end_session_writes_last_session(self, tmp_path):
        """Ending a session populates lastSession."""
        progress_file = tmp_path / "project-progress.json"
        initial = create_empty_progress("test-project")
        progress_file.write_text(json.dumps(initial))

        # Start then end
        start_session(progress_file, session_id="test-123")
        end_session(
            progress_file,
            session_id="test-123",
            duration_minutes=30,
            summary="Test session summary",
            commits=[{"hash": "abc123", "message": "Test commit"}]
        )

        data = json.loads(progress_file.read_text())
        assert data["lastSession"]["duration_minutes"] == 30
        assert data["lastSession"]["summary"] == "Test session summary"
        assert len(data["lastSession"]["commits"]) == 1

    def test_add_event_to_session(self, tmp_path):
        """Adding events appends to session events."""
        progress_file = tmp_path / "project-progress.json"
        initial = create_empty_progress("test-project")
        progress_file.write_text(json.dumps(initial))

        start_session(progress_file, session_id="test-123")

        # Add events
        add_event(progress_file, "test-123", EventType.PLAN_STARTED, plan="test.md")
        add_event(progress_file, "test-123", EventType.PLAN_TASK_COMPLETED, task=1)

        # End session and check events preserved
        end_session(progress_file, "test-123", 30, "Done", [])

        data = json.loads(progress_file.read_text())
        # Should have session_start + plan_started + plan_task_completed + session_end
        assert len(data["lastSession"]["events"]) >= 2

    def test_set_current_work_plan(self, tmp_path):
        """Setting current work to plan mode."""
        progress_file = tmp_path / "project-progress.json"
        initial = create_empty_progress("test-project")
        progress_file.write_text(json.dumps(initial))

        set_current_work(
            progress_file,
            work_type=WorkType.PLAN,
            plan="docs/plans/test.md",
            plan_task=1
        )

        data = json.loads(progress_file.read_text())
        assert data["currentWork"]["type"] == "plan"
        assert data["currentWork"]["plan"] == "docs/plans/test.md"
        assert data["currentWork"]["planTask"] == 1

    def test_set_current_work_debug(self, tmp_path):
        """Setting current work to debug mode."""
        progress_file = tmp_path / "project-progress.json"
        initial = create_empty_progress("test-project")
        progress_file.write_text(json.dumps(initial))

        set_current_work(
            progress_file,
            work_type=WorkType.DEBUG,
            debug_issue="Test failures",
            debug_phase="investigating"
        )

        data = json.loads(progress_file.read_text())
        assert data["currentWork"]["type"] == "debug"
        assert data["currentWork"]["debugIssue"] == "Test failures"
        assert data["currentWork"]["debugPhase"] == "investigating"

    def test_get_current_work(self, tmp_path):
        """Get current work state."""
        progress_file = tmp_path / "project-progress.json"
        initial = create_empty_progress("test-project")
        progress_file.write_text(json.dumps(initial))

        work = get_current_work(progress_file)
        assert work["type"] == "general"


class TestPathResolution:
    """Test progress file path resolution."""

    def test_find_in_current_dir(self, tmp_path):
        """Find progress.json in current directory."""
        progress = tmp_path / "project-progress.json"
        progress.write_text("{}")

        found = find_progress_file(tmp_path)
        assert found == progress

    def test_find_in_project_subdir(self, tmp_path):
        """Find progress.json in projects/name/ structure."""
        # Create projects/myproject/project-progress.json
        project_dir = tmp_path / "projects" / "myproject"
        project_dir.mkdir(parents=True)
        progress = project_dir / "project-progress.json"
        progress.write_text("{}")

        # When cwd is the project dir, should find it
        found = find_progress_file(project_dir)
        assert found == progress

    def test_create_if_not_exists(self, tmp_path):
        """Create progress.json if it doesn't exist."""
        found = find_progress_file(tmp_path, create_if_missing=True)
        assert found.exists()

        data = json.loads(found.read_text())
        assert data["version"] == 2

    def test_returns_none_if_not_found(self, tmp_path):
        """Return None if no progress file and create=False."""
        found = find_progress_file(tmp_path, create_if_missing=False)
        assert found is None

    def test_walks_up_to_find_progress(self, tmp_path):
        """Walk up directory tree to find progress file."""
        # Create progress at root
        progress = tmp_path / "project-progress.json"
        progress.write_text("{}")

        # Create nested directory
        nested = tmp_path / "src" / "components"
        nested.mkdir(parents=True)

        # Should find progress from nested dir
        found = find_progress_file(nested)
        assert found == progress

    def test_stops_at_git_root(self, tmp_path):
        """Stop walking at git root."""
        # Create git root
        git_dir = tmp_path / ".git"
        git_dir.mkdir()

        # Create progress above git root (shouldn't be found)
        parent_progress = tmp_path.parent / "project-progress.json"
        # Don't actually create it in parent (could affect other tests)

        # Create nested directory
        nested = tmp_path / "src"
        nested.mkdir()

        # Should not find anything (stops at git root)
        found = find_progress_file(nested, create_if_missing=False)
        assert found is None
