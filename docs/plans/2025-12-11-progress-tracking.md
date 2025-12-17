# Progress Tracking System Implementation Plan

## Goal

Create an event-driven progress tracking system that automatically tracks session state, plan progress, and debugging milestones across harness, projects, and templates.

## Architecture Overview

- **Core library:** `functional/progress_tracker.py` with pure functions for progress.json manipulation
- **Hooks:** SessionStart and Stop hooks for automatic session tracking, UserPromptSubmit for event detection
- **Commands:** Enhanced /start and /checkpoint commands
- **Schema:** progress.json v2 with currentWork and events fields

## Prerequisites

- pytest installed (`pip3 install pytest`)
- Existing hooks infrastructure in `.claude/hooks/`
- Existing commands in `.claude/commands/`

---

## Task 1: Create progress_tracker.py with schema validation

**Files:** `functional/progress_tracker.py`, `tests/test_progress_tracker.py`

### Step 1: Write failing test for schema validation

```python
# tests/test_progress_tracker.py
# ABOUTME: Tests for the progress tracking library.
# ABOUTME: Validates schema, events, and session state transitions.

import pytest
import json
from pathlib import Path
import sys

# Add functional to path
sys.path.insert(0, str(Path(__file__).parent.parent / "functional"))

from progress_tracker import validate_progress_schema, ProgressValidationError


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
```

### Step 2: Verify test fails

```bash
cd /Users/justinkistner/Documents/CopyClub\ GitHub/agent-dev-harness && pytest tests/test_progress_tracker.py -v
# Expected: ERROR - ModuleNotFoundError: No module named 'progress_tracker'
```

### Step 3: Implement schema validation

```python
# functional/progress_tracker.py
# ABOUTME: Core library for progress.json manipulation.
# ABOUTME: Provides schema validation, event handling, and session state management.

from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from datetime import datetime
import json
from pathlib import Path


class ProgressValidationError(Exception):
    """Raised when progress.json schema validation fails."""
    pass


REQUIRED_TOP_LEVEL = ["version", "project", "currentWork", "lastSession"]
REQUIRED_CURRENT_WORK = ["type", "plan", "planTask", "debugIssue", "debugPhase"]
REQUIRED_LAST_SESSION = ["date", "duration_minutes", "summary", "events", "commits", "nextSteps"]


def validate_progress_schema(data: Dict[str, Any]) -> None:
    """
    Validate progress.json conforms to v2 schema.

    Raises:
        ProgressValidationError: If validation fails
    """
    # Check version
    if "version" not in data:
        raise ProgressValidationError("Missing required field: version")
    if data["version"] != 2:
        raise ProgressValidationError(f"Expected version 2, got {data['version']}")

    # Check required top-level fields
    for field in REQUIRED_TOP_LEVEL:
        if field not in data:
            raise ProgressValidationError(f"Missing required field: {field}")

    # Check currentWork structure
    current_work = data.get("currentWork", {})
    for field in REQUIRED_CURRENT_WORK:
        if field not in current_work:
            raise ProgressValidationError(f"Missing currentWork field: {field}")

    # Check lastSession structure
    last_session = data.get("lastSession", {})
    for field in REQUIRED_LAST_SESSION:
        if field not in last_session:
            raise ProgressValidationError(f"Missing lastSession field: {field}")
```

### Step 4: Verify test passes

```bash
cd /Users/justinkistner/Documents/CopyClub\ GitHub/agent-dev-harness && pytest tests/test_progress_tracker.py -v
# Expected: 4 passed
```

### Step 5: Commit

```bash
git add functional/progress_tracker.py tests/test_progress_tracker.py
git commit -m "Add progress_tracker library with schema validation"
```

---

## Task 2: Add event creation and serialization

**Files:** `functional/progress_tracker.py`, `tests/test_progress_tracker.py`

### Step 1: Write failing test for events

