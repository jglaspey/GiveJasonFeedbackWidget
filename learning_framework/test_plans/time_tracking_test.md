# Time Tracking Test Protocol

## Objective
Validate time tracking behavior across different scenarios to fix the "7 minutes for hours of work" bug.

## Test 1: Session ID Persistence Across Context Continuation

**Question:** Does session_id change when context runs out and session continues?

**Setup:**
1. Create a script that logs session_id on every UserPromptSubmit:

```python
# .claude/hooks/log-session-id.py
#!/usr/bin/env python3
import json
import sys
from datetime import datetime
from pathlib import Path

input_data = json.load(sys.stdin)
session_id = input_data.get('session_id', 'unknown')

log_file = Path('/tmp/session_id_log.txt')
with open(log_file, 'a') as f:
    f.write(f"{datetime.now().isoformat()} | {session_id}\n")

sys.exit(0)
```

2. Add to settings.json UserPromptSubmit hooks (temporarily)

**Execution:**
1. Start fresh Claude Code session
2. Note initial session_id from log
3. Have a long conversation or artificially exhaust context
4. When context continues with summary, check log for new session_id
5. Compare before/after

**Success Criteria:**
- If session_id SAME: f2 is not a problem, focus on f1
- If session_id DIFFERENT: Need cross-session tracking

---

## Test 2: Current Cleanup Behavior

**Question:** Does deleting the session file cause the next message to reset the clock?

**Setup:** Use existing hooks, just observe carefully

**Execution:**
1. Start session, note start time in `/tmp/claude_session_start_*`
2. Work for 10+ minutes
3. Trigger stop (should show ~10 minutes)
4. Let time-tracker run, it will log and delete file
5. Send another message
6. Check if new `/tmp/claude_session_start_*` was created
7. Try to stop again - what duration shows?

**Success Criteria:**
- Confirm that step 5 creates new session file
- Confirm that step 7 shows only time since step 5, not cumulative

---

## Test 3: Marker File Approach (h5)

**Question:** Can we use a separate marker to allow stop while preserving session start?

**Setup:**
Modify hooks:

```python
# track-session-time.py changes:
# Instead of just blocking, check for logged marker first

logged_marker = Path('/tmp') / f'claude_session_logged_{session_id}'
if logged_marker.exists():
    # Already logged this session, allow stop
    sys.exit(0)

# ... rest of existing logic (block and prompt)
```

```python
# time-tracker subagent changes:
# Create marker instead of deleting start file

# After writing time entry:
logged_marker = Path('/tmp') / f'claude_session_logged_{session_id}'
logged_marker.write_text(datetime.now().isoformat())
# DON'T delete the start file
```

```python
# session-start-tracking.py changes:
# Clean up OLD session files (not current session)

import glob
current_session = input_data.get('session_id', '')

# Clean up any session files that aren't the current session
for f in glob.glob('/tmp/claude_session_start_*'):
    if current_session not in f:
        Path(f).unlink(missing_ok=True)
for f in glob.glob('/tmp/claude_session_logged_*'):
    if current_session not in f:
        Path(f).unlink(missing_ok=True)
```

**Execution:**
1. Start session
2. Work for 10 minutes
3. Stop - should block, show 10 minutes
4. Invoke time-tracker - logs entry, creates marker
5. Stop again - should ALLOW (marker exists)
6. Continue working for 5 more minutes
7. Stop - what happens?
   - If marker still exists: allows stop (might miss 5 min)
   - Need to clear marker on new work? Or track cumulative?

**Decision Point:**
After logging, should subsequent stops:
a) Always allow (accept that post-log work might not be tracked)
b) Block again if significant new work detected (check git?)
c) Show cumulative time and ask if want to log more

---

## Test 4: Git-Based Time Validation (h3)

**Question:** How accurate is git commit timestamp-based time tracking?

**Setup:** No code changes needed, just analysis

**Execution:**
1. Manually record actual session start time
2. Work for a known duration (use a timer)
3. Make several commits during the session
4. At end, compare:
   - Actual elapsed time (from timer)
   - Time from first to last commit
   - Time from session file

**Success Criteria:**
- Document the gap between commit-based and actual time
- Determine if git-based is "good enough" as primary or backup

---

## Recommended Test Order

1. **Test 2 first** - Confirm the bug mechanism (5 minutes)
2. **Test 1 second** - Understand session_id behavior (requires context exhaustion)
3. **Test 3 third** - Implement and validate fix (30 minutes)
4. **Test 4 optional** - Enhancement for accuracy

---

## Quick Test 2 Protocol (Do This Now)

We can run Test 2 right now:

1. Check current session file:
   ```bash
   cat /tmp/claude_session_start_*
   ```

2. Note the timestamp

3. I'll invoke time-tracker (which should delete the file)

4. You send another message

5. Check if new session file exists:
   ```bash
   ls -la /tmp/claude_session_start_*
   cat /tmp/claude_session_start_*
   ```

6. Compare timestamps

Ready to run Test 2?
