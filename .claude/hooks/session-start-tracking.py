#!/usr/bin/env python3
# ABOUTME: SessionStart hook that records session start time for time tracking
# ABOUTME: Writes timestamp to /tmp for later retrieval by time-tracker subagent

import glob
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

def main():
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f'Error: Invalid JSON input: {e}', file=sys.stderr)
        sys.exit(1)

    session_id = input_data.get('session_id', '')

    if not session_id:
        # No session ID, skip
        sys.exit(0)

    # Clean up session files from OTHER sessions (not current)
    for pattern in ['/tmp/claude_session_start_*', '/tmp/claude_session_logged_*']:
        for f in glob.glob(pattern):
            if session_id not in f:
                Path(f).unlink(missing_ok=True)

    # Write start time to temp file (UTC for consistent time tracking)
    # Only write if file doesn't exist (preserve original start time)
    start_file = Path('/tmp') / f'claude_session_start_{session_id}'
    if not start_file.exists():
        start_file.write_text(datetime.now(timezone.utc).isoformat())

    # Exit cleanly (no output)
    sys.exit(0)

if __name__ == '__main__':
    main()
