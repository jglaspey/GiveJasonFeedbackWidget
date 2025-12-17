---
name: writing-plans
description: When design work is complete and you need to create a detailed implementation plan - generates step-by-step guidance with exact file paths, code examples, and verification procedures
---

# Writing Implementation Plans

## Overview

Generate detailed implementation guidance for execution with minimal codebase familiarity.

**Core principle:** Plans should include exact file paths, complete code examples, and verification procedures. Break work into bite-sized tasks.

## When to Use

- After discovery/design is complete (see project-discovery skill)
- Before implementing a complex feature
- When work needs to be broken into reviewable chunks

## Plan Structure

### Header
```markdown
# [Feature Name] Implementation Plan

## Goal
[One sentence describing the outcome]

## Architecture Overview
[Brief description of approach]

## Prerequisites
[Any setup needed before starting]
```

### Tasks

Each task follows this format:

```markdown
## Task 1: [Clear name]

**Files:** `path/to/file.py`

### Step 1: Write failing test
```python
# Exact test code
```

### Step 2: Verify test fails
```bash
pytest path/to/test.py -k "test_name"
# Expected: FAILED
```

### Step 3: Implement
```python
# Exact implementation code
```

### Step 4: Verify test passes
```bash
pytest path/to/test.py -k "test_name"
# Expected: PASSED
```

### Step 5: Commit
```bash
git add path/to/file.py path/to/test.py
git commit -m "Add [feature]: [what this task accomplished]"
```
```

## Key Principles

- **Bite-sized tasks**: 2-5 minutes each
- **TDD structure**: Every task has write test → verify fail → implement → verify pass
- **Exact paths**: Always specify full file paths
- **Complete code**: Include actual code, not descriptions
- **Verification commands**: Exact commands with expected output

## Plan Location

Save completed plans to: `docs/plans/YYYY-MM-DD-<feature-name>.md`

Or for business process projects: `projects/<name>/docs/plans/`

## After Plan Completion

Offer two paths:
1. **Execute now** - Use executing-plans skill for batch execution with checkpoints
2. **Save for later** - Commit the plan, execute when ready

## Related Skills

- **project-discovery** - Use BEFORE this skill to understand what to build
- **executing-plans** - Use AFTER this skill to implement the plan
- **test-driven-development** - Every task follows TDD cycle
