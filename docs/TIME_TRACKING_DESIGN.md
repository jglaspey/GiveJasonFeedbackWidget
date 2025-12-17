# Time Tracking Subagent - Design

## Overview

A specialized subagent for tracking development time with work descriptions, integrated with git commits and session lifecycle.

## Architecture

### Component: Time Tracking Subagent

**Purpose:** Capture time spent on development activities with clear descriptions

**Location:** `.claude/agents/time-tracker.md`

**Invocation Points:**
1. SessionStart hook - Log session start time
2. Stop hook (after git operations) - Prompt main agent to invoke time-tracker subagent
3. Manual invocation - User explicitly asks to log time

**Data Captured:**
- Session start time
- Session end time
- Duration (calculated)
- Work description (from conversation context or git commits)
- Files changed (from git status/diff)
- Commits made (from git log)
- Session ID (for traceability)

## Storage

### Time Log Format (JSON Lines)

File: `outputs/time_logs/YYYY-MM.jsonl` (monthly files)

```json
{
  "timestamp": "2025-01-15T14:30:22Z",
  "duration_minutes": 45,
  "session_id": "abc123",
  "description": "Implement user authentication endpoint with tests",
  "files_changed": ["src/auth.py", "tests/test_auth.py"],
  "commits": [
    {
      "hash": "a1b2c3d",
      "message": "Add user authentication endpoint"
    },
    {
      "hash": "e4f5g6h",
      "message": "Add tests for authentication"
    }
  ],
  "tags": ["feature", "auth", "backend"]
}
```

## Subagent Definition

### `.claude/agents/time-tracker.md`

```markdown
---
name: time-tracker
description: Time tracking specialist. Use when session ends to create time log entries from git activity and conversation context. MUST be used when user requests time tracking or when Stop hook prompts for time entry.
tools: Read, Grep, Bash, Write
model: sonnet
---

# Time Tracking Specialist

You are a time tracking specialist. Your job is to create accurate time log entries for development sessions.

## Your Responsibilities

When invoked, you should:

1. **Read session start time** from `/tmp/claude_session_start_{session_id}`
   - Parse the ISO timestamp
   - Calculate duration from start to now

2. **Analyze git activity** to understand what was accomplished:
   ```bash
   # Get recent commits (since session start)
   git log --since="TIMESTAMP" --pretty=format:"%H|%s"

   # Get files changed
   git diff --name-status HEAD~N HEAD
   ```

3. **Generate work description**:
   - Review commit messages
   - Analyze files changed
   - Create a concise 1-2 sentence description focusing on WHAT was done
   - Examples:
     - "Implement user authentication endpoint with tests"
     - "Fix validation bug in registration form"
     - "Refactor database query layer for better performance"

4. **Extract tags** from the work done:
   - feature, bugfix, refactor, docs, test, config, etc.
   - Be specific: auth, api, frontend, backend, database, etc.

5. **Write time entry** to `outputs/time_logs/YYYY-MM.jsonl`:
   ```json
   {
     "timestamp": "2025-01-15T15:15:00Z",
     "duration_minutes": 45,
     "session_id": "abc123",
     "description": "Your concise description here",
     "files_changed": ["file1.py", "file2.py"],
     "commits": [
       {"hash": "a1b2c3d", "message": "Commit message"}
     ],
     "tags": ["feature", "auth", "backend"]
   }
   ```

6. **Create directory if needed**:
   ```bash
   mkdir -p outputs/time_logs
   ```

7. **Confirm with user** before writing:
   - Show the time entry you're about to write
   - Ask if description is accurate
   - Allow user to edit description or tags
   - Then append to the file

## Important Notes

- **Duration threshold**: Don't create entries for sessions < 5 minutes
- **File format**: JSON Lines (one JSON object per line, no commas between)
- **Timestamps**: Use ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ)
- **Concise descriptions**: Focus on business value, not technical details
- **Monthly files**: One file per month (YYYY-MM.jsonl)
- **Append mode**: Always append, never overwrite existing entries

## Example Session

User: "Create a time entry for this session"

You:
1. Read `/tmp/claude_session_start_abc123` → "2025-01-15T14:30:00Z"
2. Calculate duration: 45 minutes
3. Run `git log --since="2025-01-15T14:30:00Z"` → Find 2 commits
4. Generate description from commits
5. Present to user:

```
Time Entry:
- Duration: 45 minutes
- Description: "Implement user authentication endpoint with tests"
- Files: src/auth.py, tests/test_auth.py
- Commits:
  - a1b2c3d: Add user authentication endpoint
  - e4f5g6h: Add tests for authentication
