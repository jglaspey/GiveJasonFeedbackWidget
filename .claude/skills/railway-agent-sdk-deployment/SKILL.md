---
name: Railway Agent SDK Deployment
description: When deploying Claude Agent SDK to Docker/Railway, debugging spawn ENOENT errors, or configuring session persistence in containers
when_to_use: |
  - Deploying Agent SDK to Railway or Docker
  - Debugging "spawn ENOENT" errors in containers
  - CLI exits with code 1, no visible errors
  - Session persistence issues after redeployment
  - Permission errors with bypassPermissions mode
  - Railway ignoring Docker ENTRYPOINT
  - Keywords: railway, docker, spawn enoent, container, deployment, session persistence
version: 1.0.0
languages: typescript, dockerfile
---

# Railway Agent SDK Deployment

## Overview

Deploying the Claude Agent SDK in Docker containers (especially Railway) has several non-obvious gotchas. This skill captures hard-won lessons from 29 debugging attempts.

## Quick Checklist

Before deploying, verify:

- [ ] CLI version matches SDK (currently 1.0.117+ for SDK 0.1.30)
- [ ] Using `executable: 'node'` with `require.resolve()` for CLI path
- [ ] `cwd` directory exists before spawning
- [ ] `forceLoginMethod: 'console'` in user settings
- [ ] Running as non-root user (CLI refuses bypassPermissions as root)
- [ ] Volume permissions fixed in entrypoint before user switch
- [ ] NO `startCommand` in railway.toml (bypasses Docker ENTRYPOINT)
- [ ] `CLAUDE_SESSION_DIR` explicitly passed in env object

## Critical Gotchas

### 1. spawn ENOENT Usually Means Bad cwd
Node's `spawn()` throws misleading `ENOENT` when `cwd` doesn't exist, even if executable is valid.

```typescript
// WRONG - directory might not exist
const options = { cwd: '/data/.claude_sessions' };

// RIGHT - create first
fs.mkdirSync('/data/.claude_sessions', { recursive: true });
const options = { cwd: '/data/.claude_sessions' };
```

### 2. Railway startCommand Bypasses ENTRYPOINT
```toml
# railway.toml - DON'T do this
[deploy]
startCommand = "npm start"  # Completely ignores Docker ENTRYPOINT!

# DO this instead
[deploy]
# Let Docker ENTRYPOINT handle startup
healthcheckPath = "/health"
```

### 3. Session Persistence Requires Explicit Env
```typescript
// WRONG - process.env alone isn't enough
process.env.CLAUDE_SESSION_DIR = sessionsDir;
const options = { env: process.env };  // Sessions lost on redeploy!

// RIGHT - explicitly include in child env
const options = {
  env: {
    ...process.env,
    CLAUDE_SESSION_DIR: sessionsDir,  // CRITICAL
  }
};
```

### 4. CLI Won't Run bypassPermissions as Root
```dockerfile
# Must create non-root user
RUN useradd -m -u 1001 appuser

# Fix volume permissions as root, then switch
ENTRYPOINT ["/bin/sh", "-c", "chown -R appuser:appuser /data && exec gosu appuser node dist/index.js"]
```

### 5. stderr Capture Reveals Hidden Errors
```typescript
const options = {
  stderr: (data) => console.error('[claude-cli]', data),  // Essential!
  // Without this, CLI errors are invisible
};
```

## Progressive References

**For SDK configuration patterns**: Read `references/sdk-config.md`
- Complete TypeScript configuration
- Authentication setup
- Session directory handling

**For Dockerfile patterns**: Read `references/dockerfile.md`
- Non-root user setup
- gosu for user switching
- Volume permission handling

**For Railway-specific issues**: Read `references/railway.md`
- railway.toml configuration
- Volume setup
- Common Railway gotchas

**For debugging journey**: Read `references/debugging.md`
- All 29 attempts documented
- What failed and why
- Root cause analysis

## Version Compatibility

| SDK Version | Required CLI Version |
|-------------|---------------------|
| 0.1.30      | 1.0.117+            |

Keep versions aligned - the SDK passes flags that older CLIs don't understand.

## Related Skills

- **agent-sdk-basics**: For local development with Agent SDK
- **path-management**: For machine-agnostic paths
