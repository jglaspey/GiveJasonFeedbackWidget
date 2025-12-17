---
name: executing-plans
description: When implementing a plan created with writing-plans skill - batch execution with checkpoints for review, stopping when blocked rather than forcing progress
---

# Executing Plans

## Overview

Implement plans through controlled batches with review checkpoints.

**Core principle:** Execute exactly as written. Stop when blocked. Report between batches.

## The Five-Step Process

### Step 1: Load and Review Plan
- Read the plan file completely
- Raise concerns BEFORE starting
- Create TodoWrite items for tasks
- If no concerns, proceed

### Step 2: Execute Batch
Default first batch: 3 tasks.

For each task:
1. Mark as in_progress in TodoWrite
2. Follow steps EXACTLY as written
3. Run all verification commands
4. Mark as completed

### Step 3: Report
After each batch:
- Present what was implemented
- Show verification outputs
- State "Ready for feedback"
- Wait for response

### Step 4: Continue
Based on feedback:
- Apply any changes requested
- Execute next batch
- Repeat until completion

### Step 5: Complete
When all tasks done:
- Run full test suite
- Report final status
- Commit if not already done

## Critical Stopping Points

**STOP immediately when encountering:**
- Missing dependencies
- Test failures you can't explain
- Unclear instructions
- Repeated verification failures

**Request clarification rather than assuming.**

## Key Principles

1. **Follow plan exactly** - Don't improvise
2. **Don't skip verifications** - Every step matters
3. **Report between batches** - Await feedback
4. **Stop when blocked** - Don't force progress

## Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "I can figure this out" | Stop and ask |
| "Skip verification, it'll pass" | Run it anyway |
| "Combine multiple batches" | Stick to batch size |
| "Fix this small thing first" | Follow the plan order |

## Related Skills

- **writing-plans** - Creates the plans this skill executes
- **verification-before-completion** - Verify each step before claiming done
- **git-operations** - For commits at checkpoints
