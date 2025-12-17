#!/usr/bin/env python3
# ABOUTME: SubagentStop hook that verifies git-operations subagent completed expected commits
# ABOUTME: Enforces that git subagents actually commit changes as intended

import json
import re
import subprocess
import sys


def read_transcript(transcript_path: str) -> list[dict]:
    """Read the JSONL transcript file."""
    try:
        with open(transcript_path, 'r') as f:
            return [json.loads(line) for line in f if line.strip()]
    except Exception:
        return []


def is_git_operations_subagent(transcript: list[dict]) -> bool:
    """Check if this subagent was launched for git operations."""
    # Look through transcript for Task tool call that launched this subagent
    for entry in transcript:
        if entry.get('type') == 'tool_use' and entry.get('name') == 'Task':
            params = entry.get('input', {})
            prompt = params.get('prompt', '').lower()
            description = params.get('description', '').lower()

            # Check for git-related keywords
            git_keywords = ['commit', 'git', 'version control', 'repository']
            if any(keyword in prompt or keyword in description for keyword in git_keywords):
                return True

    return False


def subagent_mentioned_commit(transcript: list[dict]) -> bool:
    """Check if subagent discussed committing in its responses."""
    commit_patterns = [
        r'\bgit\s+commit\b',
        r'\bcommitted\b',
        r'\bcommitting\b',
        r'\bcreate.*commit\b',
        r'\bmake.*commit\b',
    ]

    for entry in transcript:
        if entry.get('type') == 'text' and entry.get('role') == 'assistant':
            text = entry.get('content', '').lower()
            for pattern in commit_patterns:
                if re.search(pattern, text):
                    return True

    return False


def has_uncommitted_changes() -> bool:
    """Check if there are uncommitted changes."""
    try:
        result = subprocess.run(
            ['git', 'diff-index', '--quiet', 'HEAD', '--'],
            cwd='.',
            capture_output=True,
            timeout=5
        )
        return result.returncode != 0
    except Exception:
        return False


def get_recent_commit() -> str:
    """Get the most recent commit info."""
    try:
        result = subprocess.run(
            ['git', 'log', '-1', '--oneline'],
            cwd='.',
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return ''


def main():
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f'Error: Invalid JSON input: {e}', file=sys.stderr)
        sys.exit(1)

    transcript_path = input_data.get('transcript_path', '')

    if not transcript_path:
        # No transcript path, can't verify
        sys.exit(0)

    # Read transcript to understand what the subagent was supposed to do
    transcript = read_transcript(transcript_path)

    # Check if this was a git operations subagent
    if not is_git_operations_subagent(transcript):
        # Not a git subagent, don't check
        sys.exit(0)

    # This was a git subagent - verify it committed
    mentioned_commit = subagent_mentioned_commit(transcript)

    if not mentioned_commit:
        # Subagent didn't claim to commit, maybe it was just investigating
        sys.exit(0)

    # Subagent claimed to commit - verify no uncommitted changes remain
    if has_uncommitted_changes():
        recent_commit = get_recent_commit()
        message = f'''
⚠️ Git subagent completed but uncommitted changes remain.

Most recent commit: {recent_commit if recent_commit else "No recent commits found"}

The git-operations subagent indicated it would commit changes, but git status shows uncommitted work.

Either:
1. The commit failed (check for errors)
2. New changes were made after the commit
3. Some files weren't included in the commit

Please verify the commit was successful and all intended changes were committed.
'''.strip()

        print(message, file=sys.stderr)
        sys.exit(2)  # Block subagent completion

    # Everything looks good
    sys.exit(0)


if __name__ == '__main__':
    main()
