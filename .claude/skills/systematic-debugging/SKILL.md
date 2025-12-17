---
name: systematic-debugging
description: When encountering any bug, test failure, or unexpected behavior - use this four-phase framework (root cause investigation, pattern analysis, hypothesis testing, implementation) before proposing any fixes
---

# Systematic Debugging

## Overview

Random fixes waste time and create new bugs. Quick patches mask underlying issues.

**Core principle:** ALWAYS find root cause before attempting fixes. Symptom fixes are failure.

**Violating the letter of this process is violating the spirit of debugging.**

## The Iron Law

```
NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST
```

If you haven't completed Phase 1, you cannot propose fixes.

## When to Use

Use for ANY technical issue:
- Test failures
- Bugs in production
- Unexpected behavior
- Performance problems
- Build failures
- Integration issues

**Use this ESPECIALLY when:**
- Under time pressure (emergencies make guessing tempting)
- "Just one quick fix" seems obvious
- You've already tried multiple fixes
- Previous fix didn't work
- You don't fully understand the issue

## The Four Phases

You MUST complete each phase before proceeding to the next.

### Phase 1: Root Cause Investigation

**For detailed root cause tracing techniques**: Read `references/root-cause-tracing.md`

**BEFORE attempting ANY fix:**

1. **Read Error Messages Carefully**
   - Don't skip past errors or warnings
   - They often contain the exact solution
   - Read stack traces completely

2. **Reproduce Consistently**
   - Can you trigger it reliably?
   - What are the exact steps?
   - If not reproducible, gather more data - don't guess

3. **Check Recent Changes**
   - What changed that could cause this?
   - Git diff, recent commits
   - New dependencies, config changes

4. **Trace Data Flow (Multi-Component Systems)**
   - Add diagnostic instrumentation at each boundary
   - Log what enters and exits each component
   - Run once to gather evidence showing WHERE it breaks
   - THEN investigate that specific component

### Phase 2: Pattern Analysis

1. **Find Working Examples** - Locate similar working code in same codebase
2. **Compare Against References** - Read reference implementations COMPLETELY
3. **Identify Differences** - List every difference between working and broken
4. **Understand Dependencies** - What settings, config, environment does this need?

### Phase 3: Hypothesis and Testing

1. **Form Single Hypothesis** - "I think X is the root cause because Y"
2. **Test Minimally** - Smallest possible change to test hypothesis
3. **Verify Before Continuing** - Didn't work? Form NEW hypothesis, don't stack fixes
4. **When You Don't Know** - Say so. Don't pretend.

### Phase 4: Implementation

1. **Create Failing Test Case** - MUST have before fixing (use test-driven-development skill)
2. **Implement Single Fix** - ONE change at a time, no "while I'm here" improvements
3. **Verify Fix** - Test passes? No other tests broken?
4. **If 3+ Fixes Failed** - STOP. Question the architecture. Discuss with your partner.

## Red Flags - STOP and Follow Process

If you catch yourself thinking:
- "Quick fix for now, investigate later"
- "Just try changing X and see if it works"
- "It's probably X, let me fix that"
- "I don't fully understand but this might work"
- "One more fix attempt" (when already tried 2+)

**ALL of these mean: STOP. Return to Phase 1.**

## Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "Issue is simple" | Simple issues have root causes too |
| "Emergency, no time" | Systematic is FASTER than thrashing |
| "Just try this first" | First fix sets the pattern. Do it right. |
| "Multiple fixes at once saves time" | Can't isolate what worked. Causes new bugs. |
| "I see the problem, let me fix it" | Seeing symptoms ≠ understanding root cause |

## Quick Reference

| Phase | Key Activities | Success Criteria |
|-------|---------------|------------------|
| **1. Root Cause** | Read errors, reproduce, trace data | Understand WHAT and WHY |
| **2. Pattern** | Find working examples, compare | Identify differences |
| **3. Hypothesis** | Form theory, test minimally | Confirmed or new hypothesis |
| **4. Implementation** | Create test, fix, verify | Bug resolved, tests pass |

## Related Skills

- **test-driven-development** - For creating failing test cases (Phase 4)
- **verification-before-completion** - For verifying fixes before claiming success
