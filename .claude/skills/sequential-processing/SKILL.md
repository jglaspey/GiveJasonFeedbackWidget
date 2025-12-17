---
name: Sequential Processing (Single Worker)
description: When processing items sequentially with a single worker, when you need to resume after failures, or when you want historical run records with JSONL logging
when_to_use: |
  - Sequential processing (one item at a time, single worker)
  - Long-running single-process operations
  - Need to resume after failures
  - Want historical record of runs
  - < 100 items where sequential processing is acceptable
  - ⚠️ NOT for parallel workers (>1 worker) - see parallel-processing skill
  - Symptoms: "lost progress", "must restart from beginning", "can't tell what happened"
  - Keywords: sequential, single worker, logging, resumability, progress, timestamp, errors, JSONL
version: 3.0.0
languages: all
---

# Sequential Processing (Single Worker)

## Overview

Business process agents run on unreliable infrastructure, process many items, and fail partway through. This skill shows how to track progress and resume from failures for **sequential processing**.

**Core principle:** Every run creates a timestamp directory. Track progress so you can resume.

## ⚠️ Sequential Processing Only

This skill covers file-based logging for **sequential processes** (one item at a time).

**For parallel workers (>1 worker):** Use **[parallel-processing](../parallel-processing/SKILL.md)** skill instead.

**Why?** File-based progress logs (`open("a")`) have race conditions with concurrent writers:
- Multiple workers writing to same file → corrupted JSON lines
- Lost progress entries from interleaved writes
- Inconsistent state during reads

**SQLite (in parallel-processing) provides:**
- Atomic writes
- Proper locking
- No race conditions

**Use this skill when:**
- ✅ Processing items sequentially (one at a time)
- ✅ Single process/script
- ✅ < 100 items (sequential is fine)
- ✅ Want simple, human-readable logs

**Use parallel-processing when:**
- ❌ Multiple workers processing concurrently
- ❌ > 100 items (need speed)
- ❌ Operations can run independently

## Timestamp-Based Run Directories

### Pattern

```python
from pathlib import Path
from datetime import datetime

def create_run_directory(base_dir: Path = Path("outputs")) -> Path:
    """Create timestamp-based run directory"""
    run_id = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    run_dir = base_dir / f"run_{run_id}"

    # Create subdirectories
    (run_dir / "logs").mkdir(parents=True, exist_ok=True)
    (run_dir / "results").mkdir(parents=True, exist_ok=True)
    (run_dir / "errors").mkdir(parents=True, exist_ok=True)

    return run_dir

# Usage
run_dir = create_run_directory()
# Creates: outputs/run_2025-01-15_143022/
```

### Why Timestamps?

✅ **Never overwrites** - Each run isolated
✅ **Historical record** - Compare runs over time
✅ **Debugging** - Know exactly when something ran
✅ **Safe experimentation** - Can't lose old results

## Progress Logging

### Two Log Formats

**1. Human-readable (.log)** - For debugging

```python
import logging

def setup_logging(run_dir: Path) -> logging.Logger:
    """Configure logging for this run"""
    log_file = run_dir / "logs" / "progress.log"

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

# Usage
logger = setup_logging(run_dir)
logger.info("Processing started")
logger.info(f"Processing item {item_id}")
logger.error(f"Failed item {item_id}: {error}")
```

**2. Machine-readable (.jsonl)** - For resumability

```python
import json
from datetime import datetime

def log_progress(run_dir: Path, item_id: str, status: str, details: dict = None):
    """Log progress in JSONL format for resumability"""
    progress_file = run_dir / "logs" / "progress.jsonl"

    entry = {
        "timestamp": datetime.now().isoformat(),
        "item_id": item_id,
        "status": status,  # "completed", "failed", "skipped"
        "details": details or {}
    }

    with progress_file.open("a") as f:
        f.write(json.dumps(entry) + "\n")

# Usage
log_progress(run_dir, "item_001", "completed", {"duration": 1.5})
log_progress(run_dir, "item_002", "failed", {"error": "timeout"})
```

## Resumability Pattern

### Loading Completed Items

```python
from typing import Set
import json

def load_completed_items(run_dir: Path) -> Set[str]:
    """Load IDs of already-completed items"""
    progress_file = run_dir / "logs" / "progress.jsonl"

    if not progress_file.exists():
        return set()

    completed = set()
    with progress_file.open("r") as f:
        for line in f:
            if not line.strip():
                continue
            entry = json.loads(line)
            if entry["status"] == "completed":
                completed.add(entry["item_id"])

    return completed
```

### Resumable Processing

