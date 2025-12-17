# Comprehensive Skill Review

A complete analysis of all 24 skills, their enforcement mechanisms, and recommendations.

## Skill Inventory

| # | Skill | Category | Current Enforcement | Recommended Enforcement |
|---|-------|----------|---------------------|------------------------|
| 1 | agent-project-setup | Setup/Reference | None | Slash command reference |
| 2 | agent-sdk-basics | Reference | None | Content hook (Anthropic API detection) |
| 3 | code-review | Workflow | None | Slash command + subagent |
| 4 | condition-based-waiting | Testing | None | Content hook (sleep detection) |
| 5 | defense-in-depth | Implementation | None | CLAUDE.md reminder |
| 6 | directory-structure | Setup/Reference | None | Slash command reference |
| 7 | executing-plans | Workflow | None | Slash command |
| 8 | git-operations | Safety | **Hooks + Subagent** ✓ | Already enforced |
| 9 | git-worktrees | Reference | None | None needed |
| 10 | journal-discipline | Memory | None | SessionStart reminder |
| 11 | parallel-processing | Implementation | None | Path hook (worker files) |
| 12 | path-management | Setup/Reference | None | Content hook (hardcoded paths) |
| 13 | project-discovery | Workflow | None | Slash command (/new-project) |
| 14 | prompt-isolation | Setup/Reference | None | Content hook (inline prompts) |
| 15 | railway-agent-sdk-deployment | Reference | None | Subagent-specific |
| 16 | sequential-processing | Implementation | None | Path hook (processing scripts) |
| 17 | settings-json-patterns | Reference | None | Path hook (settings.json) |
| 18 | skill-discipline | Meta | SessionStart hook | **DEPRECATE** |
| 19 | systematic-debugging | Debugging | None | Prompt hook (bug keywords) |
| 20 | test-driven-development | Implementation | None | Session state hook |
| 21 | testing-anti-patterns | Testing | None | Content hook (anti-patterns) |
| 22 | verification-before-completion | Implementation | None | CLAUDE.md + Stop hook |
| 23 | writing-plans | Workflow | None | Slash command |
| 24 | writing-skills | Reference | None | Path hook (skill files) |

---

## Skills by Enforcement Type

### 1. Already Enforced ✓

#### git-operations
**Current state:** Full enforcement via hooks + subagent
- `validate-git-command.py` - PreToolUse blocking for dangerous commands
- `post-test-commit-check.py` - PostToolUse prompt after tests pass
- `verify-git-subagent.py` - SubagentStop verification
- `final-commit-check.py` - Stop hook for uncommitted changes
- Dedicated `git-operations` subagent

**Recommendation:** No changes needed. This is the gold standard for enforcement.

---

### 2. Slash Command Enforcement

These skills apply to specific workflow moments. Better triggered via explicit commands than automatic hooks.

#### project-discovery
**Trigger:** Starting a new project
**Current:** Referenced by `/new-project` command
**Recommendation:** ✓ Already correct. Slash command is the right mechanism.

#### writing-plans
**Trigger:** After discovery, before implementation
**Current:** No enforcement
**Recommendation:** Create `/plan` slash command that references this skill.

#### executing-plans
**Trigger:** When implementing from a plan file
**Current:** No enforcement
**Recommendation:** Create `/execute` slash command OR detect plan files in cwd.

#### code-review
**Trigger:** Before merging, after completing features
**Current:** No enforcement
**Recommendation:**
- Create `/review` slash command
- Use `code-reviewer` subagent (already exists)
- Optional: Stop hook that suggests review before PR

#### agent-project-setup
**Trigger:** Starting new agent projects
**Current:** Referenced by `/new-project`
**Recommendation:** ✓ Already correct. This is an overview skill pointing to others.

#### directory-structure
**Trigger:** Setting up new projects
**Current:** None
**Recommendation:** Reference in `/new-project` command. Not independently enforced.

---

### 3. PreToolUse Hook Enforcement (Path-Based)

These skills apply when editing specific file types.

#### writing-skills
**Trigger:** Editing `.claude/skills/**`
**Detection:** Path pattern `*/.claude/skills/*`
**Current:** None
**Recommendation:** Advisory hook → "Invoke writing-skills skill"

#### settings-json-patterns
**Trigger:** Editing `.claude/settings.json`
**Detection:** Path pattern `*/.claude/settings.json`
**Current:** None
**Recommendation:** Advisory hook → "Reference settings-json-patterns skill"

#### parallel-processing
**Trigger:** Editing worker files
**Detection:** Path patterns `**/worker*.py`, `**/*_worker.py`, `**/workers/**`
**Current:** None
**Recommendation:** Advisory hook → "Follow parallel-processing patterns"