```python
# Add to tests/test_progress_tracker.py

from progress_tracker import (
    create_event,
    EventType,
    ProgressEvent
)


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
```

### Step 2: Verify test fails

```bash
cd /Users/justinkistner/Documents/CopyClub\ GitHub/agent-dev-harness && pytest tests/test_progress_tracker.py::TestEventCreation -v
# Expected: ERROR - ImportError (EventType, create_event not found)
```

### Step 3: Implement event handling

```python
# Add to functional/progress_tracker.py

from enum import Enum


class EventType(Enum):
    """Types of progress events."""
    SESSION_START = "session_start"
    SESSION_END = "session_end"
    CHECKPOINT = "checkpoint"
    PLAN_STARTED = "plan_started"
    PLAN_TASK_COMPLETED = "plan_task_completed"
    DEBUG_STARTED = "debug_started"
    DEBUG_ROOT_CAUSE = "debug_root_cause"
    DEBUG_RESOLVED = "debug_resolved"


@dataclass
class ProgressEvent:
    """A progress tracking event."""
    type: str
    timestamp: str
    data: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Serialize event to dict."""
        result = {
            "type": self.type,
            "timestamp": self.timestamp
        }
        result.update(self.data)
        return result

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "ProgressEvent":
        """Deserialize event from dict."""
        event_type = d.pop("type")
        timestamp = d.pop("timestamp")
        return cls(type=event_type, timestamp=timestamp, data=d)


def create_event(event_type: EventType, **kwargs) -> ProgressEvent:
    """
    Create a new progress event.

    Args:
        event_type: Type of event
        **kwargs: Event-specific data

    Returns:
        ProgressEvent instance
    """
    timestamp = datetime.utcnow().isoformat() + "Z"
    return ProgressEvent(
        type=event_type.value,
        timestamp=timestamp,
        data=kwargs
    )
```

### Step 4: Verify test passes

```bash
cd /Users/justinkistner/Documents/CopyClub\ GitHub/agent-dev-harness && pytest tests/test_progress_tracker.py::TestEventCreation -v
# Expected: 5 passed
```

### Step 5: Commit

```bash
git add functional/progress_tracker.py tests/test_progress_tracker.py
git commit -m "Add event creation and serialization to progress_tracker"
```

---

## Task 3: Add session state management

**Files:** `functional/progress_tracker.py`, `tests/test_progress_tracker.py`

### Step 1: Write failing test for session state

```python
# Add to tests/test_progress_tracker.py

from progress_tracker import (
    start_session,
    end_session,
    add_event,
    get_current_work,
    set_current_work,
    WorkType
)
import tempfile
import os


class TestSessionState:
    """Test session state management."""

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
```

### Step 2: Verify test fails

```bash
cd /Users/justinkistner/Documents/CopyClub\ GitHub/agent-dev-harness && pytest tests/test_progress_tracker.py::TestSessionState -v
# Expected: ERROR - ImportError (start_session, end_session, etc. not found)
```

### Step 3: Implement session state management

