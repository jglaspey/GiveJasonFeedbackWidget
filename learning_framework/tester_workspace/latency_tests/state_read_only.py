#!/usr/bin/env python3
# ABOUTME: Python hook with state file read only
# ABOUTME: Measures read overhead vs no I/O

import json
import sys
from pathlib import Path

data = json.load(sys.stdin)
state_file = Path('/tmp/latency_test_state.json')
if state_file.exists():
    state = json.loads(state_file.read_text())
sys.exit(0)
