# ABOUTME: Hook integration, enforcement mechanisms, and hook troubleshooting
# ABOUTME: Referenced from git-operations skill when dealing with hook-related issues

# Hook Enforcement

This skill is **enforced** by hook scripts. See `.claude/hooks/` for implementations.

## Hook 1: validate-git-command.py (PreToolUse on Bash)

**Purpose:** Block dangerous git commands before execution

**Blocks:**
- `git reset --hard`
- `git push --force` to main/master
- `git clean -fd`
- Edits to `.env` files
- Other destructive operations

**Exit code 2:** Blocks tool call and shows reason to Claude

### Example

```python
# In .claude/hooks/validate-git-command.py
if "git reset --hard" in command:
    print("ERROR: git reset --hard is destructive. Get explicit approval first.")
    sys.exit(2)  # Block the command
```

## Hook 2: post-test-commit-check.py (PostToolUse on Bash)

**Purpose:** Prompt commits after tests pass

**Logic:**
1. Detect test command (`pytest`, `npm test`, etc.)
2. Check exit code (only proceed if passed)
3. Check git status (uncommitted changes?)
4. Check transcript (feature complete?)
5. If yes: Block with reason "Tests passed, please commit"

**Exit code 2:** Blocks continuation and prompts commit

### Example

```python
# In .claude/hooks/post-test-commit-check.py
if test_passed and has_uncommitted_changes and feature_complete:
    print("Tests passed and you have uncommitted changes. Please commit.")
    sys.exit(2)  # Prompt commit
```

## Hook 3: verify-git-subagent.py (SubagentStop)

**Purpose:** Verify git subagent completed expected commit

**Logic:**
1. Check if this was a git-operations subagent
2. Verify commit was made (check git log)
3. Verify no uncommitted changes remain
4. If failed: Block with reason

**Exit code 2:** Blocks subagent completion

### Example

```python
# In .claude/hooks/verify-git-subagent.py
if is_git_subagent and not commit_made:
    print("Git subagent did not create expected commit.")
    sys.exit(2)  # Block completion
```

## Hook 4: final-commit-check.py (Stop)

**Purpose:** Final safety net for uncommitted changes

**Logic:**
1. Check git status
2. If uncommitted changes exist: Block with reason
3. Prompt: "You have uncommitted work, please commit"

**Exit code 2:** Blocks agent stopping

### Example

```python
# In .claude/hooks/final-commit-check.py
if has_uncommitted_changes:
    print("You have uncommitted work, please commit before stopping.")
    sys.exit(2)  # Block stopping
```

## Troubleshooting Hooks

### Problem: "Tests passed but hook isn't prompting commit"

**Possible reasons:**
1. Hook script not executable: `chmod +x .claude/hooks/*.py`
2. Hook not registered: Check `.claude/settings.json`
3. Test command not recognized: Update hook script patterns

**How to check:**
```bash
# Check if hooks are executable
ls -l .claude/hooks/*.py

# Check settings.json for hook registration
cat .claude/settings.json | grep -A 10 hooks
```

### Problem: "Hook blocked my command but shouldn't have"

**Debug steps:**
1. Check the hook script for the blocking condition
2. Review the exact command that was blocked
3. Verify the hook is correctly identifying the pattern
4. Update hook logic if needed

### Problem: "Hook isn't running at all"

**Check:**
1. Hook is registered in `.claude/settings.json`
2. Hook script has correct shebang: `#!/usr/bin/env python3`
3. Hook script is executable: `chmod +x .claude/hooks/<hook>.py`
4. Hook script has no syntax errors: `python3 .claude/hooks/<hook>.py`

## Hook Configuration

### Registering Hooks in settings.json

```json
{
  "hooks": {
    "preToolUse": [
      {
        "tool": "Bash",
        "command": "python3 .claude/hooks/validate-git-command.py"
      }
    ],
    "postToolUse": [
      {
        "tool": "Bash",
        "command": "python3 .claude/hooks/post-test-commit-check.py"
      }
    ],
    "subagentStop": [
      {
        "command": "python3 .claude/hooks/verify-git-subagent.py"
      }
    ],
    "stop": [
      {
        "command": "python3 .claude/hooks/final-commit-check.py"
      }
    ]
  }
}
```

### Hook Exit Codes

- **Exit 0**: Allow operation to proceed
- **Exit 1**: Error occurred (operation fails)
- **Exit 2**: Block operation and show message to Claude

### Hook Environment

Hooks receive context through:
- **stdin**: JSON with tool call details (for PreToolUse/PostToolUse)
- **Environment variables**: Additional context
- **File system**: Can read project files, git status, etc.
