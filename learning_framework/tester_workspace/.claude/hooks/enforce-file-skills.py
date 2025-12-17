#!/usr/bin/env python3
# ABOUTME: PreToolUse hook that enforces skills based on file paths being edited
# ABOUTME: Tests file path detection accuracy and latency for skill enforcement

import json
import sys
import time
import re
import fnmatch
import os

def detect_skill_for_file(file_path: str) -> tuple[str | None, str]:
    """
    Detect which skill should be enforced based on the file path.
    Returns (skill_name, reason) or (None, "") if no skill matches.
    """
    # Normalize path for consistent matching
    normalized = file_path.replace('\\', '/')

    # Pattern 1: Skill files -> writing-skills
    if fnmatch.fnmatch(normalized, '*/.claude/skills/*') or fnmatch.fnmatch(normalized, '.claude/skills/*'):
        return ('writing-skills', 'editing a skill file')

    # Pattern 2: Settings files -> settings-json-patterns
    if normalized.endswith('settings.json') and '.claude' in normalized:
        return ('settings-json-patterns', 'editing Claude settings')

    # Pattern 3: Test files -> testing-anti-patterns
    test_patterns = [
        r'test_.*\.py$',           # test_foo.py
        r'.*_test\.py$',           # foo_test.py
        r'(^|/)tests?/.*\.py$',    # tests/foo.py or test/foo.py (handles both absolute and relative)
        r'.*\.test\.(ts|js|tsx|jsx)$',   # foo.test.ts
        r'.*\.spec\.(ts|js|tsx|jsx)$',   # foo.spec.ts
    ]
    if any(re.search(p, normalized) for p in test_patterns):
        return ('testing-anti-patterns', 'editing a test file')

    # Pattern 4: Worker files -> parallel-processing
    if '/workers/' in normalized and normalized.endswith('.py'):
        return ('parallel-processing', 'editing a worker file')

    return (None, '')

def main():
    start = time.time()

    # Write marker file to prove hook ran (for debugging)
    marker_path = '/tmp/hook_fired_marker.txt'
    with open(marker_path, 'a') as f:
        f.write(f"Hook fired at {time.time()} from nested tester_workspace\n")

    # Read hook input
    data = json.load(sys.stdin)

    # Extract file path from tool_input
    tool_input = data.get('tool_input', {})
    file_path = tool_input.get('file_path', '')

    if not file_path:
        return  # No file path, nothing to enforce

    # Detect which skill applies
    skill, reason = detect_skill_for_file(file_path)

    elapsed_ms = (time.time() - start) * 1000

    if skill:
        print(f"📚 FILE-BASED SKILL ENFORCEMENT")
        print(f"   File: {os.path.basename(file_path)}")
        print(f"   Reason: {reason}")
        print(f"   Required skill: {skill}")
        print(f"   You MUST invoke the {skill} skill before proceeding.")
        print(f"   ⏱️ Detection time: {elapsed_ms:.1f}ms")

    # Log latency warning if slow
    if elapsed_ms > 100:
        print(f"⚠️ Hook latency warning: {elapsed_ms:.0f}ms", file=sys.stderr)

if __name__ == '__main__':
    main()
