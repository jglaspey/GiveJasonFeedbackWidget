---
name: Parallel Processing (Multiple Workers)
description: Coordinating multiple Python workers with SQLite-based progress tracking for concurrent processing of large datasets
when_to_use: |
  - Processing >100 items (need speed)
  - Operations that can run in parallel
  - Multiple workers running concurrently
  - Need fault isolation per item
  - ⚠️ For sequential processing (single worker), see sequential-processing skill
  - Keywords: parallel, multiple workers, concurrency, SQLite, coordination, race conditions, atomic
version: 3.0.0
languages: python
---

# Parallel Processing (Multiple Workers)

## When to Use This Skill

✅ **Use parallel-processing when:**
- Processing >100 items
- Operations can run independently
- Want faster throughput
- Need fault isolation (one failure doesn't stop others)

❌ **Use sequential-processing instead when:**
- Processing sequentially (one at a time)
- < 100 items
- Operations must run in specific order
- Simple scripts

**Why the distinction:** File-based logging (JSONL append) has race conditions with multiple writers. SQLite provides proper locking and atomicity.

## Core Principle

**SQLite for coordination, not files.** Workers are independent processes that coordinate through atomic database operations.

## Architecture

```
Main Orchestrator (runs in subagent)
    ↓
    ├─→ Worker 1 ─→ SQLite DB ←─ Worker 2
    ├─→ Worker 3 ─→ SQLite DB ←─ Worker 4
    └─→ Worker N ─→ SQLite DB
         ↑
         └── All workers write atomically
```

**Key decisions:**
1. **Orchestrator in subagent** - Keeps main context clean
2. **SQLite for coordination** - Atomic writes, no race conditions
3. **Workers as processes** - True parallelism, fault isolation
4. **Status tracking per item** - Resume on failure

## Progressive Disclosure

Read the detailed references for implementation:

**For database setup:** Read `references/sqlite-schema.md`
- Database schema and initialization
- Table structure and status values
- Field meanings and conventions

**For worker implementation:** Read `references/worker-pattern.md`
- Worker function with atomic state transitions
- Error handling and isolation
- Return values and customization

**For coordinating workers:** Read `references/orchestration.md`
- Orchestrator pattern and progress tracking
- Running in subagent
- Monitoring and reporting
- Complete working example

**For failure handling:** Read `references/recovery.md`
- Resuming failed runs
- Retry logic and backoff
- Common failure scenarios
- Query-based debugging

## Quick Start

1. Initialize database: `db_path = init_worker_db(run_dir)`
2. Create worker function: `worker_process_item(db_path, item_id, worker_id)`
3. Run orchestrator: `process_with_workers(items, run_dir, num_workers=4)`
4. Monitor progress: Query status counts from database
5. Handle failures: Resume with `get_pending_items(db_path)`

## Quick Reference

| Need | Solution |
|------|----------|
| Coordinate workers | SQLite database |
| Track progress | items table with status |
| Resumability | Query pending/failed items |
| Retry failed | Update status to pending, re-run |
| Monitor progress | Query status counts periodically |
| Fault isolation | Each worker independent process |
| Clean context | Run orchestrator in subagent |

## When NOT to Use This

❌ **Sequential processing** - Use sequential-processing instead
❌ **< 100 items** - Overhead not worth it
❌ **Order matters** - Workers process independently
❌ **Shared state needed** - Workers are isolated

## Related Skills

- **sequential-processing**: For sequential processing (simpler)
- **directory-structure**: Where workers.db lives (logs/)
- **path-management**: Database paths in code

## Evidence

This skill uses progressive disclosure based on proven patterns:

**Pattern #12** (0.90 confidence): "Progressive disclosure reduces context by 70%+"
- Original: 536 lines all in SKILL.md
- Restructured: ~100 line entry point + 4 focused reference files
- Result: 80%+ reduction in initial context load

**Experiment #21**: "Three-tier progressive disclosure reduces token usage"
- Entry point → Topic references → Code examples
- Readers load only what they need
- Maintains all original content without loss

This structure lets you quickly understand when and why to use parallel processing, then drill into specific implementation details only when needed.
