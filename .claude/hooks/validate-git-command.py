#!/usr/bin/env python3
# ABOUTME: PreToolUse hook that blocks dangerous git commands and .env file modifications
# ABOUTME: Enforces git safety rules from git-operations skill

import json
import re
import sys

# Dangerous git commands that require explicit approval
DANGEROUS_GIT_COMMANDS = [
    (r'git\s+reset\s+--hard', 'git reset --hard permanently deletes uncommitted work. Get explicit user approval first.'),
    (r'git\s+reset\s+HEAD~', 'git reset HEAD~ removes commits. Get explicit user approval first.'),
    (r'git\s+clean\s+-[df]', 'git clean -fd permanently deletes untracked files. Get explicit user approval first.'),
    (r'git\s+push\s+.*--force(?!-with-lease)', 'git push --force can cause data loss. Get explicit user approval first.'),
    (r'git\s+checkout\s+[0-9a-f]{7,}', 'git checkout to a commit hash risks data loss. Get explicit user approval first.'),
]

# Force push to main/master is extra dangerous
FORCE_PUSH_MAIN = r'git\s+push\s+.*--force.*\s+(origin\s+)?(main|master)'

# Destructive restore operations
DANGEROUS_RESTORE = r'git\s+restore\s+(?!--staged).*'

# Environment files that should never be edited
PROTECTED_FILES = [
    '.env',
    '.env.local',
    '.env.production',
    '.env.development',
    'credentials.json',
    'secrets.yaml',
    'secrets.yml',
]


def is_dangerous_git_command(command: str) -> tuple[bool, str]:
    """Check if command is a dangerous git operation."""
    # Check for force push to main/master
    if re.search(FORCE_PUSH_MAIN, command, re.IGNORECASE):
        return True, 'NEVER force push to main/master branches. This can destroy team members\' work.'

    # Check other dangerous commands
    for pattern, message in DANGEROUS_GIT_COMMANDS:
        if re.search(pattern, command, re.IGNORECASE):
            return True, message

    # Check for destructive restore (but allow --staged which is safe)
    if re.search(DANGEROUS_RESTORE, command, re.IGNORECASE):
        return True, 'git restore (without --staged) reverts file changes. Only use if you authored the changes. Get approval first.'

    return False, ''


def is_protected_file_operation(tool_name: str, tool_input: dict) -> tuple[bool, str]:
    """Check if operation targets protected files like .env."""
    if tool_name not in ['Write', 'Edit']:
        return False, ''

    file_path = tool_input.get('file_path', '')

    for protected in PROTECTED_FILES:
        if protected in file_path or file_path.endswith(protected):
            return True, f'NEVER edit {protected} files. Only the user may change environment configuration and secrets.'

    return False, ''


def main():
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f'Error: Invalid JSON input: {e}', file=sys.stderr)
        sys.exit(1)

    tool_name = input_data.get('tool_name', '')
    tool_input = input_data.get('tool_input', {})

    # Check for protected file operations
    is_protected, protected_msg = is_protected_file_operation(tool_name, tool_input)
    if is_protected:
        print(protected_msg, file=sys.stderr)
        sys.exit(2)  # Exit code 2 blocks the tool call

    # Check for dangerous git commands
    if tool_name == 'Bash':
        command = tool_input.get('command', '')
        is_dangerous, danger_msg = is_dangerous_git_command(command)

        if is_dangerous:
            print(f'🛑 BLOCKED: {danger_msg}', file=sys.stderr)
            print(f'\nCommand attempted: {command}', file=sys.stderr)
            print('\nIf you genuinely need this operation, ask the user for explicit written approval.', file=sys.stderr)
            sys.exit(2)  # Exit code 2 blocks the tool call

    # Command is safe, allow it
    sys.exit(0)


if __name__ == '__main__':
    main()
