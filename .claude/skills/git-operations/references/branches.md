# ABOUTME: Branch management, coordination between agents, and safe branch operations
# ABOUTME: Referenced from git-operations skill when managing branches

# Branch Management

## Architecture: Subagent + Hooks

### Why a Subagent?

Git operations should run in a dedicated subagent because:
1. **Isolation**: Git context doesn't pollute main conversation
2. **Focus**: Subagent has single responsibility
3. **Traceability**: Git operations are clearly delegated
4. **Error handling**: Git failures don't derail main process

### Why Hooks?

Hooks provide enforcement layer:
1. **PreToolUse hooks**: Block dangerous git commands before execution
2. **PostToolUse hooks**: Prompt commits after tests pass
3. **SubagentStop hooks**: Verify subagent completed expected commits
4. **Stop hooks**: Final check for uncommitted changes

**Defense in depth:** Skill provides knowledge, hooks provide enforcement.

## Branch Operations

### Creating Branches

```bash
# Create and switch to new branch
git checkout -b feature/my-feature

# Or using modern git
git switch -c feature/my-feature
```

### Switching Branches

```bash
# Switch to existing branch
git checkout main

# Or using modern git
git switch main
```

**IMPORTANT:** Always commit or stash changes before switching branches.

### Merging Branches

```bash
# Switch to target branch
git checkout main

# Merge feature branch
git merge feature/my-feature
```

### Deleting Branches

```bash
# Delete local branch (safe - only if merged)
git branch -d feature/my-feature

# Force delete local branch (use with caution)
git branch -D feature/my-feature

# Delete remote branch
git push origin --delete feature/my-feature
```

## Coordination Between Agents

### Checking Branch Status

```bash
# See all branches
git branch -a

# See which branch you're on
git branch --show-current

# See branch tracking info
git branch -vv
```

### Before Switching Branches

1. Check for uncommitted changes: `git status`
2. Either commit changes or stash them: `git stash`
3. Switch branches: `git switch <branch>`
4. If stashed, restore: `git stash pop`

### Working with Multiple Agents

**Best practices:**
- Each agent should work on their own branch when possible
- Coordinate before merging to shared branches (main/master)
- Use descriptive branch names: `feature/<feature-name>`, `fix/<bug-name>`
- Communicate branch status in commit messages
