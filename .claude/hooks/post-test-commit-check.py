#!/usr/bin/env python3
# ABOUTME: PostToolUse hook that prompts commits after test commands succeed
# ABOUTME: Enforces "commit after tests pass" discipline from git-operations skill

import json
import re
import subprocess
import sys

# Test command patterns to detect
TEST_COMMANDS = [
    r'\bpytest\b',
    r'\bpython\s+-m\s+pytest\b',
    r'\bnpm\s+test\b',
    r'\bnpm\s+run\s+test\b',
    r'\byarn\s+test\b',
    r'\bcargo\s+test\b',
    r'\bgo\s+test\b',
    r'\bruby\s+-I\s+test\b',
    r'\bruby\s+.*_test\.rb\b',
    r'\bphpunit\b',
    r'\bmvn\s+test\b',
    r'\bgradle\s+test\b',
]


def is_test_command(command: str) -> bool:
    """Check if command is a test invocation."""
    for pattern in TEST_COMMANDS:
        if re.search(pattern, command, re.IGNORECASE):
            return True
    return False


def tests_passed(tool_response: dict) -> bool:
    """Check if the test command succeeded (exit code 0)."""
    # Bash tool response includes exit code or success indicator
    # Check various possible response formats
    if 'exit_code' in tool_response:
        return tool_response['exit_code'] == 0
    if 'success' in tool_response:
        return tool_response['success'] is True
    # If we can't determine, assume it passed (let other checks catch issues)
    return True


def has_uncommitted_changes() -> bool:
    """Check if there are uncommitted changes in git."""
    try:
        # git diff-index returns non-zero if there are changes
        result = subprocess.run(
            ['git', 'diff-index', '--quiet', 'HEAD', '--'],
            cwd='.',
            capture_output=True,
            timeout=5
        )
        # Exit code 1 means there are changes
        return result.returncode != 0
    except subprocess.TimeoutExpired:
        # If git is slow, assume no changes (don't block)
        return False
    except Exception:
        # If git command fails, don't block
        return False


def get_recent_changes_summary() -> str:
    """Get a brief summary of what changed."""
    try:
        result = subprocess.run(
            ['git', 'status', '--short'],
            cwd='.',
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            # Limit to first 5 files
            if len(lines) > 5:
                return '\n'.join(lines[:5]) + f'\n... and {len(lines) - 5} more files'
            return '\n'.join(lines)
    except Exception:
        pass
    return 'Multiple files changed'


def main():
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f'Error: Invalid JSON input: {e}', file=sys.stderr)
        sys.exit(1)

    tool_name = input_data.get('tool_name', '')
    tool_input = input_data.get('tool_input', {})
    tool_response = input_data.get('tool_response', {})

    # Only check Bash commands
    if tool_name != 'Bash':
        sys.exit(0)

    command = tool_input.get('command', '')

    # Check if this was a test command
    if not is_test_command(command):
        sys.exit(0)

    # Check if tests passed
    if not tests_passed(tool_response):
        # Tests failed, don't prompt commit
        sys.exit(0)

    # Tests passed - check for uncommitted changes
    if not has_uncommitted_changes():
        # No uncommitted changes, nothing to commit
        sys.exit(0)

    # Tests passed AND uncommitted changes exist
    # Block and prompt commit
    changes = get_recent_changes_summary()

    message = f'''
🧪 Tests passed successfully!

You have uncommitted changes:
{changes}

According to git-operations best practices, you should commit your work after tests pass.

Please launch a git-operations subagent to create an atomic commit of this work, or explain why these changes should not be committed yet.
'''.strip()

    print(message, file=sys.stderr)
    sys.exit(2)  # Exit code 2 blocks continuation and shows message to Claude


if __name__ == '__main__':
    main()
