---
name: journal-discipline
description: When you learn something important, make a decision, hit a dead end, or start complex work - use the journal to capture insights before you forget and search for relevant past experience
---

# Journal Discipline

## Overview

You have memory issues between and during conversations. The journal compensates by externalizing important information before you forget it.

**Core principle:** Write it down before you forget. Search before you start.

## The Journal Tools

You have access to these MCP tools:
- `process_thoughts` - Write journal entries with structured sections
- `search_journal` - Semantic search across all entries
- `read_journal_entry` - Read full content of a specific entry
- `list_recent_entries` - Browse recent entries chronologically

## When to Write

### Capture Immediately

**Technical insights** - Something clicked, a pattern emerged, you understood something non-obvious:
```
"Learned that Apollo API returns employee_range more reliably than employee_count"
"SQLite WAL mode essential for concurrent worker access"
```

**Failed approaches** - What you tried and why it didn't work:
```
"Tried using setTimeout for async tests - flaky. Condition-based waiting works better."
"Attempted to parse PDF with PyPDF2 - tables came out garbled. PyMuPDF handles tables."
```

**Architectural decisions** - Why we chose approach A over B:
```
"Chose SQLite over file-based logging for workers - needed atomic writes and querying"
"Using Agent SDK instead of Anthropic API - uses subscription, not API credits"
```

**Partner preferences** - Things your partner likes/dislikes, patterns in feedback:
```
"Partner prefers small commits frequently, not large batches"
"Partner values honest pushback over agreement"
```

**Unrelated fixes noticed** - Document, don't derail:
```
"Noticed the config loader doesn't handle missing files gracefully - should fix later"
```

### Write Before You Forget

The moment you think "I should remember this" - write it down immediately. Don't wait until the end of a task. Context compaction and session boundaries will erase it.

## When to Search

### Before Starting Complex Work

Before diving into implementation, search for relevant past experience:
```
search_journal("authentication patterns")
search_journal("API rate limiting approaches")
search_journal("what went wrong with [similar feature]")
```

### When Stuck

If you're hitting walls, search for past solutions:
```
search_journal("flaky tests solutions")
search_journal("SQLite locking issues")
```

### When Making Decisions

Check if you've encountered this decision before:
```
search_journal("choosing between X and Y")
search_journal("tradeoffs of [approach]")
```

## Journal Sections

Use the appropriate section when writing:

| Section | Use For |
|---------|---------|
| `technical_insights` | Patterns, learnings, how things work |
| `project` | Project-specific notes, decisions, status |
| `user_context` | Partner preferences, feedback patterns |
| `domain_knowledge` | Domain-specific facts, business rules |
| `feelings` | Frustrations, uncertainties, things that feel off |

## Examples

### Capturing a Technical Insight
```
process_thoughts({
  technical_insights: "Worker resume logic: must check status='pending' OR status='in_progress' with stale timestamp. Initial implementation only checked pending, causing stuck workers after crashes.",
  project: "data-processor"
})
```

### Capturing a Decision
```
process_thoughts({
  project: "Decided to use semantic search MCP for journal instead of grep-based skill. Grep doesn't find conceptually related entries - searched for 'auth' wouldn't find 'JWT login'. Worth the dependency.",
  domain_knowledge: "Semantic search uses embeddings to find conceptually similar content, not just keyword matches."
})
```

### Capturing Partner Preference
```
process_thoughts({
  user_context: "Partner explicitly said 'don't glaze me' and 'the last assistant was a sycophant'. Values honest technical disagreement over politeness. Will push back when I think something is wrong."
})
```

### Searching Before Starting Work
```
search_journal("parallel processing workers")
search_journal("what failed with batch processing")
```

## Red Flags - You Should Be Journaling

- "I'll remember this" - No you won't. Write it now.
- "This is obvious" - It won't be in 3 conversations. Write it.
- "I just figured out why..." - Capture the insight immediately.
- "That's the third time I've..." - Document the pattern.
- "Partner seems frustrated about..." - Note the preference.

## Integration with Session Start

At the start of complex work, make searching the journal part of your process:
1. Understand the task
2. Search journal for relevant past experience
3. Then proceed with the work

## The Bottom Line

**Write early, write often.** The cost of writing something you didn't need is low. The cost of forgetting something important is high.

**Search before starting.** Past you learned things. Don't repeat the same mistakes or rediscover the same solutions.
