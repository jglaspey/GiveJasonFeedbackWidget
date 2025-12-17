# Railway-Specific Configuration

## Working railway.toml

```toml
[build]
builder = "dockerfile"

[deploy]
# CRITICAL: Do NOT set startCommand - it bypasses Docker ENTRYPOINT!
# startCommand = "npm start"  # <- This breaks everything!
healthcheckPath = "/health"

[[volumes]]
mountPath = "/data"
```

## The startCommand Trap

**This is the most surprising gotcha.** When you set `startCommand` in railway.toml, Railway completely ignores your Docker ENTRYPOINT and CMD. Your carefully crafted entrypoint script that fixes permissions? Never runs.

```toml
# WRONG - bypasses Docker ENTRYPOINT entirely
[deploy]
startCommand = "npm start"

# RIGHT - let Docker handle startup
[deploy]
# (no startCommand)
```

### Symptoms of startCommand Override

- Entrypoint debug messages never appear in logs
- Permission errors persist despite entrypoint fix
- Container runs as unexpected user

## Volume Setup

Railway volumes mount as root-owned. Your entrypoint must fix permissions before switching to non-root user.

```toml
[[volumes]]
mountPath = "/data"
```

Access the mount path in code:
```typescript
const mount = process.env.RAILWAY_VOLUME_MOUNT_PATH || '/data';
```

## Environment Variables

Set these in Railway dashboard or railway.toml:

```toml
[variables]
ANTHROPIC_API_KEY = "sk-ant-..."
NODE_ENV = "production"
```

Or use Railway's secrets management for `ANTHROPIC_API_KEY`.

## Health Checks

Railway needs a health endpoint to know your service is ready:

```toml
[deploy]
healthcheckPath = "/health"
```

Your app should expose this:
```typescript
app.get('/health', (req, res) => res.send('OK'));
```

## Debugging Railway Deployments

### Check Build Logs
- Verify Dockerfile steps complete
- Confirm non-root user creation
- Check that `@anthropic-ai/claude-code` is in production dependencies

### Check Runtime Logs
- Look for entrypoint messages
- Verify user identity: should see `appuser`, not `root`
- Check for permission errors on `/data`

### Common Railway Issues

| Symptom | Likely Cause | Solution |
|---------|--------------|----------|
| Entrypoint never runs | `startCommand` in railway.toml | Remove startCommand |
| Permission denied on /data | Volume is root-owned | Fix in entrypoint before user switch |
| CLI errors about root | Running as root user | Ensure gosu switches to appuser |
| Sessions lost on redeploy | Wrong session directory | Use `CLAUDE_SESSION_DIR` pointing to volume |

## Railway vs Other Platforms

The key Railway-specific issues:
1. `startCommand` bypassing ENTRYPOINT (unique to Railway's config)
2. Volume ownership (common to most container platforms)
3. No persistent filesystem outside volumes (standard for containers)

If deploying to other platforms (Fly.io, Render, etc.), the Dockerfile patterns still apply, but the `startCommand` trap is Railway-specific.
