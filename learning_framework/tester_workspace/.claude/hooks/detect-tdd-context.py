#!/usr/bin/env python3
# ABOUTME: UserPromptSubmit hook for detecting TDD-relevant implementation context
# ABOUTME: Part of learning framework experiment h2 for skill enforcement via hooks

import json
import sys

def main():
    data = json.load(sys.stdin)
    prompt = data.get('user_prompt', '').lower()

    # Skip if already about testing
    if 'test' in prompt and ('write test' in prompt or 'add test' in prompt):
        print(json.dumps({
            "triggered": False,
            "reason": "already_testing",
            "prompt_preview": prompt[:50]
        }), file=sys.stderr)
        sys.exit(0)

    # High-confidence implementation keywords
    impl_keywords = [
        'implement', 'add feature', 'create function',
        'write code', 'build'
    ]

    triggered_keyword = None
    for kw in impl_keywords:
        if kw in prompt:
            triggered_keyword = kw
            break

    if triggered_keyword:
        print(f"⚠️ IMPLEMENTATION DETECTED: Use test-driven-development skill")
        print(f"   Write the failing test FIRST")
        print(f"   Trigger keyword: '{triggered_keyword}'")
        print(json.dumps({
            "triggered": True,
            "keyword": triggered_keyword,
            "skill": "test-driven-development"
        }), file=sys.stderr)
    else:
        print(json.dumps({
            "triggered": False,
            "prompt_preview": prompt[:50]
        }), file=sys.stderr)

if __name__ == "__main__":
    main()
