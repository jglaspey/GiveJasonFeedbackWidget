---
name: testing-anti-patterns
description: When writing tests and want to avoid common pitfalls - identifies mock-related mistakes, test-only production code, and other patterns that make tests useless
---

# Testing Anti-Patterns

## Overview

**Core principle:** Test what the code does, not what the mocks do.

Mocks are isolation tools, not test subjects.

## The Three Iron Laws

1. Never verify mock behavior in assertions
2. Don't add methods to production classes solely for testing
3. Understand dependencies before implementing mocks

## Major Anti-Patterns

### 1. Testing Mock Existence

**Bad:**
```typescript
const mock = jest.fn();
component.logger = mock;
component.doThing();
expect(mock).toHaveBeenCalled(); // Testing the mock!
```

**Fix:** Either remove the mock or test real behavior the mock enables.

### 2. Test-Only Production Methods

**Bad:**
```typescript
class Service {
  // Added just for testing
  _resetForTesting() { this.state = null; }
}
```

**Fix:** Put test utilities in test helper modules, not production code.

### 3. Mocking Without Understanding

**Bad:** Mocking a dependency without understanding its side effects, breaking behavior the test actually needs.

**Fix:** Understand what the dependency does before deciding to mock it.

### 4. Incomplete Mock Responses

**Bad:**
```typescript
mock.mockReturnValue({ id: 1 }); // Real returns { id, name, createdAt, ... }
```

**Fix:** Mocks must mirror complete real API structure. Partial mocks hide structural assumptions.

### 5. Tests as Afterthought

**Bad:** Writing implementation first, then struggling to test it.

**Fix:** TDD prevents these problems by forcing you to understand behavior requirements upfront.

## Prevention

Following strict TDD naturally prevents these anti-patterns:
- Write failing test first → forces understanding behavior
- Observe failure against real code → catches mock issues
- Implement minimally → no test-only methods needed

## Quick Reference

| Anti-Pattern | Symptom | Fix |
|--------------|---------|-----|
| Testing mocks | `expect(mock).toHaveBeenCalled()` | Test real behavior |
| Test-only methods | `_resetForTesting()` in production | Move to test helpers |
| Blind mocking | Tests break mysteriously | Understand dependencies first |
| Partial mocks | Integration failures | Complete mock responses |
| Tests-after | Hard to test = tangled code | TDD from start |

## Related Skills

- **test-driven-development** - The cure for most anti-patterns
