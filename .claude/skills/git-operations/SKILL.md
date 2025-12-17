---
name: Git Operations for AI Agents
description: Safe git usage, atomic commits, hook enforcement - MUST be used for all git commit operations
when_to_use: |
  - Committing code changes
  - Managing version control for business processes
  - Coordinating git operations between agents
  - Need guidance on git safety, commit timing, or destructive operations
version: 2.0.0
languages: all
---

# Git Operations for AI Agents

## Overview

Git operations require strict discipline when performed by AI agents. One wrong command can destroy work.

**Core principle:** Git operations are powerful and dangerous. Default to safety, require explicit approval for destructive operations.

**Architecture:** This skill is designed to be used by a **git-operations subagent** with **hooks providing enforcement**.

## Critical Safety Rules

### NEVER Run Without Explicit Approval

**ABSOLUTELY NEVER run these commands without explicit, written approval:**
- `git reset --hard`
- `git push --force` (especially to main/master)
- `git clean -fd`
- `git commit --amend` (unless you authored it AND it's not pushed)

### NEVER Edit Environment Files

**NEVER edit, commit, or restore:**
- `.env`, `.env.local`, `.env.production`
- `credentials.json`, `secrets.yaml`
- Any file containing secrets

### ALWAYS Quote Special Characters

```bash
# ❌ WRONG
git add src/app/[candidate]/page.tsx

# ✅ CORRECT
git add "src/app/[candidate]/page.tsx"
```

**Paths with brackets, parentheses, or spaces MUST be quoted.**

## When to Commit

**Commit after:**
- ✅ Feature implemented + tests pass
- ✅ Bug fixed + tests pass
- ✅ Refactoring + tests still pass
- ✅ Documentation added

**Don't wait:**
- ❌ "I'll commit when the whole feature is done"
- ❌ "I'll commit at the end of the day"
- ❌ "I'll commit when the user asks"

## Reference Documentation

For detailed guidance on specific topics:

**For dangerous commands and safety patterns:** Read `references/safety.md`
- Complete list of destructive operations
- Safe alternatives and patterns
- File management rules
- Troubleshooting blocked commands

**For commit workflow and messages:** Read `references/commits.md`
- When to commit (timing decisions)
- Atomic commit patterns
- Commit message format
- Multi-agent coordination

**For branch management:** Read `references/branches.md`
- Creating and switching branches
- Merging and deleting branches
- Multi-agent branch coordination

**For hook integration:** Read `references/hooks.md`
- How hooks enforce safety
- Hook troubleshooting
- Configuring hooks in settings.json

## Evidence

This skill uses progressive disclosure to reduce context consumption:

- **Pattern #12** (0.90 confidence): "Progressive disclosure reduces context by 70%+"
- **Experiment #21**: "Three-tier progressive disclosure reduces token usage"

By keeping critical safety rules in the main skill and moving detailed workflows to reference files, we load only what's needed for each situation.

## Related Skills

- **agent-project-setup**: When to organize commits in business processes
- **settings-json-patterns**: Configuring git command permissions
- **sequential-processing**: Logging git operations in process runs

## Version History

- 2.0.0: Restructured with progressive disclosure (references/ directory)
- 1.0.0: Initial skill based on steipete's rules, adapted for AI agents with hook enforcement