```python
def process_with_resumability(items: list, run_dir: Path, logger):
    """Process items with ability to resume"""
    # Load what's already done
    completed = load_completed_items(run_dir)
    logger.info(f"Already completed: {len(completed)} items")

    for item in items:
        item_id = item["id"]

        # Skip if already completed
        if item_id in completed:
            logger.info(f"Skipping {item_id} (already done)")
            continue

        try:
            # Process item
            result = process_item(item)

            # Log success
            log_progress(run_dir, item_id, "completed", {"result": result})
            logger.info(f"✓ Completed {item_id}")

        except Exception as e:
            # Log failure (see error isolation below)
            log_error(run_dir, item_id, e)
            log_progress(run_dir, item_id, "failed", {"error": str(e)})
            logger.error(f"✗ Failed {item_id}: {e}")

            # Continue with next item (fault tolerance)
            continue
```

## Error Isolation

### Pattern

```python
import json
import traceback

def log_error(run_dir: Path, item_id: str, error: Exception, context: dict = None):
    """Log error with full context in separate file"""
    errors_dir = run_dir / "errors"
    errors_dir.mkdir(parents=True, exist_ok=True)

    error_file = errors_dir / f"item_{item_id}_error.json"

    error_data = {
        "timestamp": datetime.now().isoformat(),
        "item_id": item_id,
        "error_type": type(error).__name__,
        "error_message": str(error),
        "traceback": traceback.format_exc(),
        "context": context or {}
    }

    with error_file.open("w") as f:
        json.dump(error_data, f, indent=2)

# Usage
try:
    process_item(item)
except Exception as e:
    log_error(run_dir, item["id"], e, context={"item": item})
```

### Why Separate Error Files?

✅ **Easy to find** - All errors in one place
✅ **Full context** - Stack traces, item data preserved
✅ **Analysis** - Can aggregate patterns
✅ **Debugging** - Don't search through logs

## Run Directory Structure

```
outputs/run_2025-01-15_143022/
├── logs/
│   ├── progress.log        # Human-readable log
│   └── progress.jsonl      # Machine-readable progress
├── results/
│   ├── final_output.json   # Main results
│   └── summary.json        # Statistics
└── errors/                 # Only if failures occurred
    ├── item_123_error.json
    └── item_456_error.json
```

## Summary Generation

```python
def generate_summary(run_dir: Path, items: list, results: list, errors_count: int):
    """Create summary file for this run"""
    summary = {
        "run_id": run_dir.name,
        "timestamp": datetime.now().isoformat(),
        "total_items": len(items),
        "completed": len(results),
        "failed": errors_count,
        "success_rate": len(results) / len(items) if items else 0
    }

    summary_file = run_dir / "results" / "summary.json"
    with summary_file.open("w") as f:
        json.dump(summary, f, indent=2)

    return summary
```

## Complete Example

```python
from pathlib import Path
from datetime import datetime
import logging
import json

def main():
    # Create run directory
    run_dir = create_run_directory()
    logger = setup_logging(run_dir)

    logger.info(f"Starting run: {run_dir.name}")

    # Load items
    items = load_items()

    # Check resumability
    completed = load_completed_items(run_dir)
    logger.info(f"Already completed: {len(completed)} items")

    # Process
    results = []
    errors_count = 0

    for item in items:
        item_id = item["id"]

        if item_id in completed:
            logger.info(f"Skipping {item_id}")
            continue

        try:
            result = process_item(item)
            results.append(result)
            log_progress(run_dir, item_id, "completed")
            logger.info(f"✓ {item_id}")
        except Exception as e:
            log_error(run_dir, item_id, e, {"item": item})
            log_progress(run_dir, item_id, "failed")
            logger.error(f"✗ {item_id}")
            errors_count += 1

    # Summary
    summary = generate_summary(run_dir, items, results, errors_count)
    logger.info(f"Complete: {summary['completed']}/{summary['total_items']}")
```

## Common Mistakes

### Mistake 1: Overwriting Runs
**Problem:** Using fixed filename like `results.json`

**Fix:** Timestamp-based directories

### Mistake 2: No Progress Tracking
**Problem:** Can't resume after failure

**Fix:** Log progress in .jsonl format, check before processing

### Mistake 3: Errors in Main Log
**Problem:** Errors mixed with progress, hard to find

**Fix:** Separate errors/ directory

### Mistake 4: Lost Context
**Problem:** Error logged without item data

**Fix:** Include full context in error files

## Quick Reference

| Need | Solution |
|------|----------|
| Unique run directory | `run_YYYY-MM-DD_HHMMSS/` |
| Human-readable logs | `logs/progress.log` |
| Machine-readable progress | `logs/progress.jsonl` |
| Resumability | Load completed IDs from .jsonl |
| Error debugging | Separate file per error in errors/ |
| Run statistics | `results/summary.json` |

## Related Skills

- **directory-structure**: Where run directories live
- **prompt-isolation**: Prompts versioned in functional/
- **parallel-processing**: SQLite for worker coordination (not files!)

## Real-World Impact

**Before:**
- 2+ hours to find where failure occurred
- Must restart from beginning after crash
- No historical record of runs
- Errors lost in logs

**After:**
- 5-10 minutes to identify failures (check errors/)
- Resume from last successful item
- Historical analysis of all runs
- Full error context preserved

## Version History

- 1.0.0: Extracted from agent-project-setup skill for clarity
