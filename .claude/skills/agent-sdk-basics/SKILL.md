---
name: Claude Agent SDK Basics
description: When writing Python scripts that call Claude locally, or when you want to use your Claude subscription instead of API credits
when_to_use: |
  - Writing Python scripts that call Claude locally
  - Building business process automation
  - Want to use Claude subscription instead of API credits
  - Symptoms: Using anthropic.Anthropic() in local scripts, paying API fees
  - Keywords: agent sdk, python sdk, local scripts, automation, anthropic api
version: 2.0.0
languages: python
---

# Claude Agent SDK Basics

## Overview

When writing scripts that run on your local machine, use the **Claude Agent SDK** instead of the Anthropic API. The Agent SDK uses your Claude Code subscription (no API charges), provides better tool integration, and maintains conversation context.

**Core principle:** Local scripts should use Agent SDK. Production/server deployments should use Anthropic API.

## Quick Start

```bash
pip install claude-agent-sdk
```

**Most common pattern** - One-off automation:

```python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions

async def main():
    options = ClaudeAgentOptions(
        cwd="/path/to/project",
        permission_mode='acceptEdits'  # Auto-approve file operations
    )

    async for message in query(prompt="Analyze data.csv", options=options):
        if message.get('type') == 'text':
            print(message.get('content', ''))

asyncio.run(main())
```

## When to Use Agent SDK vs Anthropic API

### Use Agent SDK When:
- ✅ Script runs on your local machine
- ✅ You have Claude Code subscription
- ✅ Need file system access or command execution
- ✅ Want conversation context maintained
- ✅ Building business process automation

### Use Anthropic API When:
- ✅ Deploying to production servers
- ✅ Building web services for end users
- ✅ Need guaranteed SLA/uptime
- ✅ Require specific model versions

## Progressive References

This skill uses progressive disclosure to keep context small. Start here, then read references as needed.

### For Installation and Setup
**Read:** `references/installation.md`

Covers: Installation, authentication, verification, troubleshooting setup issues

### For Common Patterns
**Read:** `references/patterns.md`

Covers:
- `query()` vs `ClaudeSDKClient` (when to use which)
- Simple automation scripts
- Iterative processing with context
- Business process integration
- Configuration options and permission modes
- Directory structure and templates

### For Streaming and Messages
**Read:** `references/streaming.md`

Covers:
- Message types (text, tool_use, tool_result)
- Collecting responses
- Progress logging
- Real-time streaming
- Understanding async iteration

### For Error Handling
**Read:** `references/errors.md`

Covers:
- Retry patterns and error recovery
- Common issues and solutions
- Debugging strategies
- Checkpoint/resume patterns
- When to use Agent SDK vs API

## Key Concepts

### Two Modes

**`query()` - One-off tasks:**
- New session each time
- No conversation history
- Good for: Independent automation tasks

**`ClaudeSDKClient` - Continuous conversations:**
- Maintains context across multiple exchanges
- Good for: Interactive sessions, context building

### Permission Modes

**`acceptEdits` (recommended for automation):**
- Auto-approves: Read, Write, Edit, Grep, Glob
- Still asks for: Bash commands, Web operations

**`acceptAll` (use with caution):**
- Auto-approves everything
- Only for trusted, sandboxed environments

**`ask` (default):**
- User approves each tool
- Not suitable for automated scripts

## Related Skills

- **prompt-isolation**: Keep prompts in separate files
- **directory-structure**: Where to put scripts
- **sequential-processing**: Logging and resumability patterns
- **parallel-processing**: Worker scripts with Agent SDK

## Evidence

This skill was restructured using progressive disclosure based on proven patterns:

**Pattern #12** (0.90 confidence): "Progressive disclosure reduces context by 70%+"
- Original SKILL.md: 537 lines
- New SKILL.md: ~100 lines (81% reduction)
- Detailed content moved to 4 reference files
- Each reference focuses on specific use case

**Experiment #21**: "Three-tier progressive disclosure reduces token usage"
- Entry point provides overview and navigation
- Reference files contain detailed implementation
- Users only load what they need for current task

## Version History

- 2.0.0: Restructured with progressive disclosure pattern
- 1.0.0: Initial skill covering Agent SDK basics for local scripts
