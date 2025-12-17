---
name: condition-based-waiting
description: When tests have race conditions, timing dependencies, or pass/fail inconsistently - replaces arbitrary timeouts with condition polling for reliable async tests
---

# Condition-Based Waiting

## Overview

**Core principle:** Wait for the actual condition you care about, not a guess about how long it takes.

## When to Use

- Tests with arbitrary delays (`setTimeout`, `sleep`)
- Flaky tests that sometimes pass, sometimes fail
- Timeout issues in parallel execution
- Any async operation where timing varies

## When NOT to Use

- Testing actual timing behavior (debounce, throttle intervals)
- Fixed protocol delays (must wait exactly N ms)

## The Pattern

**Bad - Guessing:**
```typescript
await doThing();
await sleep(500); // Hope it's done?
expect(result).toBe(expected);
```

**Good - Condition-based:**
```typescript
await doThing();
await waitFor(() => result === expected);
expect(result).toBe(expected);
```

## Implementation

```typescript
async function waitFor(
  condition: () => boolean | Promise<boolean>,
  options: { timeout?: number; interval?: number } = {}
): Promise<void> {
  const { timeout = 5000, interval = 10 } = options;
  const start = Date.now();

  while (Date.now() - start < timeout) {
    if (await condition()) return;
    await new Promise(r => setTimeout(r, interval));
  }

  throw new Error(`Condition not met within ${timeout}ms`);
}
```

## Common Scenarios

| Waiting For | Condition |
|-------------|-----------|
| Event emitted | `() => eventReceived` |
| State change | `() => state === 'ready'` |
| Item count | `() => items.length >= 3` |
| File exists | `() => fs.existsSync(path)` |
| Element visible | `() => element.isVisible()` |

## Common Pitfalls

- **Polling too fast** - 10ms is usually fine, 1ms wastes CPU
- **No timeout** - Always include timeout to prevent infinite loops
- **Stale data** - Call getters inside the condition, not before

## When Fixed Delays ARE Needed

Rare cases where fixed delays are appropriate:
- Combined with condition-based waiting
- Documented reasoning ("API requires 100ms cooldown")
- Testing actual timing behavior

## Results

Real improvements from adopting this pattern:
- Flaky test pass rate: 60% → 100%
- Test execution: ~40% faster
