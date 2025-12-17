#!/usr/bin/env python3
# ABOUTME: SessionStart hook that reminds about skill discipline on first message
# ABOUTME: Shows reminder once per session, uses temp file to track

import json
import sys
from pathlib import Path

SKILL_REMINDER = """
📚 **Skill Discipline Reminder**

Before responding, check: Does a skill apply to this task?

Key skills available:
- **systematic-debugging** - For any bug or test failure
- **test-driven-development** - For any feature or bugfix
- **verification-before-completion** - Before claiming work is done
- **project-discovery** - For new project design
- **writing-plans** / **executing-plans** - For implementation planning
- **git-operations** - For commits and version control
- **journal-discipline** - For capturing insights and searching past experience

**Rule:** If a skill applies, announce it and follow it exactly.

**Memory:** For complex work, search your journal first for relevant past experience.

See **skill-discipline** skill for full protocol.
""".strip()

def main():
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f'Error: Invalid JSON input: {e}', file=sys.stderr)
        sys.exit(1)

    session_id = input_data.get('session_id', '')

    if not session_id:
        sys.exit(0)

    # Check if we've already shown the reminder for this session
    reminder_file = Path('/tmp') / f'claude_skill_reminder_{session_id}'

    if reminder_file.exists():
        # Already shown this session
        sys.exit(0)

    # Mark as shown
    reminder_file.write_text('shown')

    # Output the reminder (will be shown to Claude)
    print(SKILL_REMINDER)
    sys.exit(0)

if __name__ == '__main__':
    main()
