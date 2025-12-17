#!/usr/bin/env python3
# ABOUTME: Python hook with state file read and write
# ABOUTME: Measures full I/O overhead vs read-only

import json
import sys
from pathlib import Path

data = json.load(sys.stdin)
state_file = Path('/tmp/latency_test_state.json')
if state_file.exists():
    state = json.loads(state_file.read_text())
else:
    state = {}
state['count'] = state.get('count', 0) + 1
state_file.write_text(json.dumps(state))
sys.exit(0)