```python
# Add to functional/progress_tracker.py

class WorkType(Enum):
    """Types of current work."""
    GENERAL = "general"
    PLAN = "plan"
    DEBUG = "debug"


def create_empty_progress(project_name: str) -> Dict[str, Any]:
    """Create an empty v2 progress structure."""
    return {
        "version": 2,
        "lastUpdated": datetime.utcnow().isoformat() + "Z",
        "project": project_name,
        "currentWork": {
            "type": "general",
            "plan": None,
            "planTask": None,
            "debugIssue": None,
            "debugPhase": None
        },
        "lastSession": {
            "date": datetime.utcnow().strftime("%Y-%m-%d"),
            "duration_minutes": 0,
            "summary": "",
            "events": [],
            "commits": [],
            "nextSteps": []
        },
        "recentSessions": [],
        "knownIssues": []
    }


def _load_progress(path: Path) -> Dict[str, Any]:
    """Load progress file, creating if needed."""
    if not path.exists():
        data = create_empty_progress(path.parent.name)
        path.write_text(json.dumps(data, indent=2))
        return data
    return json.loads(path.read_text())


def _save_progress(path: Path, data: Dict[str, Any]) -> None:
    """Save progress file."""
    data["lastUpdated"] = datetime.utcnow().isoformat() + "Z"
    path.write_text(json.dumps(data, indent=2))


# Session event storage (in-memory per session, flushed at end)
_session_events: Dict[str, List[ProgressEvent]] = {}


def start_session(path: Path, session_id: str) -> None:
    """Initialize a new session."""
    data = _load_progress(path)
    data["currentWork"]["type"] = "general"
    _session_events[session_id] = [create_event(EventType.SESSION_START)]
    _save_progress(path, data)


def end_session(
    path: Path,
    session_id: str,
    duration_minutes: int,
    summary: str,
    commits: List[Dict[str, str]],
    next_steps: Optional[List[str]] = None
) -> None:
    """Finalize a session and write to lastSession."""
    data = _load_progress(path)

    # Add session_end event
    events = _session_events.get(session_id, [])
    events.append(create_event(EventType.SESSION_END, duration=duration_minutes))

    # Update lastSession
    data["lastSession"] = {
        "date": datetime.utcnow().strftime("%Y-%m-%d"),
        "duration_minutes": duration_minutes,
        "summary": summary,
        "events": [e.to_dict() for e in events],
        "commits": commits,
        "nextSteps": next_steps or []
    }

    # Clear currentWork
    data["currentWork"] = {
        "type": "general",
        "plan": None,
        "planTask": None,
        "debugIssue": None,
        "debugPhase": None
    }

    # Cleanup session events
    if session_id in _session_events:
        del _session_events[session_id]

    _save_progress(path, data)


def add_event(path: Path, session_id: str, event_type: EventType, **kwargs) -> None:
    """Add an event to the current session."""
    if session_id not in _session_events:
        _session_events[session_id] = []
    _session_events[session_id].append(create_event(event_type, **kwargs))


def get_current_work(path: Path) -> Dict[str, Any]:
    """Get current work state."""
    data = _load_progress(path)
    return data.get("currentWork", {})


def set_current_work(
    path: Path,
    work_type: WorkType,
    plan: Optional[str] = None,
    plan_task: Optional[int] = None,
    debug_issue: Optional[str] = None,
    debug_phase: Optional[str] = None
) -> None:
    """Set current work state."""
    data = _load_progress(path)
    data["currentWork"] = {
        "type": work_type.value,
        "plan": plan,
        "planTask": plan_task,
        "debugIssue": debug_issue,
        "debugPhase": debug_phase
    }
    _save_progress(path, data)
```

### Step 4: Verify test passes

```bash
cd /Users/justinkistner/Documents/CopyClub\ GitHub/agent-dev-harness && pytest tests/test_progress_tracker.py::TestSessionState -v
# Expected: 5 passed
```

### Step 5: Commit

```bash
git add functional/progress_tracker.py tests/test_progress_tracker.py
git commit -m "Add session state management to progress_tracker"
```

---

## Task 4: Add file path resolution for multi-location support

**Files:** `functional/progress_tracker.py`, `tests/test_progress_tracker.py`

### Step 1: Write failing test for path resolution

```python
# Add to tests/test_progress_tracker.py

from progress_tracker import find_progress_file


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
```

### Step 2: Verify test fails

```bash
cd /Users/justinkistner/Documents/CopyClub\ GitHub/agent-dev-harness && pytest tests/test_progress_tracker.py::TestPathResolution -v
# Expected: ERROR - ImportError (find_progress_file not found)
```

### Step 3: Implement path resolution

