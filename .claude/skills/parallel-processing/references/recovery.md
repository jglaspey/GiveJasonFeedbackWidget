# ABOUTME: Failure handling, resumability, and retry patterns for parallel processing
# ABOUTME: Query-based recovery and progress tracking with SQLite

# Recovery and Resumability

## Core Advantage

Unlike file-based logging, SQLite gives you queryable state. You can resume failed runs, retry specific items, and get detailed status reports.

## Resumability Pattern

```python
def get_pending_items(db_path: Path) -> list[str]:
    """Get items that still need processing"""
    conn = sqlite3.connect(db_path)
    cursor = conn.execute("""
        SELECT id FROM items
        WHERE status IN ('pending', 'failed')
        AND attempts < 3
    """)
    items = [row[0] for row in cursor.fetchall()]
    conn.close()
    return items

def get_status_summary(db_path: Path) -> dict:
    """Get current processing status"""
    conn = sqlite3.connect(db_path)
    cursor = conn.execute("""
        SELECT
            status,
            COUNT(*) as count,
            AVG(CAST((julianday(completed_at) - julianday(started_at)) * 86400 AS REAL)) as avg_duration_seconds
        FROM items
        WHERE started_at IS NOT NULL
        GROUP BY status
    """)

    summary = {}
    for status, count, avg_duration in cursor:
        summary[status] = {
            "count": count,
            "avg_duration": avg_duration
        }

    conn.close()
    return summary

# Usage - resume a failed run
pending = get_pending_items(db_path)
if pending:
    logger.info(f"Resuming: {len(pending)} items still pending")
    process_with_workers(pending, run_dir, num_workers=4)
else:
    logger.info("All items completed!")
```

## Retry Logic

```python
def process_with_retries(db_path: Path, max_attempts: int = 3):
    """Retry failed items up to max_attempts"""
    conn = sqlite3.connect(db_path)

    # Get failed items that haven't exceeded retry limit
    cursor = conn.execute("""
        SELECT id, attempts, error
        FROM items
        WHERE status = 'failed'
        AND attempts < ?
    """, (max_attempts,))

    failed_items = cursor.fetchall()
    conn.close()

    if not failed_items:
        return

    logger.info(f"Retrying {len(failed_items)} failed items")

    # Reset to pending for retry
    conn = sqlite3.connect(db_path)
    for item_id, attempts, error in failed_items:
        logger.info(f"Retry {item_id} (attempt {attempts + 1}/{max_attempts})")
        conn.execute("""
            UPDATE items
            SET status = 'pending'
            WHERE id = ?
        """, (item_id,))
    conn.commit()
    conn.close()
```

## Common Failure Scenarios

### Scenario 1: Worker Crash
**Problem:** Worker process dies, item stuck in "processing"

**Detection:**
```python
# Find items stuck in processing for >5 minutes
cursor = conn.execute("""
    SELECT id, worker_id, started_at
    FROM items
    WHERE status = 'processing'
    AND julianday('now') - julianday(started_at) > 0.0035  -- 5 minutes
""")
```

**Recovery:**
```python
# Reset stuck items to pending
conn.execute("""
    UPDATE items
    SET status = 'pending',
        worker_id = NULL
    WHERE status = 'processing'
    AND julianday('now') - julianday(started_at) > 0.0035
""")
conn.commit()
```

### Scenario 2: Transient Failures
**Problem:** Network timeout, API rate limit, temporary service outage

**Solution:** Automatic retry with backoff
```python
# Already handled by max_attempts in worker pattern
# Items with status='failed' and attempts < max_attempts will be retried
```

### Scenario 3: Permanent Failures
**Problem:** Invalid data, permanent API error

**Detection:**
```python
# Find items that hit max retries
cursor = conn.execute("""
    SELECT id, error, attempts
    FROM items
    WHERE status = 'failed'
    AND attempts >= ?
""", (max_attempts,))
```

**Action:** Manual investigation needed - check the error field

## Quick Reference

| Need | Query |
|------|-------|
| Resume processing | `WHERE status IN ('pending', 'failed') AND attempts < ?` |
| Find failures | `WHERE status = 'failed'` |
| Check progress | `SELECT status, COUNT(*) GROUP BY status` |
| Find stuck items | `WHERE status = 'processing' AND started_at < ?` |
| Get error details | `SELECT id, error FROM items WHERE status = 'failed'` |
| Calculate duration | `julianday(completed_at) - julianday(started_at)` |

## Common Mistakes

### Mistake 1: Using Files Instead of SQLite
**Problem:** Multiple workers append to same JSONL file

**Symptoms:**
- Corrupted JSON lines
- Lost progress entries
- Inconsistent state

**Fix:** Use SQLite for any parallel processing

### Mistake 2: Not Running in Subagent
**Problem:** Worker output pollutes main context

**Fix:** Orchestrator runs in subagent, reports summary to main

### Mistake 3: No Retry Logic
**Problem:** Transient failures permanently fail items

**Fix:** Track attempts, retry up to max_attempts

### Mistake 4: Ignoring Worker Failures
**Problem:** Worker crashes, item stuck in "processing"

**Fix:** Add timeout logic or heartbeat monitoring
