# Checkpoint

Mid-session checkpoint to save progress, commit changes, and optionally create/update a PR.

## Steps

### 1. Log Checkpoint Event
Log a checkpoint event to track this save point:
```python
# Using progress_tracker library
from functional.progress_tracker import find_progress_file, add_event, EventType
import os

progress_path = find_progress_file(Path.cwd())
if progress_path:
    session_id = os.environ.get('CLAUDE_SESSION_ID', 'unknown')
    add_event(progress_path, session_id, EventType.CHECKPOINT, summary="Mid-session checkpoint")
```

Or append directly to events temp file:
```bash
echo '{"type":"checkpoint","timestamp":"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'","summary":"checkpoint description"}' >> /tmp/claude_progress_events_${CLAUDE_SESSION_ID}.jsonl
```

### 2. Update Progress File
Update `project-progress.json` with current session state:
- Update `currentWork` to reflect current activity (plan, debug, or general)
- Summarize what was accomplished
- Record completed tasks (check TodoWrite)
- Note any blockers encountered
- Define next steps

### 3. Run Verification (if applicable)
If the project has tests:
```bash
# Run tests appropriate to the project
npm test || pytest || go test ./...
```

Report results before proceeding.

### 4. Git Operations
Check what needs to be committed:
```bash
git status
```

If there are changes and verification passed (or no tests):
```bash
git add -A && git status
```

Create a descriptive commit using the git-operations skill.

### 5. Push Changes
```bash
git push
```

### 6. PR Management (if on feature branch)
Check if we're on a feature branch:
```bash
git branch --show-current
```

If on a feature branch (not main/master):
- Check for existing PR: `gh pr list --head $(git branch --show-current)`
- If no PR exists, offer to create one
- If PR exists, update description with progress

### 7. Report
Output summary:
```
## Checkpoint Complete

**Commit:** [hash] - [message]
**Branch:** [branch name]
**PR:** [URL or "none"]
**Tests:** [passed/failed/skipped]

**Progress Updated:**
- Completed: [list]
- Blockers: [list or "none"]
- Next: [list]
```

---

## Arguments

- `/checkpoint` - Full checkpoint with PR check
- `/checkpoint quick` - Just commit and push, skip PR
- `/checkpoint pr` - Force PR creation/update
