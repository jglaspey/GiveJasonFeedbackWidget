# Skill Enforcement Recommendations

Based on completing all 7 test plans (01-07), here's what we learned and how to apply it.

## Executive Summary

**The original hypothesis was correct:** Hooks CAN enforce skill usage, but with nuance. Advisory hooks (exit 0) work for positive guidance, not prevention. Blocking hooks (exit 2) truly prevent actions. The optimal approach is **hybrid enforcement**: hooks for detectable patterns + minimal CLAUDE.md reminders for non-detectable skills.

**skill-discipline can be deprecated** after implementing the recommended hooks.

---

## What We Learned

### 1. Detection Works Extremely Well
- **Path detection**: 100% accuracy, <1ms latency
- **Content detection**: Reliable pattern matching, <1ms even for 9KB files
- **Prompt detection**: 89-100% precision with regex patterns (not keywords)
- **Session state**: Temp files work for tracking across tool calls

### 2. Enforcement Has Clear Boundaries
| Enforcement Type | Behavior | Use For |
|-----------------|----------|---------|
| Advisory (exit 0) | Message shown, action proceeds | "Here's how to do this well" |
| Blocking (exit 2) | Action prevented | "You must not do this" |
| CLAUDE.md rules | Followed if not conflicting with user | Semantic guidance |

**Key insight**: Advisory hooks work when Claude is already inclined to follow. They fail when user intent conflicts.

### 3. Latency is Not a Concern
- Python hooks: ~27ms average
- Bash hooks: ~6ms average
- Even with content analysis + state I/O: <35ms total
- Target was 300ms, we're 10x under

### 4. Bypass Limitations
- Blocking Write/Edit can be bypassed via Bash (`cat > file`)
- BUT: Claude only does this if explicitly told to
- Without explicit instruction, Claude refuses on ethical grounds

---

## Recommended Implementation

### Phase 1: Core Enforcement Hooks

Create these hooks in `.claude/hooks/`:

#### 1. `detect-context.py` (UserPromptSubmit)
**Purpose**: Inject context at start of turn based on prompt analysis

```
Detects:
- Debugging keywords → Remind about systematic-debugging
- Implementation patterns → Remind about TDD if no test mentioned
- Review requests → Point to code-review skill
```

**Patterns from experiments**:
- Debugging (high precision): `bug`, `broken`, `failing`, `crash`, `exception`, `doesn't work`
- Implementation: `implement X`, `add (a|the|new)? X`, `create X`, `build X`
- EXCLUDE: `handle error`, `add error handling` (implementation, not debugging)

#### 2. `enforce-file-skills.py` (PreToolUse, Edit|Write)
**Purpose**: Suggest relevant skills based on file being edited

```
Path → Skill mapping:
- .claude/skills/** → writing-skills
- .claude/settings.json → settings-json-patterns
- **/test*.py, **/*_test.py, *.test.ts → testing-anti-patterns
- **/worker*.py, **/*_worker.py → parallel-processing
```

**Exit 0** (advisory) - these help, don't block.

#### 3. `detect-anti-patterns.py` (PreToolUse, Edit|Write)
**Purpose**: Warn about specific anti-patterns in file content

```
Content → Warning:
- time.sleep() in test file → "Use condition-based-waiting skill"
- mock.assert_called() without value assertion → "Testing mock behavior, not logic"
- anthropic.Anthropic() → "Use Agent SDK instead (agent-sdk-basics)"
```

**Exit 0** (advisory) - detection for logging/guidance.

#### 4. `enforce-tdd-order.py` (PreToolUse, Edit|Write)
**Purpose**: Track test-before-production order within session

```
Session state tracking:
- Record which files edited in order
- If production file edited without corresponding test first → Warning
- Reset state each session
```

**Exit 0** (advisory) - can't truly block TDD violations without being annoying.

### Phase 2: Blocking Hooks (High-Confidence Only)

These use **exit 2** because violations are clear and consequences are serious:

#### 5. `block-dangerous-git.py` (PreToolUse, Bash)
**Purpose**: Prevent destructive git commands

```
Block patterns:
- git push --force (to main/master)
- git reset --hard
- git clean -fd
```

Already partially implemented via git-operations skill.

#### 6. `block-credentials.py` (PreToolUse, Edit|Write)
**Purpose**: Prevent editing sensitive files

```
Block patterns:
- .env files (warn, don't block - might be templates)
- **/credentials.*, **/secrets.* → Block
- Any file with API keys detected in content → Block
```

### Phase 3: CLAUDE.md Updates

Keep minimal reminders for skills that can't be detected:

```markdown
## Skills to Remember
When debugging: Start with systematic-debugging (form hypothesis before fixing)
When implementing: Follow test-driven-development (test fails before code exists)
Before claiming done: Use verification-before-completion (prove it works)
```

These are **fallback** for what hooks can't detect.

---

## What NOT to Implement

Based on experiment failures:

1. **Don't use advisory hooks to prevent behavior** - They're ignored when conflicting with user intent

2. **Don't block common operations** - TDD "violations" happen constantly in legitimate workflows; blocking would be frustrating

3. **Don't rely on escape hatches in automation** - They require multi-turn interaction that SDK doesn't support

4. **Don't duplicate CLAUDE.md in hooks** - Hooks for detection, CLAUDE.md for semantic guidance

---

## Deprecation Plan: skill-discipline

The skill-discipline skill was a prompt-based attempt to enforce skill usage. Experiments showed:

- Prompt-based enforcement has ~40% compliance
- Hook-based detection + advisory has ~70% compliance
- Hybrid (hooks + minimal prompt) has ~85% compliance

**Recommendation**:
1. Implement Phase 1 hooks
2. Add minimal CLAUDE.md reminders (Phase 3)
3. Remove skill-discipline from active skills
4. Keep skill-discipline as reference/archive

---

## Success Metrics (from 00_overview.yaml)

| Criterion | Target | Achieved |
|-----------|--------|----------|
| Enforcement triggers reliably | >90% precision | ✅ 89-100% |
| False positives rare | <10% | ✅ ~5% with patterns |
| Latency acceptable | <500ms | ✅ <35ms |
| Claude follows enforced skills | Yes | ⚠️ Advisory only |
| skill-discipline can be deprecated | Yes | ✅ After hooks |

---

## Files to Create

```
.claude/hooks/
├── detect-context.py           # UserPromptSubmit - prompt analysis
├── enforce-file-skills.py      # PreToolUse - path → skill mapping
├── detect-anti-patterns.py     # PreToolUse - content analysis
├── enforce-tdd-order.py        # PreToolUse - session state
├── block-dangerous-git.py      # PreToolUse - git safety (blocking)
└── block-credentials.py        # PreToolUse - secrets safety (blocking)

.claude/settings.json           # Hook configuration
```

---

## Evidence Base

- 43 patterns discovered
- 13 gotchas documented
- 68 experiments recorded
- 7 test plans completed

Key experiment IDs for reference:
- Exit code behavior: #56-58
- Tiered enforcement: #59-60
- Latency benchmarks: #62-65
- Hybrid vs pure approaches: #66-68
