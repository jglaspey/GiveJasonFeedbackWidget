#!/usr/bin/env python3
# ABOUTME: UserPromptSubmit hook using pattern-based context detection
# ABOUTME: Experiment h3: Combined keyword + context analysis

import json
import sys
import re

def detect_debugging_patterns(prompt):
    """
    Pattern-based debugging detection.
    Returns (triggered, pattern_name) or (False, None)
    """
    # Pattern 1: "X is broken/failing/not working"
    if re.search(r'\b(is|are|was|were)\s+(broken|failing|not working|bugged|crashed)', prompt):
        return True, "X is broken/failing"

    # Pattern 2: "there is a/an bug/error/problem"
    if re.search(r'there\s+(is|are)\s+(a|an)?\s*(bug|error|problem|issue)', prompt):
        return True, "there is a bug"

    # Pattern 3: "getting/seeing/having error/exception"
    if re.search(r'(getting|seeing|having|throwing)\s+(an?\s+)?(error|exception|crash)', prompt):
        return True, "getting error"

    # Pattern 4: "doesn't/does not/won't work"
    if re.search(r"(doesn't|does\s+not|won't|will\s+not|can't|cannot)\s+work", prompt):
        return True, "doesn't work"

    # Pattern 5: High-precision single keywords (from h1)
    high_precision = ['bug', 'broken', 'failing', 'crash', 'exception']
    for kw in high_precision:
        if re.search(rf'\b{kw}\b', prompt):
            # But exclude implementation contexts
            if not re.search(r'(handle|handling|add|log|return)\s+.{0,20}' + kw, prompt):
                return True, f"keyword:{kw}"

    return False, None

def detect_implementation_patterns(prompt):
    """
    Pattern-based implementation detection.
    Returns (triggered, pattern_name) or (False, None)
    """
    # Skip if already about testing
    if re.search(r'(write|add|create|run)\s+(a\s+)?tests?', prompt):
        return False, None

    # Pattern 1: "implement/build X"
    if re.search(r'\b(implement|build)\s+\w', prompt):
        return True, "implement/build X"

    # Pattern 2: "add (a/the/new) X (to Y)"
    if re.search(r'\badd\s+(a|the|new)?\s*\w+\s+(to|for|that)', prompt):
        return True, "add X to Y"

    # Pattern 3: "create (a/new) X"
    if re.search(r'\bcreate\s+(a|new)?\s*\w+', prompt):
        return True, "create X"

    # Pattern 4: "make (a/the) X"
    if re.search(r'\bmake\s+(a|the)?\s*\w+', prompt):
        return True, "make X"

    # Pattern 5: "write code/function/class"
    if re.search(r'\bwrite\s+(code|a\s+function|a\s+class|a\s+method)', prompt):
        return True, "write code/function"

    # Pattern 6: "new X for/to"
    if re.search(r'\bnew\s+\w+\s+(for|to)\b', prompt):
        return True, "new X for"

    return False, None

def main():
    data = json.load(sys.stdin)
    prompt = data.get('user_prompt', '').lower()

    results = []

    # Check debugging patterns
    debug_triggered, debug_pattern = detect_debugging_patterns(prompt)
    if debug_triggered:
        results.append({
            "skill": "systematic-debugging",
            "pattern": debug_pattern
        })
        print(f"⚠️ DEBUGGING DETECTED: Use systematic-debugging skill")
        print(f"   Pattern: '{debug_pattern}'")

    # Check implementation patterns
    impl_triggered, impl_pattern = detect_implementation_patterns(prompt)
    if impl_triggered:
        results.append({
            "skill": "test-driven-development",
            "pattern": impl_pattern
        })
        print(f"⚠️ IMPLEMENTATION DETECTED: Use test-driven-development skill")
        print(f"   Write the failing test FIRST")
        print(f"   Pattern: '{impl_pattern}'")

    # Log to stderr
    print(json.dumps({
        "triggered": len(results) > 0,
        "results": results,
        "prompt_preview": prompt[:50]
    }), file=sys.stderr)

if __name__ == "__main__":
    main()