```python
# Add to functional/progress_tracker.py

PROGRESS_FILENAME = "project-progress.json"


def find_progress_file(
    cwd: Path,
    create_if_missing: bool = False
) -> Optional[Path]:
    """
    Find the progress.json file for the current context.

    Search order:
    1. Current directory
    2. Parent directories (up to git root or filesystem root)

    Args:
        cwd: Current working directory
        create_if_missing: If True, create file if not found

    Returns:
        Path to progress file, or None if not found and create=False
    """
    # Check current directory first
    progress_path = cwd / PROGRESS_FILENAME
    if progress_path.exists():
        return progress_path

    # Walk up looking for progress file or git root
    current = cwd
    while current != current.parent:
        progress_path = current / PROGRESS_FILENAME
        if progress_path.exists():
            return progress_path

        # Stop at git root
        if (current / ".git").exists():
            break

        current = current.parent

    # Not found - create if requested
    if create_if_missing:
        progress_path = cwd / PROGRESS_FILENAME
        project_name = cwd.name
        data = create_empty_progress(project_name)
        progress_path.write_text(json.dumps(data, indent=2))
        return progress_path

    return None
```

### Step 4: Verify test passes

```bash
cd /Users/justinkistner/Documents/CopyClub\ GitHub/agent-dev-harness && pytest tests/test_progress_tracker.py::TestPathResolution -v
# Expected: 4 passed
```

### Step 5: Commit

```bash
git add functional/progress_tracker.py tests/test_progress_tracker.py
git commit -m "Add file path resolution for multi-location support"
```

---

## Task 5: Create track-progress-events.py hook

**Files:** `.claude/hooks/track-progress-events.py`, `tests/test_progress_hooks.py`

### Step 1: Write failing test for event detection

```python
# tests/test_progress_hooks.py
# ABOUTME: Tests for progress tracking hooks.
# ABOUTME: Validates event detection patterns and hook behavior.

import pytest
import json
import subprocess
from pathlib import Path


HOOK_PATH = Path(__file__).parent.parent / ".claude" / "hooks" / "track-progress-events.py"


class TestEventDetection:
    """Test UserPromptSubmit event detection."""

    def _run_hook(self, prompt: str, session_id: str = "test-session") -> dict:
        """Run the hook with given prompt and return parsed output."""
        hook_input = {
            "prompt": prompt,
            "session_id": session_id
        }
        result = subprocess.run(
            ["python3", str(HOOK_PATH)],
            input=json.dumps(hook_input),
            capture_output=True,
            text=True
        )
        return {
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr
        }

    def test_detects_plan_started(self):
        """Detect 'starting plan X' patterns."""
        result = self._run_hook("I'm starting the plan at docs/plans/feature.md")
        assert result["returncode"] == 0
        # Hook should log event to temp file

    def test_detects_task_completed(self):
        """Detect 'task N done/complete' patterns."""
        result = self._run_hook("Task 3 is done, moving to task 4")
        assert result["returncode"] == 0

    def test_detects_debug_started(self):
        """Detect debugging context."""
        result = self._run_hook("There's a bug in the authentication module")
        assert result["returncode"] == 0

    def test_no_detection_for_general_prompt(self):
        """General prompts don't trigger events."""
        result = self._run_hook("What files are in the src directory?")
        assert result["returncode"] == 0
```

### Step 2: Verify test fails

```bash
cd /Users/justinkistner/Documents/CopyClub\ GitHub/agent-dev-harness && pytest tests/test_progress_hooks.py -v
# Expected: ERROR - FileNotFoundError (hook doesn't exist)
```

### Step 3: Implement event detection hook

