#!/usr/bin/env python3
# ABOUTME: UserPromptSubmit hook for detecting skill-relevant context in prompts
# ABOUTME: Part of learning framework experiment for skill enforcement via hooks

import json
import sys

def main():
    data = json.load(sys.stdin)
    prompt = data.get('user_prompt', '').lower()

    # High-confidence debugging keywords
    high_conf_debug = [
        'error', 'bug', 'broken', 'failing', "doesn't work",
        'not working', 'crash', 'exception'
    ]

    # Check for debugging context
    triggered_keyword = None
    for kw in high_conf_debug:
        if kw in prompt:
            triggered_keyword = kw
            break

    if triggered_keyword:
        print(f"⚠️ DEBUGGING DETECTED: Use systematic-debugging skill")
        print(f"   Trigger keyword: '{triggered_keyword}'")
        # Output to stderr for logging purposes
        print(json.dumps({
            "triggered": True,
            "keyword": triggered_keyword,
            "skill": "systematic-debugging"
        }), file=sys.stderr)
    else:
        # Log non-trigger for experiment tracking
        print(json.dumps({
            "triggered": False,
            "prompt_preview": prompt[:50]
        }), file=sys.stderr)

if __name__ == "__main__":
    main()
