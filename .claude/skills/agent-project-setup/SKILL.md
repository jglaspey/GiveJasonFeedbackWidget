---
name: Agent Project Setup
description: Starting a new agent or business process project, setting up project structure, or deciding which patterns to apply
when_to_use: |
  - Starting new business process project
  - Setting up agent project structure
  - Want comprehensive overview of best practices
  - Deciding which specific patterns to apply
  - Keywords: setup, new project, project structure, best practices, getting started, organize
version: 2.1.0
languages: all
---

# Agent Project Setup

## Overview

Business process agents need specific patterns for maintainability, resumability, and professional operation. This overview skill points to focused skills for each pattern.

**Core principle:** Separate what runs (functional code) from what's generated (outputs). Make everything resumable.

## Quick Start

For new projects, apply these patterns in order:

1. **[directory-structure](../directory-structure/SKILL.md)** - Set up functional/ and outputs/ directories
2. **[path-management](../path-management/SKILL.md)** - Use relative paths and .env
3. **[prompt-isolation](../prompt-isolation/SKILL.md)** - Put prompts in separate files
4. **[sequential-processing](../sequential-processing/SKILL.md)** - Add timestamp runs and progress tracking

## Focused Skills

### 1. Directory Structure
**Skill:** [directory-structure](../directory-structure/SKILL.md)

**What it covers:**
- Standard project layout (functional/ vs outputs/)
- Where each file type goes
- .gitignore patterns
- Test script organization

**Use when:** Setting up new project or organizing existing one

---

### 2. Logging and Resumability
**Skill:** [sequential-processing](../sequential-processing/SKILL.md)

**What it covers:**
- Timestamp-based run directories
- Progress logging (.log and .jsonl)
- Resumability after failures
- Error isolation in errors/ directory
- Summary generation

**Use when:** Building long-running processes or need fault tolerance

---

### 3. Prompt Isolation
**Skill:** [prompt-isolation](../prompt-isolation/SKILL.md)

**What it covers:**
- Keeping prompts in separate .txt files
- Loading prompts from functional/prompts/
- Iterative prompt refinement
- A/B testing prompts

**Use when:** Working with AI prompts that change frequently

---

### 4. Path Management
**Skill:** [path-management](../path-management/SKILL.md)

**What it covers:**
- Machine-agnostic path handling
- Relative paths vs environment variables
- .env configuration
- Cross-platform compatibility

**Use when:** Code needs to run on multiple machines or environments

---

### 5. Parallel Processing
**Skill:** [parallel-processing](../parallel-processing/SKILL.md)

**What it covers:**
- Python workers for >100 items
- SQLite for worker coordination
- Subagent orchestration
- Progress tracking across workers

**Use when:** Processing large datasets in parallel

## Standard Project Template

The business process template combines all these patterns:

```
project/
├── .claude/
│   ├── CLAUDE.md           # Process instructions
│   └── settings.json       # Permissions
├── functional/              # → directory-structure
│   ├── scripts/
│   ├── prompts/            # → prompt-isolation
│   ├── workers/
│   └── config/
├── outputs/                # → directory-structure
│   └── run_YYYY-MM-DD_HHMMSS/  # → sequential-processing
│       ├── logs/
│       ├── results/
│       └── errors/
├── test_scripts/           # → directory-structure
├── .env                    # → path-management (gitignored)
├── .env.example            # → path-management (template)
├── .gitignore
└── README.md
```

## Decision Tree

**Starting new project?**
→ Use template: `cp -r templates/business_process projects/my_process`

**Organizing existing project?**
→ Start with [directory-structure](../directory-structure/SKILL.md)

**Need resumability?**
→ Apply [sequential-processing](../sequential-processing/SKILL.md)

**Prompts scattered in code?**
→ Apply [prompt-isolation](../prompt-isolation/SKILL.md)

**Hardcoded paths?**
→ Apply [path-management](../path-management/SKILL.md)

**Processing >100 items?**
→ Use [parallel-processing](../parallel-processing/SKILL.md)

## Common Combinations

### Minimal (Simple Process)
- directory-structure
- path-management

### Standard (Most Processes)
- directory-structure
- path-management
- prompt-isolation
- sequential-processing

### Advanced (Large Scale)
- All of the above
- [parallel-processing](../parallel-processing/SKILL.md)

## Quick Reference

| Need | Skill | Key Pattern |
|------|-------|-------------|
| Project layout | directory-structure | functional/ + outputs/ |
| Resumable runs | sequential-processing | run_YYYY-MM-DD_HHMMSS/ |
| Prompt refinement | prompt-isolation | Prompts in .txt files |
| Portable paths | path-management | Relative paths + .env |
| Fault tolerance | sequential-processing | Progress tracking |
| Error debugging | sequential-processing | Separate errors/ |
| Team collaboration | path-management | .env.example |

## Related Skills

- **settings-json-patterns**: Permissions for directories
- **agent-sdk-basics**: Using Agent SDK in scripts
- **git-operations**: Version control best practices
- **writing-skills**: How to create effective skills
- **railway-agent-sdk-deployment**: Deploying agents to Railway

## Why This Was Split

**v1.0.0** was a single massive skill covering everything - too much to digest.

**v2.0.0** is modular:
- Each focused skill is easy to understand
- Apply only what you need
- Clear separation of concerns
- Reference the specific skill when needed

## Migration from project-hygiene

If you were using `project-hygiene`:

1. **Directory structure** → Now in [directory-structure](../directory-structure/SKILL.md)
2. **Logging patterns** → Now in [sequential-processing](../sequential-processing/SKILL.md)
3. **Prompts in files** → Now in [prompt-isolation](../prompt-isolation/SKILL.md)
4. **Path handling** → Now in [path-management](../path-management/SKILL.md)
5. **Worker patterns** → Now in [parallel-processing](../parallel-processing/SKILL.md)

Same patterns, better organization.

## Version History

- 2.1.0: Renamed from project-hygiene to agent-project-setup for better discoverability
  - Added parallel-processing (now exists)
  - Added writing-skills and railway-agent-sdk-deployment to related skills
- 2.0.0: Refactored into focused skills for clarity
- 1.0.0: Original monolithic skill (too large)
