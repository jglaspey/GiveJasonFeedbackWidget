# ABOUTME: Worker function implementation pattern for processing individual items
# ABOUTME: Shows atomic state transitions and error handling with SQLite coordination

# Worker Pattern

## Worker Function

Each worker is an independent process that:
1. Claims an item atomically
2. Processes it
3. Updates status atomically
4. Handles errors gracefully

```python
import sqlite3
import time
from pathlib import Path
from typing import Any

def worker_process_item(db_path: Path, item_id: str, worker_id: int) -> bool:
    """
    Worker function - processes one item with SQLite coordination

    Returns True if successful, False if failed
    """
    conn = sqlite3.connect(db_path)

    try:
        # Mark as processing (atomic)
        conn.execute("""
            UPDATE items
            SET status = 'processing',
                worker_id = ?,
                started_at = datetime('now'),
                attempts = attempts + 1
            WHERE id = ? AND status IN ('pending', 'failed')
        """, (worker_id, item_id))
        conn.commit()

        # Check if we got the lock (another worker might have grabbed it)
        cursor = conn.execute(
            "SELECT worker_id FROM items WHERE id = ?",
            (item_id,)
        )
        row = cursor.fetchone()
        if row and row[0] != worker_id:
            # Another worker grabbed it first
            return False

        # Do the actual work
        result = expensive_operation(item_id)

        # Mark as completed (atomic)
        conn.execute("""
            UPDATE items
            SET status = 'completed',
                completed_at = datetime('now'),
                result = ?
            WHERE id = ?
        """, (str(result), item_id))
        conn.commit()

        return True

    except Exception as e:
        # Mark as failed (atomic)
        conn.execute("""
            UPDATE items
            SET status = 'failed',
                completed_at = datetime('now'),
                error = ?
            WHERE id = ?
        """, (str(e), item_id))
        conn.commit()

        return False

    finally:
        conn.close()


def expensive_operation(item_id: str) -> Any:
    """Replace with your actual processing logic"""
    # Simulate work
    time.sleep(1)
    return {"item_id": item_id, "processed": True}
```

## Key Design Points

### 1. Atomic Claiming

```python
UPDATE items
SET status = 'processing', worker_id = ?
WHERE id = ? AND status IN ('pending', 'failed')
```

This prevents race conditions. Only one worker can successfully claim an item.

### 2. Lock Verification

```python
cursor = conn.execute("SELECT worker_id FROM items WHERE id = ?", (item_id,))
row = cursor.fetchone()
if row and row[0] != worker_id:
    # Another worker grabbed it first
    return False
```

Double-check that we actually got the item (another worker might have claimed it between transactions).

### 3. Error Isolation

Each worker catches its own exceptions and marks items as failed. One worker's crash doesn't affect others.

### 4. Separate Connections

Each worker opens its own SQLite connection. SQLite handles the locking automatically.

## Return Values

- `True`: Item processed successfully
- `False`: Item failed or was claimed by another worker

The orchestrator can track these to report overall progress.

## Customization Points

Replace `expensive_operation()` with your actual processing logic:
- API calls
- File transformations
- Data validation
- Whatever your business process needs