#### sequential-processing
**Trigger:** Editing processing scripts
**Detection:** Path patterns `**/process*.py`, `**/*_processor.py`
**Current:** None
**Recommendation:** Advisory hook → "Follow sequential-processing patterns"
**Note:** Distinguish from parallel by checking for SQLite imports

---

### 4. PreToolUse Hook Enforcement (Content-Based)

These skills apply when specific patterns appear in file content.

#### agent-sdk-basics
**Trigger:** Using Anthropic API in local scripts
**Detection:** Content pattern `anthropic.Anthropic()`, `from anthropic import`
**Current:** None
**Recommendation:** Advisory hook → "Use Agent SDK instead (agent-sdk-basics)"
**Note:** Only for scripts, not production server code

#### condition-based-waiting
**Trigger:** Using sleep/timeouts in tests
**Detection:** Content patterns in test files:
- `time.sleep(`
- `asyncio.sleep(`
- `setTimeout(`
- `await new Promise(r => setTimeout`
**Current:** None
**Recommendation:** Advisory hook → "Use condition-based-waiting instead"

#### testing-anti-patterns
**Trigger:** Mock-only assertions in tests
**Detection:** Content patterns:
- `.assert_called` without value assertions
- `.toHaveBeenCalled` without `.toBe`/`.toEqual`
**Current:** None
**Recommendation:** Advisory hook → "Testing mock behavior, not logic"

#### path-management
**Trigger:** Hardcoded paths in code
**Detection:** Content patterns:
- `/Users/` followed by username
- `/home/` followed by username
- Absolute paths outside project
**Current:** None
**Recommendation:** Advisory hook → "Use relative paths (path-management)"

#### prompt-isolation
**Trigger:** Large inline prompts in code
**Detection:** Content patterns:
- Multi-line f-strings with prompt-like content
- `prompt = """` or `prompt = f"""`
**Current:** None
**Recommendation:** Advisory hook → "Consider prompt-isolation pattern"
**Note:** Low confidence - hard to distinguish from legitimate strings

---

### 5. UserPromptSubmit Hook Enforcement

These skills apply based on what the user is asking.

#### systematic-debugging
**Trigger:** Debugging context in prompt
**Detection:** Keywords (high precision):
- `bug`, `broken`, `failing`, `crash`, `exception`
- `doesn't work`, `not working`
- Pattern: `X is broken`, `there is a bug`
**Exclude:** `handle error`, `add error handling`
**Current:** None
**Recommendation:** Advisory hook → "Start with systematic-debugging"

#### test-driven-development
**Trigger:** Implementation requests
**Detection:** Patterns:
- `implement X`, `add X`, `create X`, `build X`
- `write code/function/class`
**Exclude:** `write test`, `add test`
**Current:** None
**Recommendation:**
- UserPromptSubmit → Remind about TDD
- PreToolUse session state → Track test-before-production order

---

### 6. Session/Lifecycle Hook Enforcement

#### journal-discipline
**Trigger:** Session boundaries, important discoveries
**Current:** None
**Recommendation:**
- SessionStart hook already exists (session-start-skill-reminder.py)
- Add to Stop hook: "Did you journal any important discoveries?"
- This is more about building habit than enforcement

#### verification-before-completion
**Trigger:** Before claiming done
**Current:** None
**Recommendation:**
- Stop hook: "Did you verify your work?"
- CLAUDE.md reminder in completion section
- Hard to detect programmatically - relies on discipline

---

### 7. Subagent-Specific Skills

These skills apply when a specific subagent is running.

#### git-operations (for git-operations subagent)
**Current:** ✓ Subagent has skill in its prompt
**Recommendation:** No changes

#### railway-agent-sdk-deployment (for railway-deployment subagent)
**Current:** Subagent exists with this knowledge
**Recommendation:** Ensure subagent prompt references skill

#### code-review (for code-reviewer subagent)
**Current:** Subagent exists
**Recommendation:** Ensure subagent prompt references skill

---

### 8. Reference-Only Skills (No Enforcement)

These are pure reference material - used when needed, not enforced.

#### git-worktrees
**When used:** Manually when wanting isolated workspace
**Enforcement:** None needed - optional technique

#### defense-in-depth
**When used:** After fixing bugs
**Enforcement:** CLAUDE.md reminder only
**Note:** Hard to detect "bug fix" vs "new feature" programmatically

---

### 9. Skills to Deprecate

#### skill-discipline
**Current:** SessionStart hook reminder
**Problem:** Prompt-based enforcement has ~40% compliance
**Recommendation:**
1. Keep for reference/historical value
2. Remove from active skill rotation
3. Replace with hybrid enforcement (hooks + minimal CLAUDE.md)
4. Delete SessionStart reminder after other hooks implemented

---

## Implementation Priority

### Phase 1: High-Value, Easy Implementation

