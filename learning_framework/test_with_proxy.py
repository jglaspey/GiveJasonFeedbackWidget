#!/usr/bin/env python3
# ABOUTME: Test script to run Agent SDK through claude-code-logger proxy
# ABOUTME: Helps debug what Claude actually sees including hook outputs

import asyncio
import argparse
import re
from pathlib import Path

from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, TextBlock, ToolUseBlock
from claude_agent_sdk.types import HookMatcher, PreToolUseHookInput, HookContext, SyncHookJSONOutput

# Define hook as Python function instead of shell script
# Signature per SDK docs: async def hook(input_data: dict, tool_use_id: str | None, context: HookContext) -> dict
async def enforce_file_skills_hook(
    input_data: dict,
    tool_use_id: str | None,
    context: HookContext
) -> dict:
    """PreToolUse hook that enforces skills based on file paths."""
    tool_name = input_data.get('tool_name', 'unknown')
    tool_input = input_data.get('tool_input', {})

    print(f"[DEBUG] Hook called! Tool: {tool_name}")
    print(f"[DEBUG] tool_input: {tool_input}")

    file_path = tool_input.get('file_path', '')
    if not file_path:
        print("[DEBUG] No file_path in tool_input, skipping")
        return {}  # No enforcement needed

    # Normalize path
    normalized = file_path.replace('\\', '/')

    # Check test file patterns
    test_patterns = [
        r'test_.*\.py$',
        r'.*_test\.py$',
        r'(^|/)tests?/.*\.py$',
        r'.*\.test\.(ts|js|tsx|jsx)$',
        r'.*\.spec\.(ts|js|tsx|jsx)$',
    ]

    if any(re.search(p, normalized) for p in test_patterns):
        message = """📚 FILE-BASED SKILL ENFORCEMENT (Python hook)
   File: {}
   Reason: editing a test file
   Required skill: testing-anti-patterns
   You MUST invoke the testing-anti-patterns skill before proceeding.""".format(
            normalized.split('/')[-1]
        )
        print(f"[HOOK OUTPUT] {message}")  # Print to see if it shows up
        return {"message": message}

    return {}


async def run_with_proxy(prompt: str, workspace: Path, proxy_url: str = "http://localhost:8000", use_python_hooks: bool = False):
    """Run a prompt through the Agent SDK with proxy for debugging."""

    # Base options
    options_dict = {
        'cwd': str(workspace),
        'permission_mode': 'bypassPermissions',
        'max_turns': 5,
        'add_dirs': [str(workspace)],
        # Use 'project' to load workspace's .claude/settings.json (including hooks)
        # Nested git repo in tester_workspace should make it the project root
        'setting_sources': ['project', 'local'],
        'disallowed_tools': ['Task'],
    }

    if proxy_url:
        options_dict['env'] = {'ANTHROPIC_BASE_URL': proxy_url}

    # Optionally use Python hooks instead of shell hooks
    if use_python_hooks:
        options_dict['hooks'] = {
            'PreToolUse': [
                HookMatcher(
                    matcher='Edit|Write',
                    hooks=[enforce_file_skills_hook]
                )
            ]
        }
        print("Using Python hooks (in-process)")
    else:
        print("Using shell hooks from settings.json (if loaded)")

    options = ClaudeAgentOptions(**options_dict)

    print(f"Running with proxy: {proxy_url}")
    print(f"Workspace: {workspace}")
    print(f"Prompt: {prompt}")
    print("=" * 60)

    try:
        async for message in query(prompt=prompt, options=options):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(f"[Text] {block.text[:200]}...")
                    elif isinstance(block, ToolUseBlock):
                        print(f"[Tool] {block.name}: {list(block.input.keys())}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

def main():
    parser = argparse.ArgumentParser(description="Run Agent SDK through proxy for debugging")
    parser.add_argument("prompt", help="Prompt to send")
    parser.add_argument("--proxy", default="http://localhost:8000", help="Proxy URL (use --no-proxy to disable)")
    parser.add_argument("--no-proxy", action="store_true", help="Don't use proxy")
    parser.add_argument("--python-hooks", action="store_true", help="Use Python hooks instead of shell hooks")
    parser.add_argument("--isolated", action="store_true",
                        help="Use isolated workspace at /tmp/claude_tester_workspace (outside parent git repo)")
    parser.add_argument("--workspace", type=Path,
                        default=Path(__file__).parent / "tester_workspace")
    args = parser.parse_args()

    # Use isolated workspace if requested
    workspace = Path("/tmp/claude_tester_workspace") if args.isolated else args.workspace

    proxy_url = None if args.no_proxy else args.proxy
    asyncio.run(run_with_proxy(args.prompt, workspace, proxy_url, args.python_hooks))

if __name__ == "__main__":
    main()
