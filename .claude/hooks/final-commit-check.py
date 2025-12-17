#!/usr/bin/env python3
# ABOUTME: Stop hook that performs final check for uncommitted changes before agent stops
# ABOUTME: Last safety net to ensure work is committed before session ends

import json
import subprocess
import sys


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
        return result.returncode != 0
    except Exception:
        # If git fails, don't block (might not be a git repo)
        return False


def is_file_ignored(filepath: str) -> bool:
    """Check if a file is gitignored."""
    try:
        result = subprocess.run(
            ['git', 'check-ignore', '-q', filepath],
            cwd='.',
            capture_output=True,
            timeout=5
        )
        return result.returncode == 0
    except Exception:
        return False


def get_changes_summary() -> tuple[str, bool]:
    """Get summary of uncommitted changes, filtering out gitignored files.

    Returns: (summary_string, has_non_ignored_changes)
    """
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
            # Filter out gitignored files
            non_ignored = []
            for line in lines:
                if not line.strip():
                    continue
                # Extract filepath from git status output (format: "XY filename" or "XY filename -> newname")
                parts = line.split()
                if len(parts) >= 2:
                    filepath = parts[1]
                    if not is_file_ignored(filepath):
                        non_ignored.append(line)

            if not non_ignored:
                return '', False

            if len(non_ignored) > 10:
                return '\n'.join(non_ignored[:10]) + f'\n... and {len(non_ignored) - 10} more files', True
            return '\n'.join(non_ignored), True
    except Exception:
        pass
    return 'Multiple files changed', True


def is_in_git_repo() -> bool:
    """Check if current directory is in a git repository."""
    try:
        result = subprocess.run(
            ['git', 'rev-parse', '--git-dir'],
            cwd='.',
            capture_output=True,
            timeout=5
        )
        return result.returncode == 0
    except Exception:
        return False


def main():
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f'Error: Invalid JSON input: {e}', file=sys.stderr)
        sys.exit(1)

    # Check if we're in a git repository
    if not is_in_git_repo():
        # Not a git repo, nothing to check
        sys.exit(0)

    # Check for uncommitted changes
    if not has_uncommitted_changes():
        # No uncommitted changes, all good
        sys.exit(0)

    # Uncommitted changes exist - check if any are non-ignored
    changes, has_non_ignored = get_changes_summary()

    if not has_non_ignored:
        # All changes are gitignored, nothing to commit
        sys.exit(0)

    message = f'''
🛑 STOP: You have uncommitted changes

Changes detected:
{changes}

Before finishing, you should commit your work according to git-operations best practices.

Please either:
1. Launch a git-operations subagent to commit these changes
2. Explain why these changes should remain uncommitted (e.g., debugging artifacts, incomplete work)

Don't end your session with uncommitted work unless there's a specific reason.
'''.strip()

    print(message, file=sys.stderr)
    sys.exit(2)  # Exit code 2 blocks stopping and shows message to Claude


if __name__ == '__main__':
    main()