- Tags: feature, auth, backend

Is this description accurate? (y/n/edit)
```

6. If user confirms, append to `outputs/time_logs/2025-01.jsonl`
7. Clean up: Delete `/tmp/claude_session_start_abc123`
```

## Hook Integration

### Hook 1: SessionStart Hook

**Purpose:** Record session start time

**Script:** `.claude/hooks/session-start-tracking.py`

**Logic:**
```python
#!/usr/bin/env python3
import json
import sys
from datetime import datetime
from pathlib import Path

def main():
    input_data = json.load(sys.stdin)
    session_id = input_data.get('session_id', '')

    # Write start time to temp file
    start_file = Path('/tmp') / f'claude_session_start_{session_id}'
    start_file.write_text(datetime.now().isoformat())

    sys.exit(0)

if __name__ == '__main__':
    main()
```

**Configuration:**
```json
{
  "hooks": {
    "SessionStart": [{
      "hooks": [{
        "type": "command",
        "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/session-start-tracking.py"
      }]
    }]
  }
}
```

### Hook 2: Stop Hook Enhancement

**Purpose:** After git operations complete, prompt for time tracking

**Script:** `.claude/hooks/track-session-time.py`

**Logic:**
```python
#!/usr/bin/env python3
import json
import sys
from datetime import datetime
from pathlib import Path

def main():
    input_data = json.load(sys.stdin)
    session_id = input_data.get('session_id', '')

    # Check if start time exists
    start_file = Path('/tmp') / f'claude_session_start_{session_id}'
    if not start_file.exists():
        # No start time, skip tracking
        sys.exit(0)

    # Calculate duration
    start_time = datetime.fromisoformat(start_file.read_text())
    end_time = datetime.now()
    duration_minutes = int((end_time - start_time).total_seconds() / 60)

    # If session was < 5 minutes, skip tracking
    if duration_minutes < 5:
        start_file.unlink()  # Clean up
        sys.exit(0)

    # Block stoppage and prompt agent to use time-tracker subagent
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
```

**Configuration:**
```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [{
          "type": "command",
          "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/final-commit-check.py"
        }]
      },
      {
        "hooks": [{
          "type": "command",
          "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/track-session-time.py"
        }]
      }
    ]
  }
}
```

**Note:** Time tracking runs AFTER commit check, ensuring all commits are captured.

## Workflow Examples

### Example 1: Feature Development Session

```
1. User starts Claude Code
   → [SessionStart hook] Records start time to /tmp/claude_session_start_abc123

2. Agent implements feature
3. Agent writes tests
4. Agent runs tests → pass
   → [PostToolUse hook] Prompts to commit

5. Agent launches git subagent
6. Git subagent creates commit
   → [SubagentStop hook] Verifies commit

7. Agent says "feature complete"
   → [Stop hook - commit check] All changes committed ✓
   → [Stop hook - time tracking] Blocks and prompts:

⏱️  Time Tracking
Session duration: 45 minutes
Please use the time-tracker subagent to record this work session.

8. Main agent: "Use time-tracker subagent to create time entry"

9. Time-tracker subagent launches:
   - Reads /tmp/claude_session_start_abc123
   - Runs git log --since="2025-01-15T14:30:00Z"
   - Analyzes commits
   - Generates description
   - Presents to user:

Time Entry:
- Duration: 45 minutes
- Description: "Implement user authentication endpoint with tests"
- Files: src/auth.py, tests/test_auth.py
- Commits: a1b2c3d "Add user authentication endpoint"
- Tags: feature, auth, backend

Is this accurate? (y/n/edit)

10. User confirms
11. Subagent appends to outputs/time_logs/2025-01.jsonl
12. Subagent deletes /tmp/claude_session_start_abc123
13. Session ends
```

### Example 2: Bug Fix Session

```
1. User: "Fix the validation bug in forms"
   → [SessionStart hook] Records start time

2. Agent investigates, finds bug, fixes it
3. Agent runs tests → pass
   → [PostToolUse hook] Prompts to commit

4. Agent commits via git subagent

5. Agent: "Bug fixed"
   → [Stop hook - time tracking] Prompts for time entry

6. Time-tracker subagent creates entry:

Time Entry:
- Duration: 20 minutes
- Description: "Fix validation bug in user registration form"
- Files: src/forms/validation.py
- Commits: x9y8z7w "Fix email validation regex"
- Tags: bugfix, forms, validation

7. User confirms, entry logged
```

