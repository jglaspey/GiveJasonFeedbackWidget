# ABOUTME: Core library for progress.json manipulation.
# ABOUTME: Provides schema validation, event handling, and session state management.

from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import json
from pathlib import Path


class ProgressValidationError(Exception):
    """Raised when progress.json schema validation fails."""
    pass


REQUIRED_TOP_LEVEL = ["version", "project", "currentWork", "lastSession"]
REQUIRED_CURRENT_WORK = ["type", "plan", "planTask", "debugIssue", "debugPhase"]
# Note: featureId is optional for backwards compatibility
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
    FEATURE_STARTED = "feature_started"
    FEATURE_COMPLETED = "feature_completed"


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
        d = d.copy()  # Don't modify original
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


class WorkType(Enum):
    """Types of current work."""
    GENERAL = "general"
    PLAN = "plan"
    DEBUG = "debug"
    FEATURE = "feature"


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
    debug_phase: Optional[str] = None,
    feature_id: Optional[str] = None
) -> None:
    """Set current work state."""
    data = _load_progress(path)
    data["currentWork"] = {
        "type": work_type.value,
        "plan": plan,
        "planTask": plan_task,
        "debugIssue": debug_issue,
        "debugPhase": debug_phase,
        "featureId": feature_id
    }
    _save_progress(path, data)


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
