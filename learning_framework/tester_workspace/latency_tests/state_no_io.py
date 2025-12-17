#!/usr/bin/env python3
# ABOUTME: Python hook with no state file I/O
# ABOUTME: Baseline for state file overhead comparison

import json
import sys

json.load(sys.stdin)
sys.exit(0)
