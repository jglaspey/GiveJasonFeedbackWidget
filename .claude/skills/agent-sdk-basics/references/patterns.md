# ABOUTME: Common usage patterns for Claude Agent SDK in business processes
# ABOUTME: Includes query() vs ClaudeSDKClient, automation patterns, and integration examples

# Common Usage Patterns

## The Two Modes: query() vs ClaudeSDKClient

### Mode 1: query() - One-Off Tasks

**Best for:** Independent tasks, no context needed between runs

```python
import asyncio
from claude_agent_sdk import query

async def main():
    async for message in query(prompt="Analyze this log file and summarize errors"):
        print(message)

asyncio.run(main())
```

**Characteristics:**
- New session each time
- No conversation history
- Simple and clean
- Good for automation scripts

### Mode 2: ClaudeSDKClient - Continuous Conversations

**Best for:** Interactive sessions, context building, follow-up questions

```python
import asyncio
from claude_agent_sdk import ClaudeSDKClient

async def main():
    async with ClaudeSDKClient() as client:
        # First question
        async for msg in client.send("Read config.json"):
            print(msg)

        # Follow-up that references previous response
        async for msg in client.send("What's wrong with those settings?"):
            print(msg)

asyncio.run(main())
```

**Characteristics:**
- Maintains conversation context
- Multiple exchanges in same session
- Can interrupt/control flow
- Can use hooks and custom tools

## Pattern 1: Simple Automation Script

**Use case:** Run a one-time task, get result, exit

```python
# ABOUTME: Simple automation script using Agent SDK for one-off task
# ABOUTME: Processes data file and generates summary report

import asyncio
from pathlib import Path
from claude_agent_sdk import query, ClaudeAgentOptions

async def process_data_file(data_path: Path):
    """Process a data file and generate summary."""

    options = ClaudeAgentOptions(
        cwd=str(data_path.parent),  # Set working directory
        permission_mode='acceptEdits'  # Auto-approve file edits
    )

    prompt = f"Analyze {data_path.name} and create a summary report"

    async for message in query(prompt=prompt, options=options):
        # Process messages (text, tool calls, etc.)
        if message.get('type') == 'text':
            print(message.get('content', ''))

async def main():
    data_file = Path('./data/input.csv')
    await process_data_file(data_file)

if __name__ == '__main__':
    asyncio.run(main())
```

## Pattern 2: Iterative Processing with Context

**Use case:** Process multiple items, building context as you go

```python
# ABOUTME: Iterative processor using Agent SDK to maintain context across items
# ABOUTME: Processes list of files with Claude remembering previous analyses

import asyncio
from pathlib import Path
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions

async def process_files_with_context(file_paths: list[Path]):
    """Process multiple files, maintaining context between them."""

    options = ClaudeAgentOptions(
        permission_mode='acceptEdits',
        cwd=str(file_paths[0].parent)
    )

    async with ClaudeSDKClient(options=options) as client:
        # First file establishes baseline
        first_prompt = f"Analyze {file_paths[0].name} and note any patterns"
        async for msg in client.send(first_prompt):
            if msg.get('type') == 'text':
                print(f"File 1: {msg.get('content', '')}")

        # Subsequent files can reference previous analyses
        for file_path in file_paths[1:]:
            prompt = f"Compare {file_path.name} to the previous files. What's different?"
            async for msg in client.send(prompt):
                if msg.get('type') == 'text':
                    print(f"{file_path.name}: {msg.get('content', '')}")

async def main():
    files = [
        Path('./logs/day1.log'),
        Path('./logs/day2.log'),
        Path('./logs/day3.log'),
    ]
    await process_files_with_context(files)

if __name__ == '__main__':
    asyncio.run(main())
```

## Pattern 3: Business Process with Prompts in Files

**Use case:** Long-running process with isolated prompts for easy refinement

