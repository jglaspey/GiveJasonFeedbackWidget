#!/usr/bin/env python3
# ABOUTME: Python hook with content pattern analysis
# ABOUTME: Measures regex matching overhead on various content sizes

import json
import sys
import re

data = json.load(sys.stdin)
content = data.get('tool_input', {}).get('new_string', '')

# Simulate all content patterns from enforcement hooks
patterns = [
    r'time\.sleep\s*\(',
    r'await\s+asyncio\.sleep\s*\(',
    r'setTimeout\s*\(',
    r'expect\(.*mock.*\)\.toHaveBeenCalled',
    r'anthropic\.Anthropic\s*\(',
    r'from\s+anthropic\s+import',
    r'def\s+test_',
    r'class\s+Test',
    r'assert\s+',
    r'\.write\(',
    r'\.read\(',
]

for p in patterns:
    re.search(p, content, re.IGNORECASE)

sys.exit(0)
