---
name: git-worktrees
description: When you need an isolated workspace for experimental work or parallel development - creates git worktrees without polluting the main working directory
---

# Using Git Worktrees

## Overview

Git worktrees let you have multiple branches checked out simultaneously in separate directories.

**Core principle:** Isolated workspaces for experimental or parallel work.

## When to Use

- Experimental changes you might abandon
- Working on a feature while main needs a hotfix
- Testing changes without stashing current work
- Parallel development branches

## Creating a Worktree

### 1. Choose Location

Priority order:
1. Existing `.worktrees/` or `worktrees/` directory
2. CLAUDE.md preferences
3. Ask user

### 2. Verify .gitignore

**CRITICAL:** Before creating project-local worktrees:

```bash
grep -q "worktrees/" .gitignore || echo "worktrees/" >> .gitignore
```

This prevents accidentally committing worktree contents.

### 3. Create Worktree

```bash
# Get project name
PROJECT=$(basename $(git rev-parse --show-toplevel))

# Create worktree with new branch
git worktree add worktrees/${PROJECT}-feature feature-branch

# Or from existing branch
git worktree add worktrees/${PROJECT}-hotfix existing-branch
```

### 4. Setup Dependencies

Auto-detect and install:
```bash
cd worktrees/${PROJECT}-feature

# Node.js
[ -f package.json ] && npm install

# Python
[ -f requirements.txt ] && pip install -r requirements.txt

# etc.
```

### 5. Verify Clean State

Run tests in new worktree to establish baseline:
```bash
npm test  # or pytest, cargo test, etc.
```

## Cleanup

When done with worktree:

```bash
# Remove worktree
git worktree remove worktrees/${PROJECT}-feature

# Or if changes abandoned
git worktree remove --force worktrees/${PROJECT}-feature
```

## Key Rules

- Always verify .gitignore before creating project-local worktrees
- Run tests after setup to verify clean state
- Get permission before proceeding if tests fail
- Clean up worktrees when done

## Related Skills

- **git-operations** - General git best practices
