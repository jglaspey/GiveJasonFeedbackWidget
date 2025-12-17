#!/usr/bin/env python3
# ABOUTME: Runs a test prompt against Claude in the tester_workspace and observes behavior
# ABOUTME: Uses Agent SDK to spawn Claude with skills and capture what happens

import asyncio
import argparse
import json
from pathlib import Path
from datetime import datetime

# Check if claude-agent-sdk is available
try:
    from claude_agent_sdk import (
        query, ClaudeAgentOptions,
        AssistantMessage, SystemMessage, UserMessage, ResultMessage,
        TextBlock, ToolUseBlock
    )
    AGENT_SDK_AVAILABLE = True
except ImportError:
    AGENT_SDK_AVAILABLE = False
    print("Warning: claude-agent-sdk not installed. Install with: pip install claude-agent-sdk")


async def run_test_prompt(prompt: str, workspace: Path, verbose: bool = False) -> dict:
    """Run a test prompt and capture skill invocation behavior."""

    if not AGENT_SDK_AVAILABLE:
        return {
            "error": "claude-agent-sdk not installed",
            "prompt": prompt
        }

    options = ClaudeAgentOptions(
        cwd=str(workspace),
        permission_mode='bypassPermissions',  # Full permissions for testing
        max_turns=10,  # Enough to invoke skill, read it, and respond
        add_dirs=[str(workspace)],  # Try adding workspace to skill discovery path
        setting_sources=['project', 'local']  # Load all settings including hooks
    )

    result = {
        "prompt": prompt,
        "timestamp": datetime.now().isoformat(),
        "skill_invoked": False,
        "skill_name": None,
        "tool_calls": [],
        "text_responses": [],
        "raw_messages": []
    }

    try:
        async for message in query(prompt=prompt, options=options):
            if verbose:
                print(f"[{type(message).__name__}] {message}")

            result["raw_messages"].append(str(message))

            # Handle AssistantMessage - contains content blocks
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        result["text_responses"].append(block.text)
                    elif isinstance(block, ToolUseBlock):
                        result["tool_calls"].append({
                            "name": block.name,
                            "input": block.input
                        })
                        # Check if it's a Skill tool call
                        if block.name == 'Skill':
                            result["skill_invoked"] = True
                            result["skill_name"] = block.input.get('skill', '')

            # Handle other message types for logging
            elif isinstance(message, SystemMessage):
                if verbose:
                    print(f"  System: {message.subtype}")
            elif isinstance(message, ResultMessage):
                if verbose:
                    print(f"  Result received")

    except Exception as e:
        result["error"] = str(e)
        import traceback
        if verbose:
            traceback.print_exc()

    return result


def main():
    parser = argparse.ArgumentParser(
        description="Run a test prompt against Claude in the tester workspace",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Test if mentioning skill name triggers invocation
  python run_experiment.py "Use the test-skill-detailed skill to analyze test.txt"

  # Test if keywords trigger invocation
  python run_experiment.py "Analyze test.txt for patterns"

  # Verbose mode to see all messages
  python run_experiment.py -v "Review the test file"

  # Save results to file
  python run_experiment.py "Analyze test.txt" > result.json
        """
    )

    parser.add_argument("prompt", help="The prompt to send to Claude")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Show all messages from Claude")
    parser.add_argument("--workspace", type=Path,
                        default=Path(__file__).parent / "tester_workspace",
                        help="Path to tester workspace")

    args = parser.parse_args()

    if not AGENT_SDK_AVAILABLE:
        print("Error: claude-agent-sdk is required")
        print("Install with: pip install claude-agent-sdk")
        return

    # Run the experiment
    result = asyncio.run(run_test_prompt(
        prompt=args.prompt,
        workspace=args.workspace,
        verbose=args.verbose
    ))

    # Output result
    print("\n" + "=" * 60)
    print("EXPERIMENT RESULT")
    print("=" * 60)
    print(f"Prompt: {result['prompt']}")
    print(f"Skill Invoked: {'YES' if result['skill_invoked'] else 'NO'}")
    if result['skill_name']:
        print(f"Skill Name: {result['skill_name']}")
    print(f"Tool Calls: {len(result['tool_calls'])}")
    for tc in result['tool_calls']:
        print(f"  - {tc['name']}")

    if result.get('error'):
        print(f"Error: {result['error']}")

    print("\n--- Recording command ---")
    actual = "invoked" if result['skill_invoked'] else "not_invoked"
    print(f"""
python record_experiment.py \\
    --feature skills_invocation \\
    --hypothesis "YOUR_HYPOTHESIS_HERE" \\
    --prompt "{result['prompt']}" \\
    --expected invoked|not_invoked|uncertain \\
    --actual {actual} \\
    --notes "Tool calls: {', '.join(tc['name'] for tc in result['tool_calls'])}"
""")


if __name__ == "__main__":
    main()
