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
