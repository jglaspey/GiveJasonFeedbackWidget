# ABOUTME: Installation and setup instructions for Claude Agent SDK
# ABOUTME: Covers installation, authentication, and initial configuration

# Installation and Setup

## Installing the SDK

```bash
pip install claude-agent-sdk
```

**No API key needed** - Uses your Claude Code authentication.

## Authentication

The Agent SDK uses your Claude Code authentication automatically. If you encounter authentication issues:

```bash
claude auth login
```

This will open your browser and authenticate you with Claude Code.

## Verifying Installation

Test that the SDK is installed correctly:

```python
import asyncio
from claude_agent_sdk import query

async def test():
    async for message in query(prompt="Say hello"):
        if message.get('type') == 'text':
            print(message.get('content', ''))

asyncio.run(test())
```

If this runs without errors and prints a greeting, you're ready to go.

## Common Installation Issues

### Problem: "Module not found: claude_agent_sdk"

**Solution:** Install the SDK:
```bash
pip install claude-agent-sdk
```

Make sure you're using the correct Python environment if you're using virtual environments.

### Problem: "Authentication failed"

**Solution:** Ensure you're logged in to Claude Code:
```bash
claude auth login
```

### Problem: Import errors or version conflicts

**Solution:** Update to the latest version:
```bash
pip install --upgrade claude-agent-sdk
```
