# SDK Configuration for Docker Deployment

## Package Dependencies

```json
{
  "dependencies": {
    "@anthropic-ai/claude-agent-sdk": "^0.1.30",
    "@anthropic-ai/claude-code": "^1.0.117"
  }
}
```

**Important:** Include `@anthropic-ai/claude-code` as a runtime dependency, not just globally installed. This ensures `require.resolve()` works after `npm prune --production`.

## Complete SDK Configuration

```typescript
import { createRequire } from 'node:module';
import fs from 'node:fs';
import path from 'path';
import os from 'os';

const require = createRequire(import.meta.url);

// Create sessions directory - MUST exist before spawning
function getSessionsDir(): string {
  const mount = process.env.RAILWAY_VOLUME_MOUNT_PATH;
  const sessionsPath = mount
    ? path.join(mount, '.claude_sessions')
    : '/data/.claude_sessions';
  fs.mkdirSync(sessionsPath, { recursive: true });
  return sessionsPath;
}

// Configure Claude settings for API key auth (non-interactive)
function ensureClaudeUserSettings(): void {
  const settingsPath = path.join(os.homedir(), '.claude/settings.json');
  fs.mkdirSync(path.dirname(settingsPath), { recursive: true });
  fs.writeFileSync(settingsPath, JSON.stringify({
    forceLoginMethod: 'console',
    hasCompletedOnboarding: true
  }));
}

// Call before SDK initialization
ensureClaudeUserSettings();

const sessionsDir = getSessionsDir();

// SDK options
const options = {
  // Use node directly to bypass shebang PATH issues
  executable: 'node',

  // Get absolute path to CLI JS file
  pathToClaudeCodeExecutable: require.resolve('@anthropic-ai/claude-code/cli.js'),

  // Working directory - must exist!
  cwd: sessionsDir,

  // Environment for child process
  env: {
    ...process.env,
    ANTHROPIC_API_KEY: process.env.ANTHROPIC_API_KEY,
    CLAUDE_SESSION_DIR: sessionsDir,  // CRITICAL for session persistence
  },

  // Capture stderr - essential for debugging
  stderr: (data: string) => console.error('[claude-cli stderr]', data),

  // Auto-approve permissions (requires non-root user)
  permissionMode: 'bypassPermissions',
};
```

## Why Each Option Matters

### `executable: 'node'`
The CLI has a shebang (`#!/usr/bin/env node`) that can't resolve in spawned processes. Using `executable: 'node'` runs the CLI JS file directly, bypassing shebang resolution.

### `require.resolve()`
Gets the absolute path to the CLI JS file from your `node_modules`. More reliable than hardcoded paths that might differ between build and runtime.

### `cwd` Must Exist
Node's `spawn()` throws a misleading `ENOENT` error when `cwd` doesn't exist, even if the executable is valid. Always create the directory first.

### `CLAUDE_SESSION_DIR` in env
The `cwd` option does NOT control where sessions are stored. The CLI looks for `CLAUDE_SESSION_DIR` environment variable. Must be explicitly passed in the `env` object - setting `process.env.CLAUDE_SESSION_DIR` in the parent process isn't enough.

### `stderr` Callback
Without this, CLI errors are invisible. The stderr capture revealed critical errors like `unknown option '--setting-sources'` that would have been impossible to debug otherwise.

## Authentication Flow

1. `ensureClaudeUserSettings()` writes `forceLoginMethod: 'console'` to force API key auth
2. `ANTHROPIC_API_KEY` is passed in the env object
3. CLI uses API key instead of OAuth flow (which requires browser)

## Session Persistence

Sessions are stored in `CLAUDE_SESSION_DIR`. For persistence across redeployments:

1. Mount a volume (e.g., `/data` on Railway)
2. Set `CLAUDE_SESSION_DIR` to a path on that volume
3. Explicitly pass `CLAUDE_SESSION_DIR` in the `env` object

```typescript
// Verification logging
console.log(`Sessions directory: ${sessionsDir}`);
console.log(`Contents: ${fs.readdirSync(sessionsDir)}`);
```