### Example 3: Multiple Features in One Session

```
1. Session starts
   → [SessionStart hook] Records start

2. Implement feature A → commit
3. Implement feature B → commit
4. Implement feature C → commit

5. Agent: "All features complete"
   → [Stop hook - time tracking] Prompts for time entry

6. Time-tracker subagent analyzes all commits:

Time Entry:
- Duration: 120 minutes
- Description: "Implement user authentication, profile page, and settings API"
- Files: [15 files changed]
- Commits:
  - a1b2c3d "Add user authentication"
  - e4f5g6h "Add profile page"
  - i7j8k9l "Add settings API endpoint"
- Tags: feature, auth, frontend, api

Is this accurate? (y/n/edit)

7. User can adjust description if needed
8. Entry logged with all commits captured
```

## Reporting

### Monthly Report Script

File: `functional/scripts/generate_time_report.py`

```python
#!/usr/bin/env python3
# ABOUTME: Generates time reports from time log files
# ABOUTME: Summarizes work done by day, week, or month

import json
from pathlib import Path
from collections import defaultdict
from datetime import datetime

def generate_monthly_report(year: int, month: int):
    """Generate report for a specific month."""

    log_file = Path(f'outputs/time_logs/{year}-{month:02d}.jsonl')

    if not log_file.exists():
        print(f"No time logs found for {year}-{month:02d}")
        return

    # Read all entries
    entries = []
    with log_file.open('r') as f:
        for line in f:
            entries.append(json.loads(line))

    # Calculate totals
    total_minutes = sum(e['duration_minutes'] for e in entries)
    total_hours = total_minutes / 60

    # Group by tag
    by_tag = defaultdict(int)
    for entry in entries:
        for tag in entry.get('tags', []):
            by_tag[tag] += entry['duration_minutes']

    # Print report
    print(f"\n=== Time Report for {year}-{month:02d} ===\n")
    print(f"Total Time: {total_hours:.1f} hours ({total_minutes} minutes)")
    print(f"Sessions: {len(entries)}")
    print(f"\nTime by Category:")
    for tag, minutes in sorted(by_tag.items(), key=lambda x: -x[1]):
        hours = minutes / 60
        print(f"  {tag}: {hours:.1f} hours")

    print(f"\nRecent Work:")
    for entry in entries[-10:]:
        date = datetime.fromisoformat(entry['timestamp']).strftime('%Y-%m-%d')
        duration = entry['duration_minutes']
        desc = entry['description']
        print(f"  [{date}] {duration}min - {desc}")

if __name__ == '__main__':
    import sys
    if len(sys.argv) >= 3:
        year = int(sys.argv[1])
        month = int(sys.argv[2])
    else:
        now = datetime.now()
        year = now.year
        month = now.month

    generate_monthly_report(year, month)
```

**Usage:**
```bash
# Current month
python functional/scripts/generate_time_report.py

# Specific month
python functional/scripts/generate_time_report.py 2025 1
```

## Complete Hook Configuration

Add to `.claude/settings.json`:

```json
{
  "hooks": {
    "SessionStart": [{
      "hooks": [{
        "type": "command",
        "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/session-start-tracking.py"
      }]
    }],
    "PreToolUse": [{
      "matcher": "Bash|Write|Edit",
      "hooks": [{
        "type": "command",
        "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/validate-git-command.py"
      }]
    }],
    "PostToolUse": [{
      "matcher": "Bash",
      "hooks": [{
        "type": "command",
        "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/post-test-commit-check.py"
      }]
    }],
    "SubagentStop": [{
      "hooks": [{
        "type": "command",
        "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/verify-git-subagent.py"
      }]
    }],
    "Stop": [
      {
        "hooks": [{
          "type": "command",
          "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/final-commit-check.py"
        }]
      },
      {
        "hooks": [{
          "type": "command",
          "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/track-session-time.py"
        }]
      }
    ]
  }
}
```

## Future Enhancements

1. **Invoice Generation:** Convert time logs to invoices
2. **Project Breakdown:** Track time per project/feature
3. **Client Billing:** Associate entries with clients
4. **Jira/GitHub Integration:** Link to issue trackers
5. **Calendar Integration:** Sync with Google Calendar
6. **Analytics:** Visualize time distribution

## Version History

- 1.0.0: Initial design for time tracking subagent with hook integration (corrected to use proper subagent architecture)
