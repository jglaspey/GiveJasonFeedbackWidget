# ABOUTME: Understanding streaming responses and message types in Claude Agent SDK
# ABOUTME: Covers message structure, processing patterns, and collecting responses

# Streaming Responses

## Message Types

Messages yielded from `query()` or `client.send()` have these types:

```python
{
    'type': 'text',
    'content': 'Claude\'s text response'
}

{
    'type': 'tool_use',
    'name': 'Read',
    'input': {'file_path': '/path/to/file'}
}

{
    'type': 'tool_result',
    'tool_use_id': '...',
    'content': '...'
}
```

## Pattern: Collecting Final Response

```python
async def get_final_response(prompt: str) -> str:
    """Get Claude's final text response."""
    responses = []

    async for message in query(prompt=prompt):
        if message.get('type') == 'text':
            responses.append(message.get('content', ''))

    return '\n'.join(responses)
```

## Pattern: Processing Different Message Types

```python
async def process_with_details(prompt: str):
    """Process and log different message types."""

    text_responses = []
    tools_used = []

    async for message in query(prompt=prompt):
        msg_type = message.get('type')

        if msg_type == 'text':
            content = message.get('content', '')
            text_responses.append(content)
            print(f"Response: {content}")

        elif msg_type == 'tool_use':
            tool_name = message.get('name')
            tool_input = message.get('input', {})
            tools_used.append(tool_name)
            print(f"Using tool: {tool_name}")

        elif msg_type == 'tool_result':
            print(f"Tool completed")

    return {
        'response': '\n'.join(text_responses),
        'tools_used': tools_used
    }
```

## Pattern: Progress Logging

```python
# ABOUTME: Agent SDK script with progress logging for resumability
# ABOUTME: Logs each step for debugging and resume capability

import asyncio
import json
from pathlib import Path
from datetime import datetime
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions

class ProcessLogger:
    """Log progress for resumability."""

    def __init__(self, log_path: Path):
        self.log_path = log_path
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def log(self, step: str, data: dict):
        """Append log entry."""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'step': step,
            'data': data
        }
        with self.log_path.open('a') as f:
            f.write(json.dumps(entry) + '\n')

async def process_with_logging(items: list[str], log_path: Path):
    """Process items with progress logging."""
    logger = ProcessLogger(log_path)

    options = ClaudeAgentOptions(permission_mode='acceptEdits')

    async with ClaudeSDKClient(options=options) as client:
        for item in items:
            logger.log('processing', {'item': item})

            async for msg in client.send(f"Process {item}"):
                if msg.get('type') == 'text':
                    result = msg.get('content', '')
                    logger.log('completed', {'item': item, 'result': result})

async def main():
    items = ['item1', 'item2', 'item3']
    log_path = Path('./outputs/run_2025-01-15/progress.jsonl')
    await process_with_logging(items, log_path)

if __name__ == '__main__':
    asyncio.run(main())
```

## Pattern: Real-time Streaming Output

```python
async def stream_with_feedback(prompt: str):
    """Stream responses with real-time feedback."""

    async for message in query(prompt=prompt):
        msg_type = message.get('type')

        if msg_type == 'text':
            # Print text as it arrives
            content = message.get('content', '')
            print(content, end='', flush=True)

        elif msg_type == 'tool_use':
            # Show what Claude is doing
            tool_name = message.get('name')
            print(f"\n[Using {tool_name}...]", flush=True)
```

## Understanding Async Iteration

The SDK uses async generators. Key points:

1. **You must use `async for`** - not regular `for`
2. **Messages arrive in real-time** - as Claude produces them
3. **The loop blocks** until Claude finishes
4. **You can break early** if you only need partial results

Example of breaking early:

```python
async def get_first_response(prompt: str) -> str:
    """Get just the first text response."""
    async for message in query(prompt=prompt):
        if message.get('type') == 'text':
            return message.get('content', '')
    return ""
```
