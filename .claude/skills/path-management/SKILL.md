---
name: Machine-Agnostic Path Management
description: When writing code that runs on multiple machines, setting up projects for team use, or when you see hardcoded paths like /Users/username/
when_to_use: |
  - Writing code that runs on multiple machines
  - Setting up project for team use
  - Deploying to different environments
  - Symptoms: "works on my machine", "hardcoded paths", "/Users/justin/..."
  - Keywords: paths, .env, relative paths, portability, environment variables
version: 1.0.0
languages: python, javascript
---

# Machine-Agnostic Path Management

## Overview

Hardcoded machine-specific paths break when code runs elsewhere. This skill shows how to write portable path code using relative paths and environment variables.

**Core principle:** No hardcoded machine-specific paths. Ever.

## The Problem

### ❌ Hardcoded Paths

```python
# DON'T - Works only on Justin's Mac
data_path = "/Users/justin/projects/data/input.csv"
output_path = "/Users/justin/projects/outputs/results.json"

# DON'T - Windows-specific
data_path = "C:\\Users\\Justin\\data\\input.csv"

# DON'T - Assumes specific directory structure
data_path = "/var/data/production/input.csv"
```

**Problems:**
- Breaks on teammate's machine
- Breaks in CI/CD
- Breaks in production
- Hard to maintain

## The Solutions

### Solution 1: Relative to Project Root

✅ **Best for:** Paths within the project

```python
from pathlib import Path

# Get project root relative to current file
project_root = Path(__file__).parent.parent

# Build paths from there
data_path = project_root / "data" / "input.csv"
output_path = project_root / "outputs" / "results.json"
prompts_dir = project_root / "functional" / "prompts"
```

**Why it works:**
- `Path(__file__)` = current script location
- `.parent.parent` = go up to project root
- `/` operator builds paths correctly for any OS
- Works on Mac, Linux, Windows

### Solution 2: Environment Variables

✅ **Best for:** Machine-specific config

```python
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get paths from environment
data_dir = Path(os.getenv("DATA_DIR", "data"))  # Default to "data"
input_file = data_dir / "input.csv"

# Or required variables (error if missing)
api_key = os.getenv("API_KEY")
if not api_key:
    raise ValueError("API_KEY environment variable required")
```

**.env file (gitignored):**
```bash
# Local configuration
DATA_DIR=/mnt/data
OUTPUT_DIR=/mnt/outputs
TEMP_DIR=/tmp/process_temp
API_KEY=your_secret_key
```

**.env.example (version controlled):**
```bash
# Copy to .env and customize
DATA_DIR=data
OUTPUT_DIR=outputs
TEMP_DIR=temp
API_KEY=your_key_here
```

## Standard Patterns

### Project Path Helper

```python
from pathlib import Path
from typing import Union

class ProjectPaths:
    """Centralized path management for project"""

    def __init__(self, script_file: str):
        # Determine project root from script location
        self.root = Path(script_file).parent.parent

        # Define standard directories
        self.functional = self.root / "functional"
        self.scripts = self.functional / "scripts"
        self.prompts = self.functional / "prompts"
        self.config = self.functional / "config"
        self.workers = self.functional / "workers"

        self.outputs = self.root / "outputs"
        self.test_scripts = self.root / "test_scripts"

    def get_prompt(self, name: str) -> Path:
        """Get path to prompt file"""
        return self.prompts / f"{name}.txt"

    def get_config(self, name: str) -> Path:
        """Get path to config file"""
        return self.config / name

    def create_run_dir(self, base: str = None) -> Path:
        """Create timestamp-based run directory"""
        from datetime import datetime

        if base is None:
            base = self.outputs

        run_id = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        run_dir = base / f"run_{run_id}"
        run_dir.mkdir(parents=True, exist_ok=True)

        return run_dir

# Usage
paths = ProjectPaths(__file__)
prompt = paths.get_prompt("analyze")
config = paths.get_config("items.json")
run_dir = paths.create_run_dir()
```

### Environment Configuration

```python
import os
from pathlib import Path
from dotenv import load_dotenv
from typing import Optional

class Config:
    """Configuration from environment variables"""

    def __init__(self):
        load_dotenv()

        # Paths (with defaults)
        self.data_dir = Path(os.getenv("DATA_DIR", "data"))
        self.output_dir = Path(os.getenv("OUTPUT_DIR", "outputs"))
        self.temp_dir = Path(os.getenv("TEMP_DIR", "temp"))

        # Process settings
        self.max_items = int(os.getenv("MAX_ITEMS_PER_RUN", "1000"))
        self.log_level = os.getenv("LOG_LEVEL", "INFO")

        # Secrets
        self.api_key = os.getenv("API_KEY")

        # Validate required settings
        if not self.api_key:
            raise ValueError("API_KEY must be set in .env")

    def get_input_path(self, filename: str) -> Path:
        """Get input file path"""
        return self.data_dir / filename

    def get_output_path(self, filename: str) -> Path:
        """Get output file path"""
        return self.output_dir / filename

# Usage
config = Config()
input_file = config.get_input_path("items.json")
output_file = config.get_output_path("results.json")
```

