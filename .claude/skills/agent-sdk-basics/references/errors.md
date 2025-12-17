# ABOUTME: Error handling and troubleshooting for Claude Agent SDK
# ABOUTME: Common issues, retry patterns, and debugging strategies

# Error Handling and Troubleshooting

## Pattern: Error Handling and Retry

```python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions

async def process_with_retry(prompt: str, max_retries: int = 3):
    """Process with retry logic."""

    for attempt in range(max_retries):
        try:
            responses = []
            async for message in query(prompt=prompt):
                if message.get('type') == 'text':
                    responses.append(message.get('content', ''))

            return '\n'.join(responses)

        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(2 ** attempt)  # Exponential backoff
```

## Common Issues and Solutions

### Problem: "Authentication failed"

**Solution:** Ensure you're logged in to Claude Code:
```bash
claude auth login
```

### Problem: "Module not found: claude_agent_sdk"

**Solution:** Install the SDK:
```bash
pip install claude-agent-sdk
```

### Problem: Script hangs or doesn't progress

**Possible causes:**
1. Permission mode is 'ask' (waiting for user input)
   - Use `permission_mode='acceptEdits'` for automation
2. Infinite loop
   - Set `max_turns=10` in options
3. Waiting for async operation
   - Ensure you're using `asyncio.run()` correctly

**Example fix:**
```python
options = ClaudeAgentOptions(
    permission_mode='acceptEdits',  # Don't wait for user input
    max_turns=10  # Prevent infinite loops
)
```

### Problem: Can't read/write files

**Check:**
1. `cwd` is set correctly in options
2. Paths are relative to `cwd` or absolute
3. Permission mode allows file operations
4. Files/directories exist

**Example:**
```python
from pathlib import Path

project_root = Path(__file__).parent
options = ClaudeAgentOptions(
    cwd=str(project_root),  # Set working directory
    permission_mode='acceptEdits'  # Allow file operations
)
```

### Problem: Context too long or running out of memory

**Solutions:**
1. Use `query()` instead of `ClaudeSDKClient` for independent tasks
2. Set `max_turns` to limit conversation length
3. Break work into smaller chunks
4. Clear context by creating new client sessions

```python
# Instead of one long session
async with ClaudeSDKClient() as client:
    for item in many_items:  # This builds up context
        await client.send(f"Process {item}")

# Use separate sessions
for item in many_items:
    async for msg in query(f"Process {item}"):  # Each has clean context
        pass
```

### Problem: Unexpected tool execution

**Cause:** Permission mode set too permissive

**Solution:** Use appropriate permission mode:
```python
# For scripts that should only read/write files
options = ClaudeAgentOptions(
    permission_mode='acceptEdits'  # Won't run bash commands without asking
)

# For fully automated scripts in safe environments
options = ClaudeAgentOptions(
    permission_mode='acceptAll'  # Use with caution
)
```

## Debugging Strategies

### 1. Log all messages

```python
async def debug_query(prompt: str):
    """Log all message types for debugging."""
    async for message in query(prompt=prompt):
        print(f"Message type: {message.get('type')}")
        print(f"Full message: {message}")
        print("---")
```

### 2. Catch and log exceptions

```python
import traceback

async def safe_process(prompt: str):
    """Process with full error logging."""
    try:
        async for message in query(prompt=prompt):
            if message.get('type') == 'text':
                print(message.get('content', ''))
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()
        raise
```

### 3. Test with minimal example

```python
# Minimal test to isolate issues
async def minimal_test():
    """Simplest possible test."""
    async for msg in query(prompt="Say hello"):
        print(msg)

asyncio.run(minimal_test())
```

### 4. Check Python version and environment

```bash
# Ensure Python 3.8+
python --version

# Check installed packages
pip list | grep claude

# Verify you're in the right virtual environment
which python
```

## Error Recovery Patterns

### Pattern: Graceful degradation

```python
async def process_with_fallback(prompt: str, fallback_action):
    """Try processing, fall back if it fails."""
    try:
        result = []
        async for msg in query(prompt=prompt):
            if msg.get('type') == 'text':
                result.append(msg.get('content', ''))
        return '\n'.join(result)
    except Exception as e:
        print(f"Processing failed: {e}")
        print("Running fallback action...")
        return fallback_action()
```

### Pattern: Checkpoint and resume

```python
import json
from pathlib import Path

async def process_with_checkpoints(items: list, checkpoint_path: Path):
    """Process items with checkpoint/resume capability."""

    # Load checkpoint if exists
    completed = set()
    if checkpoint_path.exists():
        with checkpoint_path.open() as f:
            completed = set(json.load(f))

    for item in items:
        if item in completed:
            print(f"Skipping {item} (already completed)")
            continue

        try:
            async for msg in query(f"Process {item}"):
                pass

            # Mark completed
            completed.add(item)
            with checkpoint_path.open('w') as f:
                json.dump(list(completed), f)

        except Exception as e:
            print(f"Failed on {item}: {e}")
            print(f"Resume from checkpoint by re-running")
            raise
```

## When to Use Agent SDK vs Anthropic API

If you're hitting issues, consider whether Agent SDK is the right choice:

### Use Agent SDK When:
- Script runs on your local machine
- You have Claude Code subscription
- Need file system access or command execution
- Want conversation context maintained
- Building business process automation
- Prototyping and development

### Use Anthropic API When:
- Deploying to production servers
- Need simple stateless requests
- Building web services for end users
- Need guaranteed SLA/uptime
- Require specific model versions
- Agent SDK authentication is problematic in your environment
