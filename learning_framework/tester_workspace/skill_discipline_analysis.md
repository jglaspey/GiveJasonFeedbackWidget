# ABOUTME: Analysis of skill-discipline failure modes vs hook coverage
# ABOUTME: Part of 07_skill_discipline_deprecation experiment

## H1: Do Hooks Cover Main Failure Modes?

### Failure Mode 1: Forgetting to check for applicable skills

**Current Prompt-Based Approach:**
- Relies on me mentally running through "list available skills" checklist
- Easy to skip when focused on the problem
- No enforcement mechanism

**Hook-Based Approach:**
- UserPromptSubmit hook automatically scans prompt for skill triggers
- SessionStart hook reminds about key skills at session beginning
- No action required from me - detection is automatic

**Hook Coverage: FULL** ✅
- Hooks eliminate the "remember to check" problem entirely
- Automatic keyword/pattern detection catches debugging (systematic-debugging) and implementation (TDD) contexts
- From completed experiments: pattern-based detection achieves 89% recall for TDD, 100% precision

### Failure Mode 2: Rationalizing that skill doesn't apply

**Current Prompt-Based Approach:**
- Lists common rationalizations to recognize
- Relies on self-awareness to catch rationalizing behavior
- Easy to convince myself the skill doesn't apply

**Hook-Based Approach:**
- Hook fires regardless of my reasoning
- Hard to ignore explicit "⚠️ DEBUGGING DETECTED: Use systematic-debugging skill" message
- Blocking hooks (exit 2) can prevent tool use until skill is acknowledged

**Hook Coverage: SUBSTANTIAL** ✅
- Main mechanism: Makes rationalization visible and harder to act on
- The hook's message appears in context, making it awkward to proceed without skill
- From experiments: Pattern exclusions reduce false positives (e.g., "add error handling" not triggering debugging)

### Failure Mode 3: Skipping skill because "too simple"

**Current Prompt-Based Approach:**
- "The skill is overkill for this" listed as rationalization
- No enforcement beyond conscience

**Hook-Based Approach:**
- Hook fires based on prompt content, not task complexity judgment
- Simple tasks that match patterns still trigger
- Reminder appears regardless of perceived simplicity

**Hook Coverage: SUBSTANTIAL** ✅
- Complexity judgment is subjective; pattern matching is objective
- Hook fires for "fix this small bug" same as "fix this complex bug"
- From experiments: Even single-keyword triggers ("crash", "failing") work reliably

## Summary: Hook Coverage of Failure Modes

| Failure Mode | Prompt Coverage | Hook Coverage | Improvement |
|--------------|-----------------|---------------|-------------|
| Forgetting to check | Checklist (voluntary) | Automatic detection | Major |
| Rationalizing | Self-awareness | External reminder | Major |
| "Too simple" | Listed warning | Objective patterns | Major |

## What Hooks DON'T Cover (see H2)

1. Skills without clear keyword patterns (e.g., project-discovery)
2. Announcing skill usage for transparency
3. TodoWrite checklist creation
4. Following the skill exactly (semantic compliance)

## Evidence from Completed Experiments

- **01_prompt_context_detection**: Pattern-based detection works with 89% recall, 100% precision for TDD
- **03_content_pattern_detection**: Can detect anti-patterns in code being written
- **04_tdd_enforcement**: State tracking enables enforcement of TDD workflow
- **06_latency_impact**: Hooks add only ~31ms latency (not a concern)

## Conclusion

**H1 SUPPORTED**: Hooks cover the three main failure modes of skill-discipline more effectively than prompt-based reminders because:
1. Automatic vs voluntary checking
2. External reminder vs self-awareness
3. Objective patterns vs subjective complexity judgment

---

## H2: What Aspects Can't Be Replaced By Hooks?

The test plan identifies three potentially unreplaceable aspects:
1. Announcing skill usage (social/documentation)
2. TodoWrite checklist creation (internal process)
3. Following skill exactly (semantic understanding)

### Aspect 1: Announcing Skill Usage

**Current Requirement:**
> "Say: 'I'm using [Skill Name] to [what you're doing].'"

**Hook Capability:**
- Hooks can DETECT skill invocation (PostToolUse on Skill tool)
- Hooks CAN'T FORCE announcement text in my response
- Could log/track skill usage, but can't inject text

**Is This Loss Acceptable?**

| Value | Assessment |
|-------|------------|
| Transparency to user | Medium - user sees tool calls in UI |
| Self-discipline reinforcement | Low - hook already reminds |
| Debugging/audit | High - can achieve via hook logging instead |

**Verdict:** ACCEPTABLE LOSS
- The announcement is mostly self-discipline (now replaced by hooks)
- Users can see Skill tool invocation in the interface
- Audit trail can be maintained via hook logging to files

### Aspect 2: TodoWrite Checklist Creation