## Path Resolution Strategies

### Strategy 1: Script-Relative (Within Project)

```python
# For files within the project
project_root = Path(__file__).parent.parent
path = project_root / "functional" / "prompts" / "analyze.txt"
```

**Use when:**
- Files are part of the project
- In version control
- Same structure on all machines

### Strategy 2: Environment Variable (External)

```python
# For files outside the project
data_dir = Path(os.getenv("DATA_DIR"))
path = data_dir / "input.csv"
```

**Use when:**
- Files outside project structure
- Location varies by machine
- External data sources

### Strategy 3: Configurable with Default

```python
# Best of both worlds
from pathlib import Path
import os

# Default to project location, allow override
default_data_dir = Path(__file__).parent.parent / "data"
data_dir = Path(os.getenv("DATA_DIR", str(default_data_dir)))
```

**Use when:**
- Want local development to "just work"
- But allow production override

## Cross-Platform Compatibility

### Use Path from pathlib

```python
from pathlib import Path

# ✅ Works on all platforms
path = Path("data") / "input.csv"
path = Path.home() / ".config" / "app"

# ❌ Don't use string concatenation
path = "data/" + "input.csv"  # Breaks on Windows
path = "data\\" + "input.csv"  # Breaks on Unix
```

### Path Separators

```python
# ✅ Use Path - handles separators automatically
path = project_root / "data" / "subdir" / "file.txt"

# ❌ Don't hardcode separators
path = project_root + "/data/subdir/file.txt"  # Breaks on Windows
path = project_root + "\\data\\subdir\\file.txt"  # Breaks on Unix
```

### Converting to String

```python
# When you need a string (for APIs, etc.)
path = Path("data") / "input.csv"

# Convert to string
path_str = str(path)  # Correct for current OS

# Or absolute path
abs_path = str(path.absolute())
```

## Setup Instructions for Teams

### .env.example Template

```bash
# Copy this file to .env and customize for your machine
# .env is gitignored and will not be committed

# Data directories (adjust paths for your system)
DATA_DIR=data
OUTPUT_DIR=outputs
TEMP_DIR=temp

# API configuration
API_KEY=your_api_key_here
API_BASE_URL=https://api.example.com

# Process settings
MAX_ITEMS_PER_RUN=1000
LOG_LEVEL=INFO
ENABLE_DEBUG=false

# Machine-specific paths (if needed)
# CUSTOM_PATH=/path/to/something
```

### README Instructions

```markdown
## Setup

1. Clone repository
2. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
3. Edit `.env` with your machine-specific configuration
4. Run the process:
   ```bash
   python functional/scripts/process.py
   ```
```

## Common Mistakes

### Mistake 1: Absolute Paths
**Problem:** `/Users/justin/data/input.csv`

**Fix:** Relative to project root or environment variable

### Mistake 2: Windows-Specific Paths
**Problem:** `C:\\Users\\...` in code

**Fix:** Use pathlib.Path, works cross-platform

### Mistake 3: String Concatenation
**Problem:** `base_path + "/subdir/" + filename`

**Fix:** `Path(base_path) / "subdir" / filename`

### Mistake 4: Committing .env
**Problem:** Secrets in version control

**Fix:** .gitignore .env, commit .env.example instead

### Mistake 5: Missing .env.example
**Problem:** New team members don't know what to configure

**Fix:** Provide .env.example with all variables documented

## Quick Reference

| Scenario | Solution |
|----------|----------|
| File in project | `Path(__file__).parent.parent / "data" / "file"` |
| External data | `Path(os.getenv("DATA_DIR")) / "file"` |
| With default | `Path(os.getenv("DIR", "default")) / "file"` |
| Cross-platform | Always use `pathlib.Path`, never string concat |
| Secrets | Store in .env, never hardcode |
| Team setup | Provide .env.example |

## Related Skills

- **directory-structure**: Standard project layout
- **sequential-processing**: Where outputs go
- **prompt-isolation**: Loading prompts with relative paths

## Real-World Impact

**Before:**
- "Works on my machine" syndrome
- Breaks in CI/CD
- Team members can't run project
- Manual path updates for each environment

**After:**
- Works everywhere immediately
- CI/CD works without changes
- New team members: copy .env.example, done
- Deploy to production: just set environment variables

## Version History

- 1.0.0: Extracted from agent-project-setup skill for clarity
