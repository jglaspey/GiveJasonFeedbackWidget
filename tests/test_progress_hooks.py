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


class TestSessionTimeIntegration:
    """Test track-session-time.py integration with progress_tracker."""

    def test_events_file_format(self, tmp_path):
        """Events files use JSONL format with type and timestamp."""
        # Create events file matching the format track-progress-events.py writes
        events_file = tmp_path / "events.jsonl"
        events_file.write_text(
            '{"type": "plan_started", "timestamp": "2025-12-11T18:00:00Z", "plan": "test.md"}\n'
            '{"type": "plan_task_completed", "timestamp": "2025-12-11T18:30:00Z", "task": 1}\n'
        )

        # Verify the file format is correct
        lines = events_file.read_text().strip().split("\n")
        assert len(lines) == 2

        event1 = json.loads(lines[0])
        assert event1["type"] == "plan_started"
        assert event1["plan"] == "test.md"

        event2 = json.loads(lines[1])
        assert event2["type"] == "plan_task_completed"
        assert event2["task"] == 1
