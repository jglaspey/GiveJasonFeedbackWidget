#!/usr/bin/env python3
# ABOUTME: Stop hook that prompts time tracking after session ends
# ABOUTME: Blocks stopping and prompts agent to invoke time-tracker subagent

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

    # Check if start time exists
    start_file = Path('/tmp') / f'claude_session_start_{session_id}'
    logged_marker = Path('/tmp') / f'claude_session_logged_{session_id}'

    # If time was already logged this session, allow stop
    if logged_marker.exists():
        sys.exit(0)

    if not start_file.exists():
        # No start time, skip tracking
        sys.exit(0)

    # Calculate duration (using UTC for consistency)
    try:
        start_time = datetime.fromisoformat(start_file.read_text().strip())
        end_time = datetime.now(timezone.utc)
        duration_minutes = int((end_time - start_time).total_seconds() / 60)
    except Exception:
        # If we can't parse start time, skip
        start_file.unlink(missing_ok=True)
        sys.exit(0)

    # For short sessions (< 5 min), update progress.json directly and allow exit
    skip_time_log = duration_minutes < 5

    if skip_time_log:
        # Update progress.json directly for short sessions
        import os
        project_dir = os.environ.get('CLAUDE_PROJECT_DIR', os.getcwd())
        progress_path = Path(project_dir) / 'project-progress.json'
        if progress_path.exists():
            try:
                data = json.loads(progress_path.read_text())
                data['lastSession']['date'] = datetime.now(timezone.utc).strftime('%Y-%m-%d')
                data['lastSession']['duration_minutes'] = duration_minutes
                data['lastUpdated'] = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
                progress_path.write_text(json.dumps(data, indent=2))
                print(f'⏱️  Short session ({duration_minutes} min) - updated progress.json', file=sys.stderr)
            except Exception as e:
                print(f'⏱️  Short session ({duration_minutes} min) - failed to update progress.json: {e}', file=sys.stderr)

        # Create logged marker and allow clean exit
        logged_marker.touch()
        start_file.unlink(missing_ok=True)
        sys.exit(0)
    else:
        message = f"""
⏱️  Time Tracking

Session duration: {duration_minutes} minutes

Please use the time-tracker subagent to record this work session.

The time-tracker subagent will analyze your commits and create a time log entry.
""".strip()

    print(message, file=sys.stderr)

    # Exit code 2 blocks stopping and shows message to Claude
    sys.exit(2)

if __name__ == '__main__':
    main()
