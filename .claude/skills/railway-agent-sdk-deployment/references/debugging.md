# Debugging Journey: 29 Attempts

This documents every approach tried when deploying Claude Agent SDK to Railway, explaining what failed and why. Use this when standard solutions don't work.

## The Problem

Deploying a Slack bot using Claude Agent SDK in Docker on Railway, encountering persistent `spawn ENOENT` errors.

## Root Causes Discovered

After 29 attempts, we identified four distinct root causes:

### Root Cause 1: Invalid cwd (Attempts 1-18)
- **Symptom:** `spawn ENOENT` even when executable exists
- **Actual cause:** Node's `spawn()` throws misleading ENOENT when `cwd` doesn't exist
- **Solution:** Create directory before spawning

### Root Cause 2: Version Incompatibility (Attempts 23-25)
- **Symptom:** CLI exits with code 1, no visible error
- **Discovery:** stderr capture revealed `unknown option '--setting-sources'`
- **Actual cause:** SDK v0.1.30 requires CLI v1.0.117+
- **Solution:** Upgrade CLI to match SDK

### Root Cause 3: Root User Restrictions (Attempt 26)
- **Symptom:** `--dangerously-skip-permissions cannot be used with root/sudo`
- **Actual cause:** CLI security feature
- **Solution:** Run as non-root user

### Root Cause 4: Railway Bypassing ENTRYPOINT (Attempts 27-28)
- **Symptom:** Entrypoint never executes
- **Actual cause:** `startCommand` in railway.toml overrides Docker ENTRYPOINT
- **Solution:** Remove startCommand

---

## Failed Attempts (What NOT to Do)

### Attempts 1-3: PATH Fixes
Tried various PATH configurations thinking node wasn't in PATH.

```dockerfile
ENV PATH="/usr/local/bin:$PATH"
```

**Why it failed:** The ENOENT wasn't about finding node - it was about invalid cwd.

### Attempts 4-10: Wrapper Scripts
Created bash and node.js wrappers to call the CLI.

```bash
#!/bin/sh
exec /usr/local/bin/node /app/claude-code/cli.js "$@"
```

**Why it failed:** Still hit the cwd issue. Also discovered files in `/usr/local/bin` don't persist to Railway runtime.

### Attempts 11-16: Various Path Configurations
- Set NODE env var
- Removed `pathToClaudeCodeExecutable`
- Installed SDK globally
- Used different path formats

**Why it failed:** All addressing the wrong problem (path resolution instead of cwd existence).

---

## Breakthrough Attempts

### Attempt 17: `executable: 'node'` with `require.resolve()`
```typescript
const options = {
  executable: 'node',
  pathToClaudeCodeExecutable: require.resolve('@anthropic-ai/claude-code/cli.js'),
};
```

**Result:** Error changed from `spawn ENOENT` to `exit code 1`. Process now spawns!

### Attempt 18: Create cwd Directory First
```typescript
fs.mkdirSync(sessionsDir, { recursive: true });
const options = { cwd: sessionsDir };
```

**Result:** Spawn issues completely resolved. New error: authentication.

### Attempt 23: stderr Capture
```typescript
const options = {
  stderr: (data) => console.error('[claude-cli]', data),
};
```

**Result:** Finally saw the hidden error: `unknown option '--setting-sources'`

### Attempt 25: Version Alignment
Upgraded CLI from 1.0.67 to 1.0.117.

**Result:** New error: `cannot use bypassPermissions with root`. Progress!

### Attempt 26: Non-Root User
```dockerfile
RUN useradd -m -u 1001 appuser
```

**Result:** CLI spawns successfully! New error: `SqliteError: readonly database`

### Attempt 28: Remove startCommand
```toml
[deploy]
# startCommand = "npm start"  # REMOVED
```

**Result:** ENTRYPOINT now runs, permissions fixed, everything works!

### Attempt 29: Session Persistence
```typescript
env: {
  CLAUDE_SESSION_DIR: sessionsDir,  // Explicit in child env
}
```

**Result:** Sessions persist across redeployments. Fully operational!

---

## Debugging Techniques That Worked

### 1. stderr/stdout Capture
Essential for seeing CLI errors that would otherwise be invisible.

```typescript
const options = {
  stderr: (data) => console.error('[claude-cli stderr]', data),
  stdout: (data) => console.log('[claude-cli stdout]', data),
};
```

### 2. Entrypoint Logging
```bash
#!/bin/sh
echo "[Entrypoint] Running as: $(id)"
echo "[Entrypoint] /data contents: $(ls -la /data 2>&1 || echo 'not mounted')"
```

### 3. Build-time Verification
```dockerfile
RUN ls -la /app/
RUN cat /app/claude
RUN which node
```

### 4. Error Classification
Track which type of error you're seeing:
- `spawn ENOENT` → cwd or executable path issue
- `exit code 1` → CLI error (need stderr capture)
- `permission denied` → user/file ownership issue

---

## Lessons Learned

1. **Node spawn ENOENT is misleading** - check cwd exists before assuming executable is missing
2. **Always capture stderr** - CLI errors are often invisible without it
3. **Version mismatches are silent killers** - SDK and CLI must be compatible
4. **Platform configs can override Docker** - Railway's startCommand bypasses ENTRYPOINT
5. **Security features aren't bugs** - CLI won't run dangerous modes as root for good reason
6. **Environment variables don't inherit automatically** - explicitly pass to child processes
