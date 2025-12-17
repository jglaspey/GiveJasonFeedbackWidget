# ABOUTME: SQLite database schema and initialization for parallel worker coordination
# ABOUTME: Defines tables for item tracking and optional worker health monitoring

# SQLite Schema for Worker Coordination

## Core Principle

SQLite provides atomic writes and proper locking. This eliminates race conditions that plague file-based logging when multiple workers write concurrently.

## Database Schema

```python
import sqlite3
from pathlib import Path

def init_worker_db(run_dir: Path) -> Path:
    """Initialize SQLite database for worker coordination"""
    db_path = run_dir / "logs" / "workers.db"

    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id TEXT PRIMARY KEY,
            status TEXT NOT NULL,  -- 'pending', 'processing', 'completed', 'failed'
            worker_id INTEGER,
            started_at TEXT,
            completed_at TEXT,
            result TEXT,
            error TEXT,
            attempts INTEGER DEFAULT 0
        )
    """)

    # Optional: Track worker health
    conn.execute("""
        CREATE TABLE IF NOT EXISTS workers (
            worker_id INTEGER PRIMARY KEY,
            started_at TEXT,
            last_heartbeat TEXT,
            items_processed INTEGER DEFAULT 0,
            items_failed INTEGER DEFAULT 0
        )
    """)

    conn.commit()
    conn.close()

    return db_path
```

## Status Values

| Status | Meaning | Next State |
|--------|---------|------------|
| `pending` | Not yet started | → `processing` |
| `processing` | Currently being worked on | → `completed` or `failed` |
| `completed` | Successfully finished | (terminal) |
| `failed` | Error occurred | → `pending` (for retry) |

## Key Fields

- **id**: Unique identifier for the item (PRIMARY KEY prevents duplicates)
- **status**: Current processing state
- **worker_id**: Which worker claimed this item
- **started_at**: When processing began (ISO timestamp)
- **completed_at**: When processing finished (ISO timestamp)
- **result**: Success output (stored as TEXT, serialize if needed)
- **error**: Failure details (stack trace, error message)
- **attempts**: How many times we've tried (for retry limiting)

## Location

Database file lives at: `{run_dir}/logs/workers.db`

This follows the **directory-structure** skill's convention where logs go in `logs/` subdirectory.
