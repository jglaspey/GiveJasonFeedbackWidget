# ABOUTME: Commit workflow, timing decisions, message format, and atomic commit patterns
# ABOUTME: Referenced from git-operations skill when creating commits

# Commit Workflow and Best Practices

## When to Commit

### Commit After Each Logical Unit

**Always commit after:**
- ✅ Implementing a feature + tests pass
- ✅ Fixing a bug + tests pass
- ✅ Refactoring + tests still pass
- ✅ Adding documentation for a feature
- ✅ Completing a subtask in a larger feature

**Don't wait to commit:**
- ❌ "I'll commit when the whole feature is done" (too large)
- ❌ "I'll commit at the end of the day" (too infrequent)
- ❌ "I'll commit when the user asks" (too late)

**Enforcement:** PostToolUse hook (on test completion) prompts you to commit.

### Atomic Commits

**Each commit should:**
- Represent one logical change
- Be independently understandable
- Have tests passing
- Be clearly described

```bash
# ✅ GOOD - Atomic commits
git commit -m "Add user authentication endpoint"
git commit -m "Add tests for authentication endpoint"
git commit -m "Update API documentation for auth"

# ❌ BAD - Monolithic commit
git commit -m "Add auth, fix bugs, update docs, refactor tests"
```

## Commit Message Format

### Good Commit Messages

```
Add parallel processing support for large datasets

Implements worker pool pattern with SQLite coordination.
Tests show 10x speedup on 1000+ item datasets.

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>
```

### Format Structure

1. **Subject line** (50 chars): Action verb + what changed
2. **Blank line**
3. **Body** (72 char lines): Why changed, impact, relevant details
4. **Blank line**
5. **Attribution**

### Action Verbs

- `Add` - New feature/file
- `Update` - Enhancement to existing feature
- `Fix` - Bug fix
- `Refactor` - Code restructure, no behavior change
- `Remove` - Delete feature/file
- `Document` - Documentation only

## Coordination Patterns

### Pattern: Multi-Agent Work

**When multiple agents are working:**
1. Each agent commits their work atomically
2. Before touching shared files, check git log
3. If conflict potential, coordinate explicitly
4. Use descriptive commit messages so others understand

### Pattern: Main Agent → Git Subagent

**Typical workflow:**
```
Main Agent:
  1. Implements feature
  2. Runs tests
  3. Launches git-operations subagent

Git Subagent:
  1. Reviews changes (git status, git diff)
  2. Identifies files to commit
  3. Creates atomic commit
  4. Reports back to main agent

Hooks:
  - SubagentStop: Verifies commit was made
  - Stop: Final check when main agent finishes
```

**Communication:**
- Main agent tells subagent what was accomplished
- Subagent reviews actual changes
- Subagent crafts appropriate commit message

## Common Scenarios

### Scenario 1: Implementing a Feature

```
1. Main agent implements feature
2. Main agent runs tests → tests pass
3. [PostToolUse hook triggers]
   → "Tests passed and you have uncommitted changes. Please commit."
4. Main agent launches git-operations subagent
5. Git subagent reviews changes, creates commit
6. [SubagentStop hook verifies commit made]
7. Main agent continues to next task
```

### Scenario 2: Multiple Features in One Session

```
1. Implement feature A → tests pass → [hook prompts] → commit
2. Implement feature B → tests pass → [hook prompts] → commit
3. Implement feature C → tests pass → [hook prompts] → commit
4. Agent says "done"
5. [Stop hook checks] → All changes committed ✓
```

### Scenario 3: Debugging (No Tests Yet)

```
1. Implement partial feature
2. Try to test manually → doesn't work yet
3. Fix bugs
4. Eventually: run tests → pass
5. [PostToolUse hook triggers] → commit
```

**Key:** Hook waits for tests to pass, doesn't nag during debugging.