**Current Requirement:**
> "If a skill has a checklist, YOU MUST create TodoWrite todos for EACH item."

**Hook Capability:**
- PostToolUse on Skill tool can detect which skill was invoked
- CAN check if skill has a known checklist
- CAN remind "📋 CHECKLIST: TDD has a checklist, create todos"
- CAN'T verify I actually created todos
- CAN'T block until todos are created (circular - need to call TodoWrite)

**Potential Enhancement:**
Could add a PostToolUse hook that:
1. Detects skill invocation
2. Checks if it's a skill with checklist
3. Outputs strong reminder
4. Separately, could add a PreToolUse hook on Edit/Write that checks if TodoWrite was called since skill invocation (state tracking)

**Is This Loss Acceptable?**

| Value | Assessment |
|-------|------------|
| Prevents step skipping | High - this is the core value |
| Enforcement mechanism | Partial - can remind, can't enforce |
| Alternative | Strong reminders + convention |

**Verdict:** PARTIAL LOSS - MITIGABLE
- Can't enforce TodoWrite creation, but can strongly remind
- Hook-based reminder is more reliable than prompt-based
- If I ignore explicit reminder, that's observable/auditable

### Aspect 3: Following Skill Exactly

**Current Requirement:**
> "Follow the skill exactly."

**Hook Capability:**
- CAN'T verify semantic compliance with skill instructions
- CAN verify specific patterns (e.g., "test file before production code" in TDD)
- CAN'T understand if I followed all steps properly

**What CAN Be Enforced:**
- TDD workflow order (test → fail → implement → pass)
- File path patterns (workers in workers/, tests in tests/)
- Content anti-patterns (time.sleep(), mock assertions)

**What CAN'T Be Enforced:**
- Did I fully investigate root cause (systematic-debugging)?
- Did I consider all hypotheses?
- Did I check all the right files?
- Did I follow the spirit of the skill?

**Verdict:** FUNDAMENTAL LIMITATION
- Hooks enforce mechanics, not semantics
- This is inherent - hooks can't understand intent
- But: Mechanics enforcement is 80% of the value

### Gap Analysis Summary

| Aspect | Can Hook Detect? | Can Hook Enforce? | Loss if Removed |
|--------|------------------|-------------------|-----------------|
| Skill announcement | Yes (PostToolUse) | No | Low |
| TodoWrite checklist | Yes (PostToolUse) | Partial (remind) | Medium |
| Following skill exactly | Partial (patterns) | Partial (mechanics) | Medium |
| Listing skills mentally | N/A | N/A | None (automated) |
| 1% rule | Yes (patterns) | Yes (reminder) | None |
| Common rationalizations | N/A | N/A | None (automated) |

### Acceptable vs Unacceptable Gaps

**Acceptable (can lose):**
- Skill announcements - redundant with tool call visibility
- Mental skill listing - automated by detection

**Mitigable (need alternative):**
- TodoWrite checklist creation - strong reminder hook
- "Instructions ≠ permission to skip" - detection handles main case

**Fundamental (inherent limitation):**
- Semantic compliance - hooks enforce mechanics, not understanding
- But this is 80/20: If mechanics are right, semantics usually follow

## H2 Conclusion

**H2 SUPPORTED**: Some aspects can't be fully replaced:
1. **Announcing skill usage** - Acceptable loss (redundant)
2. **TodoWrite checklist** - Mitigable with strong reminder hook
3. **Following exactly** - Fundamental limitation, but mechanics enforcement covers most value

The gaps are either acceptable losses or mitigable with enhanced hooks.

---

## H3: Is a Hybrid Approach Optimal?

The test plan proposes three approaches to compare:
1. **Hooks-only**: Remove skill-discipline, rely on automated enforcement
2. **Current**: skill-discipline skill + session-start reminder
3. **Hybrid**: Hooks for detection + minimal session reminder + CLAUDE.md guidance

### Approach Analysis

#### Option 1: Hooks-Only

**What We Get:**
- Automatic prompt context detection (debugging, TDD)
- Automatic file path enforcement
- Automatic content pattern detection
- TDD state tracking
- ~31ms latency per hook (acceptable)

**What We Lose:**
- No reminder about non-detectable skills (project-discovery, journal-discipline)
- No TodoWrite checklist enforcement
- No guidance on rationalizations

**Assessment:** Incomplete - misses skills without keyword patterns

#### Option 2: Current (skill-discipline + reminder)

**What We Get:**
- Comprehensive checklist before each response
- Rationalization list to watch for
- TodoWrite checklist requirement
- Skill announcement requirement

**What We Lose:**
- Nothing technically, but...

**Problems:**
- Prompt-based = easily ignored
- Long reminder = context cost
- Checklist fatigue = becomes background noise
- Redundant with hooks for detectable skills

**Assessment:** Redundant - hooks do the detectable parts better