| Skill | Mechanism | Effort |
|-------|-----------|--------|
| writing-skills | Path hook | Low |
| settings-json-patterns | Path hook | Low |
| testing-anti-patterns | Content hook | Low |
| condition-based-waiting | Content hook | Low |
| agent-sdk-basics | Content hook | Low |

### Phase 2: Workflow Commands

| Skill | Mechanism | Effort |
|-------|-----------|--------|
| writing-plans | `/plan` command | Medium |
| executing-plans | `/execute` command | Medium |
| code-review | `/review` command | Medium |

### Phase 3: Complex Detection

| Skill | Mechanism | Effort |
|-------|-----------|--------|
| systematic-debugging | Prompt analysis | Medium |
| test-driven-development | Session state + prompt | High |
| path-management | Content analysis | Medium |
| verification-before-completion | Stop hook + CLAUDE.md | Medium |

### Phase 4: Low Priority

| Skill | Mechanism | Effort |
|-------|-----------|--------|
| parallel-processing | Path hook | Low |
| sequential-processing | Path hook | Low |
| prompt-isolation | Content hook (unreliable) | Low |
| journal-discipline | SessionStart enhancement | Low |

---

## Existing Hooks Inventory

Current hooks in `.claude/hooks/`:

| Hook | Type | Purpose | Skills Enforced |
|------|------|---------|-----------------|
| validate-git-command.py | PreToolUse | Block dangerous git | git-operations |
| post-test-commit-check.py | PostToolUse | Prompt commit after tests | git-operations |
| verify-git-subagent.py | SubagentStop | Verify commit made | git-operations |
| final-commit-check.py | Stop | Block if uncommitted | git-operations |
| track-session-time.py | Stop | Prompt time tracking | (time-tracker) |
| session-start-tracking.py | SessionStart | Record start time | (time-tracker) |
| session-start-skill-reminder.py | SessionStart | Remind about skills | skill-discipline |

---

## Existing Slash Commands

| Command | Purpose | Skills Referenced |
|---------|---------|-------------------|
| /start | Session initialization | None directly |
| /checkpoint | Mid-session save | git-operations |
| /experiment | Learning framework | None |
| /new-project | Start new project | project-discovery, agent-project-setup |

---

## Existing Subagents

| Subagent | Purpose | Skills Used |
|----------|---------|-------------|
| git-operations | Safe commits | git-operations |
| time-tracker | Log session time | None (operational) |
| code-reviewer | Review code | code-review |
| railway-deployment | Deploy to Railway | railway-agent-sdk-deployment |

---

## Recommended New Hooks

Based on this review, create these hooks:

### 1. `detect-context.py` (UserPromptSubmit)
Covers: systematic-debugging, test-driven-development (prompt detection)

### 2. `enforce-file-skills.py` (PreToolUse, Edit|Write)
Covers: writing-skills, settings-json-patterns, parallel-processing, sequential-processing

### 3. `detect-anti-patterns.py` (PreToolUse, Edit|Write)
Covers: testing-anti-patterns, condition-based-waiting, agent-sdk-basics, path-management

### 4. `enforce-tdd-order.py` (PreToolUse, Edit|Write)
Covers: test-driven-development (session state tracking)

### 5. `prompt-verification.py` (Stop)
Covers: verification-before-completion, journal-discipline

---

## Recommended New Commands

### `/plan`
**Purpose:** Enter planning mode, reference writing-plans skill
**Content:** Load writing-plans skill, create plan file

### `/execute [plan-file]`
**Purpose:** Execute a plan with checkpoints
**Content:** Load executing-plans skill, track progress

### `/review`
**Purpose:** Request code review
**Content:** Launch code-reviewer subagent with code-review skill

---

## Summary

| Category | Count | Enforcement |
|----------|-------|-------------|
| Already enforced | 1 | git-operations |
| Slash command | 6 | project-discovery, writing-plans, executing-plans, code-review, agent-project-setup, directory-structure |
| Path hook | 4 | writing-skills, settings-json-patterns, parallel-processing, sequential-processing |
| Content hook | 5 | agent-sdk-basics, condition-based-waiting, testing-anti-patterns, path-management, prompt-isolation |
| Prompt hook | 2 | systematic-debugging, test-driven-development |
| Lifecycle hook | 2 | journal-discipline, verification-before-completion |
| Subagent-specific | 2 | railway-agent-sdk-deployment, (code-review via subagent) |
| Reference only | 2 | git-worktrees, defense-in-depth |
| **Deprecate** | 1 | skill-discipline |
| **Total** | 24 | |

---

## Next Steps

1. **Implement Phase 1 hooks** - High value, low effort
2. **Create new slash commands** - /plan, /execute, /review
3. **Update CLAUDE.md** - Minimal reminders for non-detectable skills
4. **Deprecate skill-discipline** - After hooks are in place
5. **Test and iterate** - Use learning framework to validate effectiveness
