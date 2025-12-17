# ABOUTME: Orchestrator pattern for coordinating multiple parallel workers
# ABOUTME: Manages worker pool, progress tracking, and final reporting

# Orchestration Pattern

## Overview

The orchestrator:
1. Initializes the database
2. Populates items to process
3. Spawns worker pool
4. Tracks progress
5. Reports results

**Important:** Run this in a SUBAGENT to keep main context clean.

## Orchestrator Implementation

```python
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from datetime import datetime
import sqlite3
import logging

def process_with_workers(
    items: list,
    run_dir: Path,
    num_workers: int = 4,
    max_attempts: int = 3
):
    """
    Orchestrate parallel processing with workers

    This should run in a SUBAGENT to keep main context clean
    """
    logger = logging.getLogger(__name__)

    # Initialize database
    db_path = init_worker_db(run_dir)

    # Populate items table
    conn = sqlite3.connect(db_path)
    for item in items:
        item_id = item["id"]
        conn.execute("""
            INSERT OR IGNORE INTO items (id, status)
            VALUES (?, 'pending')
        """, (item_id,))
    conn.commit()

    # Get items that need processing
    cursor = conn.execute("""
        SELECT id FROM items
        WHERE status IN ('pending', 'failed')
        AND attempts < ?
    """, (max_attempts,))
    items_to_process = [row[0] for row in cursor.fetchall()]
    conn.close()

    logger.info(f"Processing {len(items_to_process)} items with {num_workers} workers")

    # Process in parallel
    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        # Submit all tasks
        futures = {
            executor.submit(worker_process_item, db_path, item_id, worker_id): item_id
            for worker_id, item_id in enumerate(items_to_process)
        }

        # Track progress
        completed = 0
        failed = 0

        for future in as_completed(futures):
            item_id = futures[future]
            try:
                success = future.result()
                if success:
                    completed += 1
                    logger.info(f"✓ Completed {item_id} ({completed}/{len(items_to_process)})")
                else:
                    failed += 1
                    logger.warning(f"✗ Failed {item_id}")
            except Exception as e:
                failed += 1
                logger.error(f"✗ Exception for {item_id}: {e}")

    # Final report
    conn = sqlite3.connect(db_path)
    cursor = conn.execute("""
        SELECT status, COUNT(*)
        FROM items
        GROUP BY status
    """)

    logger.info("=" * 50)
    logger.info("Processing complete!")
    for status, count in cursor:
        logger.info(f"{status}: {count}")
    logger.info("=" * 50)

    conn.close()
```

## Running in Subagent

**Why subagent?**
- Keeps main context clean
- Worker output doesn't pollute main conversation
- Can monitor progress without interrupting main task

**Pattern:**
```python
# Main script
from claude_agent_sdk import create_session

async def main():
    # Load items
    items = load_items()

    # Spawn subagent for worker orchestration
    subagent = await create_session(
        name="worker_orchestrator",
        system_prompt="You orchestrate parallel workers"
    )

    prompt = f"""
    Process these {len(items)} items using parallel workers.

    Items: {items}
    Run directory: {run_dir}
    Workers: 4

    Use the patterns from parallel-processing skill.
    Report progress as you go.
    """

    await subagent.send_message(prompt)
```

## Monitoring Progress

```python
def monitor_progress(db_path: Path, interval_seconds: int = 5):
    """Monitor worker progress in real-time"""
    import time

    while True:
        conn = sqlite3.connect(db_path)
        cursor = conn.execute("""
            SELECT status, COUNT(*)
            FROM items
            GROUP BY status
        """)

        status_counts = dict(cursor.fetchall())
        conn.close()

        total = sum(status_counts.values())
        completed = status_counts.get('completed', 0)
        failed = status_counts.get('failed', 0)
        processing = status_counts.get('processing', 0)
        pending = status_counts.get('pending', 0)

        print(f"\rProgress: {completed}/{total} completed, "
              f"{processing} processing, {pending} pending, {failed} failed",
              end='', flush=True)

        if pending == 0 and processing == 0:
            print("\nAll items processed!")
            break

        time.sleep(interval_seconds)

# Run in separate thread
import threading
monitor_thread = threading.Thread(
    target=monitor_progress,
    args=(db_path,),
    daemon=True
)
monitor_thread.start()
```

## Complete Example

```python
# ABOUTME: Parallel processing example with SQLite coordination
# ABOUTME: Processes items using multiple workers with resumability

from pathlib import Path
from datetime import datetime
import logging

def main():
    # Setup
    run_dir = create_run_directory()
    logger = setup_logging(run_dir)

    # Load items to process
    items = [{"id": f"item_{i:03d}"} for i in range(500)]

    logger.info(f"Processing {len(items)} items with parallel workers")

    # Initialize database
    db_path = init_worker_db(run_dir)

    # Process with workers
    process_with_workers(
        items=items,
        run_dir=run_dir,
        num_workers=8,
        max_attempts=3
    )

    # Generate summary
    summary = get_status_summary(db_path)
    logger.info(f"Summary: {summary}")

if __name__ == "__main__":
    main()
```

## Performance Notes

**Typical speedup:**
- 4 workers: 3-3.5x faster than sequential
- 8 workers: 6-7x faster than sequential
- 16 workers: Diminishing returns (I/O bound)

**Optimal worker count:**
- CPU-bound: num_cpus
- I/O-bound (API calls): 2-4x num_cpus
- Test and measure for your workload
