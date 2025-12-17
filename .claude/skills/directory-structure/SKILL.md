---
name: Agent Project Directory Structure
description: When starting a new business process project, organizing agent files, or separating generated outputs from functional code
when_to_use: |
  - Starting new business process project
  - Organizing agent project files
  - Setting up outputs directory
  - Symptoms: "where should files go?", "outputs mixed with code", "git status cluttered"
  - Keywords: directory structure, functional, outputs, organization
version: 1.0.0
languages: all
---

# Agent Project Directory Structure

## Overview

Business process agents need a clear separation between code (functional/) and generated outputs (outputs/). This pattern makes projects maintainable and git-friendly.

**Core principle:** Separate what runs (functional code) from what's generated (outputs).

## Standard Layout

```
project_name/
├── .claude/
│   ├── CLAUDE.md           # Process-specific instructions
│   └── settings.json       # Restrictive permissions
├── functional/
│   ├── scripts/            # Python/JS scripts
│   ├── prompts/            # Isolated prompt files
│   ├── workers/            # Parallel processing workers
│   └── config/             # Configuration files
├── outputs/                # Gitignored
│   └── run_YYYY-MM-DD_HHMMSS/
│       ├── logs/
│       ├── results/
│       └── errors/
├── test_scripts/           # Testing/validation scripts
├── .env.example
├── .gitignore
└── README.md
```

## Key Directories

### functional/ (Version Controlled)

**Purpose:** Code that runs the process

**Contains:**
- `scripts/` - Main process scripts
- `prompts/` - Prompt templates (see prompt-isolation skill)
- `workers/` - Parallel processing workers
- `config/` - Configuration files, input templates

**Why separate:**
- Track in git
- Evolves over time
- Shared across runs

### outputs/ (Gitignored)

**Purpose:** Run-specific generated data

**Contains:**
- `run_YYYY-MM-DD_HHMMSS/` - Timestamp-based run directories
- Each run isolated in its own directory
- See sequential-processing skill for run directory structure

**Why separate:**
- Never commit outputs
- Each run independent
- Easy to clean up old runs
- Historical analysis

### test_scripts/ (Optional)

**Purpose:** Test and validation scripts

**Why separate:**
- Keeps tests out of functional/
- Prevents clutter (test.py, test2.py, etc.)
- Clear distinction: functional = production, test_scripts = testing

## .gitignore Pattern

```gitignore
# Outputs (run-specific, never commit)
outputs/
logs/
*.log

# Secrets
.env
.env.*
secrets.json

# Python
__pycache__/
*.pyc

# Database
*.db
*.sqlite

# Keep structure
!outputs/.gitkeep
```

## Setup Pattern

```python
from pathlib import Path

# Project paths (relative to script)
project_root = Path(__file__).parent.parent
functional_dir = project_root / "functional"
outputs_dir = project_root / "outputs"

# Ensure outputs directory exists
outputs_dir.mkdir(exist_ok=True)
```

## Common Mistakes

### Mistake 1: Outputs in Git
**Problem:** Committing outputs/ directory

**Symptoms:**
- Git status always shows changes
- Large repo size
- Merge conflicts on output files

**Fix:** Add `outputs/` to .gitignore immediately

### Mistake 2: Code in Outputs
**Problem:** Putting scripts in outputs/

**Why bad:** Can't track changes, hard to find code

**Fix:** Scripts always go in functional/scripts/

### Mistake 3: Test Files Scattered
**Problem:** test.py, test_new.py, temp_test.py everywhere

**Fix:** All tests in test_scripts/ directory

### Mistake 4: No Separation
**Problem:** Everything at project root

**Symptoms:**
- Hard to find files
- Can't tell what's code vs output
- Git status messy

**Fix:** Follow standard layout from day 1

## Quick Reference

| File Type | Location | Git Tracked? |
|-----------|----------|--------------|
| Python scripts | functional/scripts/ | ✅ Yes |
| Prompts | functional/prompts/ | ✅ Yes |
| Config files | functional/config/ | ✅ Yes |
| Workers | functional/workers/ | ✅ Yes |
| Run outputs | outputs/run_XXX/ | ❌ No |
| Logs | outputs/run_XXX/logs/ | ❌ No |
| Results | outputs/run_XXX/results/ | ❌ No |
| Errors | outputs/run_XXX/errors/ | ❌ No |
| Test scripts | test_scripts/ | ✅ Yes |
| Environment vars | .env | ❌ No |
| Env template | .env.example | ✅ Yes |

## Related Skills

- **sequential-processing**: Structure of run directories
- **prompt-isolation**: Why prompts go in functional/prompts/
- **path-management**: How to reference these directories in code
- **settings-json-patterns**: Permissions for each directory

## Real-World Impact

**Before:**
- Mixed code and outputs
- Git status cluttered
- Hard to clean up old runs
- Confusion about what to track

**After:**
- Clean separation
- Git shows only code changes
- Easy to manage outputs
- Clear project organization

## Version History

- 1.0.0: Extracted from agent-project-setup skill for clarity