#### Option 3: Hybrid (Recommended)

**Hooks Handle:**
- Debugging context detection → systematic-debugging
- Implementation context detection → test-driven-development
- File path enforcement → skill compliance
- Content anti-patterns → skill compliance
- TDD workflow state → blocking enforcement
- Latency: ~90ms cumulative (acceptable)

**Minimal Reminder Handles:**
- Non-detectable skills (project-discovery, journal-discipline)
- TodoWrite for skill checklists (strong reminder)
- One-line prompt, not full checklist

**CLAUDE.md Handles:**
- Guidance that applies always (not per-prompt)
- Rationalization awareness (education, not enforcement)
- General principle: "Skills are enforced via hooks"

### Proposed Hybrid Configuration

**1. Keep these hooks:**
- `session-start-skill-reminder.py` → Simplify to minimal version
- `detect-skill-context.py` → Upgrade to pattern-based v2
- Future: `tdd-enforcement.py` (blocking)
- Future: `skill-checklist-reminder.py` (PostToolUse on Skill)

**2. Simplify session-start-skill-reminder.py:**

```python
# Current: 27 lines of detailed protocol
SKILL_REMINDER = """
📚 **Skill Discipline Reminder**

Before responding, check: Does a skill apply to this task?

Key skills available:
- **systematic-debugging** - For any bug or test failure
- **test-driven-development** - For any feature or bugfix
[...7 more lines...]

**Rule:** If a skill applies, announce it and follow it exactly.
**Memory:** For complex work, search your journal first.
See **skill-discipline** skill for full protocol.
"""

# Proposed minimal: 6 lines
SKILL_REMINDER = """
📚 Most skills are enforced via hooks. For cases hooks can't detect:
- **project-discovery** - New project design
- **journal-discipline** - Search journal for complex work

If invoking a skill with a checklist, create TodoWrite items.
"""
```

**3. Update CLAUDE.md:**

Move rationalization awareness and general guidance from skill-discipline into CLAUDE.md:
- "Skills exist because simple things become complex"
- "Instructions describe WHAT, skills describe HOW"

**4. Deprecate skill-discipline:**

After validation, move to `.claude/skills/_deprecated/skill-discipline/`.
Keep for reference but remove from active skill list.

### Comparison Matrix

| Aspect | Hooks-Only | Current | Hybrid |
|--------|------------|---------|--------|
| Detectable skills | ✅ Auto | ⚠️ Manual | ✅ Auto |
| Non-detectable skills | ❌ | ✅ | ✅ |
| Rationalization prevention | ✅ | ⚠️ | ✅ |
| Context cost | Low | High | Low |
| Checklist fatigue | None | High | Low |
| TodoWrite reminder | ❌ | ✅ | ✅ |
| Audit trail | ✅ | ❌ | ✅ |

### Hybrid Validation Plan

**Phase 1 (Now):** Document the hybrid architecture (done above)

**Phase 2 (Next):** Implement minimal reminder
- Modify `session-start-skill-reminder.py`
- Test with Agent SDK

**Phase 3 (1 week):** Run hybrid for 1 week
- Track skill compliance
- Track false positives
- Track user satisfaction

**Phase 4 (After validation):** Deprecate skill-discipline
- Move to _deprecated folder
- Update CLAUDE.md
- Update skill list in CLAUDE.md

### Rollback Criteria

Rollback to skill-discipline if:
- Compliance drops > 30%
- False positive rate > 25%
- Non-detectable skills frequently skipped
- User complaints about missing guidance

## H3 Conclusion

**H3 SUPPORTED**: Hybrid approach is optimal because:
1. **Hooks** cover detectable cases with enforcement (not just reminders)
2. **Minimal reminder** covers non-detectable cases without checklist fatigue
3. **CLAUDE.md** holds guidance that applies always (not per-prompt)

This gives us:
- Better enforcement (hooks) where we can automate
- Lower context cost (minimal reminder vs full protocol)
- Reduced fatigue (targeted reminders vs comprehensive checklist)
- Clear audit trail (hook logs)

---

## Overall Conclusions

### H1: Main Failure Modes ✅
Hooks cover forgetting, rationalizing, and "too simple" better than prompts through automatic detection, external reminders, and objective pattern matching.

### H2: Unreplaceable Aspects ✅
Some aspects can't be fully replaced (announcements, TodoWrite, semantics), but losses are acceptable or mitigable.

### H3: Hybrid Approach ✅
Optimal approach is hooks + minimal reminder + CLAUDE.md guidance, not hooks-only or full skill-discipline.

### Migration Recommendation

1. **Keep hooks** - They're working and well-tested
2. **Simplify reminder** - Reduce to non-detectable skills only
3. **Deprecate skill-discipline** - Move to _deprecated after validation
4. **Update CLAUDE.md** - Add general skill guidance there instead
