# Session Start

Initialize a new work session by gathering context and preparing for productive work.

## Steps

### 1. Check Environment
Run these commands to understand current state:

```bash
git status
```

```bash
git log --oneline -5
```

### 2. Load Progress State
Read `project-progress.json` if it exists in the project root. If found, report:

**Current Work** (from `currentWork` field):
- If `type == "plan"`: Show plan path and current task number
- If `type == "debug"`: Show issue description and debug phase
- If `type == "general"`: Just note "general work"

**Last Session** (from `lastSession` field):
- Date and duration
- Summary of what was accomplished
- Events that occurred (plans started, tasks completed, etc.)
- Any commits made
- Planned next steps

If no progress file exists, note this and ask what we're working on today.

### 3. Search Journal
Search your journal for entries from the last 7 days related to this project:
```
search_journal("recent work")
```

Surface any relevant insights or decisions.

### 4. Check Pending Work
```bash
gh pr list --state open --limit 5
```

```bash
git branch --list | head -10
```

### 5. Report Status
Provide a summary:
- **Uncommitted work**: Any changes that need attention?
- **Last session**: What was accomplished? Any blockers?
- **Open PRs**: Any awaiting review or merge?
- **Recommendation**: What should we work on?

### 6. Surface Applicable Skills
Based on the planned work, mention any skills that might apply.

---

**Output format:**

```
## Session Start Summary

**Git Status:** [clean/uncommitted changes]
**Current Work:** [plan: path (task N) | debug: issue (phase) | general]
**Last Session:** [date] - [summary] ([duration] minutes)
**Blockers:** [any from last time]
**Open PRs:** [count]

**Recommended Next Steps:**
1. [first priority from progress.json nextSteps]
2. [second priority]

**Applicable Skills:** [list if relevant to current work]
```