```python
# ABOUTME: Business process script loading prompts from separate files
# ABOUTME: Follows prompt-isolation pattern for easy iteration

import asyncio
from pathlib import Path
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions

def load_prompt(prompt_name: str) -> str:
    """Load prompt from functional/prompts/ directory."""
    prompt_path = Path(__file__).parent / 'functional' / 'prompts' / f'{prompt_name}.txt'
    return prompt_path.read_text()

async def run_business_process(input_data: dict):
    """Run business process with isolated prompts."""

    # Set up working directory
    project_root = Path(__file__).parent

    options = ClaudeAgentOptions(
        cwd=str(project_root),
        permission_mode='acceptEdits',
        system_prompt=load_prompt('system')  # Load system prompt from file
    )

    async with ClaudeSDKClient(options=options) as client:
        # Step 1: Extract data
        extract_prompt = load_prompt('extract_data').format(**input_data)
        async for msg in client.send(extract_prompt):
            pass  # Process extraction

        # Step 2: Validate
        validate_prompt = load_prompt('validate')
        async for msg in client.send(validate_prompt):
            pass  # Process validation

        # Step 3: Generate output
        output_prompt = load_prompt('generate_output')
        async for msg in client.send(output_prompt):
            if msg.get('type') == 'text':
                print(msg.get('content', ''))

async def main():
    await run_business_process({
        'source_file': 'input.csv',
        'output_dir': 'outputs/run_2025-01-15_143022'
    })

if __name__ == '__main__':
    asyncio.run(main())
```

## Configuration Options

### ClaudeAgentOptions

Common configuration options:

```python
from claude_agent_sdk import ClaudeAgentOptions

options = ClaudeAgentOptions(
    # Working directory for file operations
    cwd="/path/to/project",

    # Permission mode
    # 'ask' - Ask user for each tool (default)
    # 'acceptEdits' - Auto-approve file edits
    # 'acceptAll' - Auto-approve everything (dangerous!)
    permission_mode='acceptEdits',

    # System prompt override
    system_prompt="You are an expert data analyst",

    # Model selection
    model='claude-sonnet-4',

    # Max conversation turns (prevents infinite loops)
    max_turns=10,

    # Custom settings file path
    settings_path=".claude/settings.json"
)
```

### Permission Modes Explained

**`ask` (default):**
- User approves each tool use
- Good for: Interactive development
- Not good for: Automated scripts

**`acceptEdits`:**
- Auto-approves: Read, Write, Edit, Grep, Glob
- Still asks for: Bash commands, Web operations
- Good for: Most automation scripts
- Safety: Moderate

**`acceptAll`:**
- Auto-approves everything
- Good for: Trusted, sandboxed environments
- Safety: Low - only use in isolated environments

## Integration with Business Process Structure

### Directory Layout

```
business_process/
├── functional/
│   ├── scripts/
│   │   └── process.py          # Uses Agent SDK
│   ├── prompts/
│   │   ├── system.txt
│   │   ├── extract_data.txt
│   │   └── validate.txt
│   └── workers/
│       └── worker.py           # Uses Agent SDK
├── outputs/
│   └── run_YYYY-MM-DD_HHMMSS/
│       ├── logs/
│       └── results/
└── .claude/
    ├── CLAUDE.md
    └── settings.json
```

### Script Template

```python
#!/usr/bin/env python3
# ABOUTME: Business process script using Agent SDK
# ABOUTME: Follows directory-structure and prompt-isolation patterns

import asyncio
import sys
from pathlib import Path
from datetime import datetime
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

def setup_run_directory() -> Path:
    """Create timestamped run directory."""
    timestamp = datetime.now().strftime('%Y-%m-%d_%H%M%S')
    run_dir = PROJECT_ROOT / 'outputs' / f'run_{timestamp}'
    (run_dir / 'logs').mkdir(parents=True, exist_ok=True)
    (run_dir / 'results').mkdir(parents=True, exist_ok=True)
    (run_dir / 'errors').mkdir(parents=True, exist_ok=True)
    return run_dir

def load_prompt(name: str) -> str:
    """Load prompt from functional/prompts/."""
    path = PROJECT_ROOT / 'functional' / 'prompts' / f'{name}.txt'
    return path.read_text()

async def main():
    """Run business process."""
    run_dir = setup_run_directory()

    options = ClaudeAgentOptions(
        cwd=str(PROJECT_ROOT),
        permission_mode='acceptEdits',
        system_prompt=load_prompt('system')
    )

    async with ClaudeSDKClient(options=options) as client:
        # Your process logic here
        prompt = load_prompt('main').format(
            run_dir=str(run_dir)
        )

        async for message in client.send(prompt):
            if message.get('type') == 'text':
                print(message.get('content', ''))

if __name__ == '__main__':
    asyncio.run(main())
```

## Quick Reference

| Task | Method | Mode |
|------|--------|------|
| One-off automation | `query()` | Simple |
| Interactive session | `ClaudeSDKClient` | Advanced |
| File operations | Either, set `cwd` | Both |
| Conversation context | `ClaudeSDKClient` | Advanced |
| Custom tools | `ClaudeSDKClient` | Advanced |
| Simple script | `query()` | Simple |