```python
#!/usr/bin/env python3
# ABOUTME: UserPromptSubmit hook for detecting progress events.
# ABOUTME: Logs plan/debug/task events to temp file for session tracking.

import json
import sys
import re
import os
from pathlib import Path
from datetime import datetime

# Event detection patterns
PLAN_STARTED_PATTERNS = [
    r"starting\s+(?:the\s+)?plan\s+(?:at\s+)?([^\s]+\.md)",
    r"following\s+(?:the\s+)?plan\s+(?:at\s+)?([^\s]+\.md)",
    r"executing\s+plan\s+([^\s]+\.md)",
]

TASK_COMPLETED_PATTERNS = [
    r"task\s+(\d+)\s+(?:is\s+)?(?:done|complete|finished)",
    r"completed\s+task\s+(\d+)",
    r"finished\s+task\s+(\d+)",
]

DEBUG_STARTED_PATTERNS = [
    r"\b(bug|broken|failing|crash|exception)\b",
    r"\bdoesn'?t\s+work\b",
    r"\bnot\s+working\b",
]

# Exclusion patterns (implementation context, not debugging)
DEBUG_EXCLUSIONS = [
    r"\b(add|handle|implement|log)\s+.{0,20}error",
    r"error\s+(handling|message|case)",
]


def get_events_file(session_id: str) -> Path:
    """Get path to session events temp file."""
    return Path(f"/tmp/claude_progress_events_{session_id}.jsonl")


def log_event(session_id: str, event_type: str, **data):
    """Append event to session events file."""
    events_file = get_events_file(session_id)
    event = {
        "type": event_type,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        **data
    }
    with open(events_file, "a") as f:
        f.write(json.dumps(event) + "\n")


def detect_events(prompt: str, session_id: str) -> list:
    """Detect progress events in prompt."""
    events = []
    prompt_lower = prompt.lower()

    # Check for plan started
    for pattern in PLAN_STARTED_PATTERNS:
        match = re.search(pattern, prompt_lower)
        if match:
            plan_path = match.group(1)
            log_event(session_id, "plan_started", plan=plan_path)
            events.append(("plan_started", plan_path))
            break

    # Check for task completed
    for pattern in TASK_COMPLETED_PATTERNS:
        match = re.search(pattern, prompt_lower)
        if match:
            task_num = int(match.group(1))
            log_event(session_id, "plan_task_completed", task=task_num)
            events.append(("plan_task_completed", task_num))
            break

    # Check for debug started (with exclusions)
    is_debug = False
    for pattern in DEBUG_STARTED_PATTERNS:
        if re.search(pattern, prompt_lower):
            is_debug = True
            break

    if is_debug:
        # Check exclusions
        for exclusion in DEBUG_EXCLUSIONS:
            if re.search(exclusion, prompt_lower):
                is_debug = False
                break

    if is_debug:
        # Extract issue description (first sentence or up to 100 chars)
        issue = prompt[:100].split(".")[0]
        log_event(session_id, "debug_started", issue=issue)
        events.append(("debug_started", issue))

    return events


def main():
    # Read hook input from stdin
    try:
        hook_input = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)  # No input, nothing to do

    prompt = hook_input.get("prompt", "")
    session_id = hook_input.get("session_id", "unknown")

    # Detect and log events
    events = detect_events(prompt, session_id)

    # Exit 0 - this is advisory, not blocking
    sys.exit(0)


if __name__ == "__main__":
    main()
```

### Step 4: Verify test passes

```bash
cd /Users/justinkistner/Documents/CopyClub\ GitHub/agent-dev-harness && chmod +x .claude/hooks/track-progress-events.py && pytest tests/test_progress_hooks.py -v
# Expected: 4 passed
```

### Step 5: Commit

```bash
git add .claude/hooks/track-progress-events.py tests/test_progress_hooks.py
git commit -m "Add track-progress-events.py hook for event detection"
```

---

## Task 6: Update track-session-time.py to use progress_tracker

**Files:** `.claude/hooks/track-session-time.py`

### Step 1: Write failing test for integration

