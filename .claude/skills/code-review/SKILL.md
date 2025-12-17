---
name: code-review
description: When requesting or receiving code review feedback - structured approach to giving and receiving technical feedback with verification and technical rigor over social comfort
---

# Code Review

## Overview

Technical correctness over social comfort. Verify before implementing. Ask before assuming.

## Requesting Review

### When to Request

**Mandatory:**
- Before merging to main
- After completing major features
- After multi-task implementation batches

**Optional but helpful:**
- When stuck on approach
- Before major refactoring

### What to Include

1. What was built (summary)
2. Which files changed
3. How to test/verify
4. Any concerns or areas needing attention

## Receiving Review

### Response Pattern

1. **Read feedback completely** - Don't start implementing mid-read
2. **Restate requirements** - "You want me to..."
3. **Verify against codebase** - Is this technically sound for YOUR context?
4. **Respond with:**
   - Technical acknowledgment, OR
   - Reasoned objection with evidence

### Forbidden Responses

- "You're absolutely right!"
- "Great point!"
- Any performative agreement

**Actions speak. Just fix it.** Or explain why you won't.

### When to Push Back

Challenge suggestions that:
- Would break existing functionality
- Lack full context about your codebase
- Violate YAGNI (add unused features)
- Conflict with documented architecture decisions

Push back with **technical reasoning**, not defensiveness.

### Implementation Order

1. Critical issues (blocking)
2. Simple fixes (quick wins)
3. Complex refactoring (last)

Test each change individually to prevent regressions.

## Key Principles

| Do | Don't |
|----|-------|
| Verify suggestions work in your context | Blindly implement all feedback |
| Ask for clarification when unclear | Guess at intent |
| Push back with technical evidence | Be defensive or dismissive |
| Fix issues systematically | Batch unrelated changes |

## Related Skills

- **verification-before-completion** - Verify before claiming fixes work
- **test-driven-development** - Each fix should have a test
