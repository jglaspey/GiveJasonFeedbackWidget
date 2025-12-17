---
name: defense-in-depth
description: When fixing bugs and want to prevent recurrence - adds validation at multiple layers so the bug becomes structurally impossible, not just fixed in one place
---

# Defense-in-Depth Validation

## Overview

**Core principle:** Validate at EVERY layer data passes through. Make the bug structurally impossible.

Single validation points can be bypassed through:
- Alternative code paths
- Refactored logic
- Test mocks

By distributing validation across layers, the system becomes resilient.

## The Four Layers

### Layer 1: Entry Point Validation
Prevent obviously invalid input at API boundaries.

```typescript
function createProject(directory: string) {
  if (!directory || !fs.existsSync(directory)) {
    throw new Error('Invalid directory');
  }
  // ...
}
```

### Layer 2: Business Logic Validation
Ensure data makes semantic sense.

```typescript
function initWorkspace(dir: string) {
  if (!path.isAbsolute(dir)) {
    throw new Error('Workspace requires absolute path');
  }
  // ...
}
```

### Layer 3: Environment Guards
Prevent dangerous operations in specific contexts.

```typescript
function gitInit(directory: string) {
  if (process.env.NODE_ENV === 'test' && !directory.includes('/tmp')) {
    throw new Error('Tests must use temp directories');
  }
  // ...
}
```

### Layer 4: Debug Instrumentation
Capture context for forensic analysis.

```typescript
function gitInit(directory: string) {
  console.error('git init:', { directory, cwd: process.cwd() });
  // ...
}
```

## Implementation Pattern

After finding a root cause:

1. **Trace data flow** - Map all layers data passes through
2. **Add validation at each layer** - Not just where error occurred
3. **Test bypass scenarios** - Verify bypassing one layer triggers another

## Example

Bug: Empty `projectDir` caused `git init` in wrong location.

**Fixed with 4 layers:**
```
Layer 1: Project.create() → validates directory exists
Layer 2: WorkspaceManager → validates not empty string
Layer 3: NODE_ENV guard → refuses outside tmpdir in tests
Layer 4: Debug log → captures directory before git init
```

Result: 1847 tests passed, bug structurally impossible.

## Key Principle

Don't just fix where the error appeared. Add checks at every layer to make the bug impossible to recur through any code path.

## Related Skills

- **systematic-debugging** - Find root cause first, then add defense
- **root-cause-tracing** - Trace to find all layers involved
