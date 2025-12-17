# Dockerfile Patterns for Agent SDK

## Complete Working Dockerfile

```dockerfile
FROM node:20-slim

# Create non-root user (required - CLI refuses bypassPermissions as root)
RUN useradd -m -u 1001 appuser

# Install app dependencies
WORKDIR /app
COPY package*.json ./
RUN npm ci

# Build application
COPY . .
RUN npm run build

# Prune dev dependencies
RUN npm prune --production

# Give ownership to appuser
RUN chown -R appuser:appuser /app

# Install gosu for secure user switching
RUN apt-get update && apt-get install -y gosu && rm -rf /var/lib/apt/lists/*

# Entrypoint: fix volume permissions as root, then switch to appuser
ENTRYPOINT ["/bin/sh", "-c", "if [ -d /data ]; then chown -R appuser:appuser /data; fi && exec gosu appuser /usr/local/bin/node dist/index.js"]
```

## Why Non-Root User is Required

The Claude Code CLI has a security feature that prevents `bypassPermissions` mode when running as root:

```
--dangerously-skip-permissions cannot be used with root/sudo privileges for security reasons
```

This is intentional - root with bypassed permissions would be too dangerous.

## User Switching Pattern

The tricky part: Railway volumes mount as root-owned, but you need a non-root user for the CLI. Solution: start as root, fix permissions, then switch users.

### Using gosu (Recommended)

```dockerfile
# Install gosu
RUN apt-get update && apt-get install -y gosu && rm -rf /var/lib/apt/lists/*

# Entrypoint fixes permissions then switches
ENTRYPOINT ["/bin/sh", "-c", "chown -R appuser:appuser /data && exec gosu appuser node dist/index.js"]
```

### Why gosu Over su/sudo

- `gosu` properly drops privileges (no lingering root capabilities)
- Works correctly with `exec` for signal handling
- Simpler than `su -c` syntax
- No TTY requirement like sudo

## Volume Permission Handling

```dockerfile
# The volume directory might not exist at build time
# Handle it gracefully in the entrypoint
ENTRYPOINT ["/bin/sh", "-c", "if [ -d /data ]; then chown -R appuser:appuser /data; fi && exec gosu appuser node dist/index.js"]
```

## Alternative: Dedicated Entrypoint Script

For more complex logic, use a separate script:

```dockerfile
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
```

```bash
#!/bin/sh
# docker-entrypoint.sh

echo "[Entrypoint] Running as: $(id)"

if [ -d /data ]; then
    echo "[Entrypoint] Fixing /data permissions..."
    chown -R appuser:appuser /data
fi

echo "[Entrypoint] Switching to appuser..."
exec gosu appuser /usr/local/bin/node dist/index.js
```

## Common Mistakes

### Mistake 1: Using USER directive alone
```dockerfile
# WRONG - volume will still be root-owned
USER appuser
CMD ["node", "dist/index.js"]
```

### Mistake 2: Forgetting exec
```dockerfile
# WRONG - node runs as child, signals won't propagate
ENTRYPOINT ["/bin/sh", "-c", "gosu appuser node dist/index.js"]

# RIGHT - exec replaces shell
ENTRYPOINT ["/bin/sh", "-c", "exec gosu appuser node dist/index.js"]
```

### Mistake 3: Not including CLI in runtime dependencies
```dockerfile
# If you use npm prune --production, ensure @anthropic-ai/claude-code is in dependencies, not devDependencies
```