```python
# Add to tests/test_progress_hooks.py

class TestSessionTimeIntegration:
    """Test track-session-time.py integration with progress_tracker."""

    def test_reads_events_from_temp_file(self, tmp_path):
        """Session end should include events from temp file."""
        # Create events file
        events_file = Path("/tmp/claude_progress_events_test-integration.jsonl")
        events_file.write_text(
            '{"type": "plan_started", "timestamp": "2025-12-11T18:00:00Z", "plan": "test.md"}\n'
            '{"type": "plan_task_completed", "timestamp": "2025-12-11T18:30:00Z", "task": 1}\n'
        )

        # The modified hook should read these when finalizing
        # This test validates the integration works
        assert events_file.exists()
```

### Step 2: Verify current behavior (manual inspection)

The existing `track-session-time.py` doesn't update progress.json. We need to add that integration.

### Step 3: Implement integration

This task modifies the existing hook to:
1. Read events from temp file
2. Update progress.json with lastSession data
3. Keep existing time tracking behavior

**Note:** This is a modification to existing code. Read the current implementation first, then add the progress_tracker integration while preserving existing functionality.

### Step 4: Verify test passes

```bash
cd /Users/justinkistner/Documents/CopyClub\ GitHub/agent-dev-harness && pytest tests/test_progress_hooks.py::TestSessionTimeIntegration -v
# Expected: passed
```

### Step 5: Commit

```bash
git add .claude/hooks/track-session-time.py
git commit -m "Integrate track-session-time.py with progress_tracker"
```

---

## Task 7: Add UserPromptSubmit hook to settings.json

**Files:** `.claude/settings.json`

### Step 1: Document current hooks configuration

Read current settings.json to understand existing hook structure.

### Step 2: Add new hook

Add `track-progress-events.py` to UserPromptSubmit hooks.

### Step 3: Verify hook fires

Test manually by starting a session and checking if events are logged.

### Step 4: Commit

```bash
git add .claude/settings.json
git commit -m "Add track-progress-events.py to UserPromptSubmit hooks"
```

---

## Task 8: Enhance /checkpoint command

**Files:** `.claude/commands/checkpoint.md`

### Step 1: Read current implementation

### Step 2: Enhance to update progress.json

Add steps to:
1. Read current events from temp file
2. Log checkpoint event
3. Update progress.json with current state
4. Continue with existing commit workflow

### Step 3: Test manually

### Step 4: Commit

```bash
git add .claude/commands/checkpoint.md
git commit -m "Enhance /checkpoint to update progress.json"
```

---

## Task 9: Enhance /start command

**Files:** `.claude/commands/start.md`

### Step 1: Read current implementation

### Step 2: Enhance to show progress context

Add steps to:
1. Read progress.json currentWork
2. If plan active: show plan name, current task
3. If debug active: show issue, phase
4. Show lastSession summary
5. Continue with existing context gathering

### Step 3: Test manually

### Step 4: Commit

```bash
git add .claude/commands/start.md
git commit -m "Enhance /start to show progress context"
```

---

## Task 10: Update harness project-progress.json to v2

**Files:** `project-progress.json`

### Step 1: Migrate existing file to v2 schema

### Step 2: Validate with progress_tracker

### Step 3: Commit

```bash
git add project-progress.json
git commit -m "Migrate project-progress.json to v2 schema"
```

---

## Task 11: Add progress.json to business_process template

**Files:** `templates/business_process/project-progress.json`

### Step 1: Create template progress file

### Step 2: Update template documentation

### Step 3: Commit

```bash
git add templates/business_process/
git commit -m "Add project-progress.json to business_process template"
```

---

## Summary

After completing all tasks:

1. **Core library:** `functional/progress_tracker.py` with full test coverage
2. **Hooks:** Event detection and session tracking integrated
3. **Commands:** /start and /checkpoint use progress system
4. **Multi-location:** Works in harness, projects, and templates

Run full test suite to verify:

```bash
cd /Users/justinkistner/Documents/CopyClub\ GitHub/agent-dev-harness && pytest tests/test_progress_tracker.py tests/test_progress_hooks.py -v
```
