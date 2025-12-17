#!/usr/bin/env python3
# ABOUTME: Pre-commit hook that lints .claude/settings.json for common mistakes
# ABOUTME: Catches unquoted $CLAUDE_PROJECT_DIR paths and other gotchas

import json
import sys
import os
import re

def lint_settings_json():
    """Lint .claude/settings.json for common configuration mistakes."""

    project_dir = os.environ.get('CLAUDE_PROJECT_DIR', os.getcwd())
    settings_path = os.path.join(project_dir, '.claude', 'settings.json')

    if not os.path.exists(settings_path):
        # No settings.json to lint
        return 0, []

    try:
        with open(settings_path, 'r') as f:
            content = f.read()
            settings = json.loads(content)
    except json.JSONDecodeError as e:
        return 1, [f"Invalid JSON in settings.json: {e}"]

    errors = []
    warnings = []

    # Check for hooks configuration
    hooks = settings.get('hooks', {})

    for event_type, event_configs in hooks.items():
        if not isinstance(event_configs, list):
            continue

        for config in event_configs:
            hook_list = config.get('hooks', [])
            for hook in hook_list:
                if hook.get('type') != 'command':
                    continue

                command = hook.get('command', '')

                # Check for unquoted $CLAUDE_PROJECT_DIR
                # Pattern: $CLAUDE_PROJECT_DIR not preceded by " and not followed by proper quoting
                if '$CLAUDE_PROJECT_DIR' in command:
                    # Should be wrapped in escaped quotes: "\"$CLAUDE_PROJECT_DIR/...\""
                    if not command.startswith('"') or not command.endswith('"'):
                        errors.append(
                            f"Hook command in {event_type} has unquoted $CLAUDE_PROJECT_DIR.\n"
                            f"  Found: {command}\n"
                            f"  Fix: Wrap in escaped quotes: \"\\\"$CLAUDE_PROJECT_DIR/...\\\"\"\n"
                            f"  Why: Paths with spaces (like 'CopyClub GitHub') break without quotes."
                        )

    # Check for spaces before colons in allowed_tools
    allowed_tools = settings.get('allowed_tools', [])
    for tool in allowed_tools:
        if ' :' in tool:
            errors.append(
                f"Space before colon in allowed_tools pattern.\n"
                f"  Found: {tool}\n"
                f"  Fix: Remove space before colon\n"
                f"  Why: Validator accepts but runtime silently fails."
            )

    # Check for filename wildcards in allowed_tools
    for tool in allowed_tools:
        # Match patterns like *.json, *.py (wildcard in filename position)
        if re.search(r'\*\.[a-zA-Z]+["\)]', tool):
            warnings.append(
                f"Filename wildcard may not work in allowed_tools.\n"
                f"  Found: {tool}\n"
                f"  Note: Only directory wildcards like 'dir/*' are reliable.\n"
                f"  Consider: Using 'dir/*' or '*' instead."
            )

    return len(errors), errors + warnings


def main():
    """Main entry point for pre-commit hook."""
    error_count, messages = lint_settings_json()

    if messages:
        print("🔍 settings.json lint results:")
        print()
        for msg in messages:
            print(f"  {msg}")
            print()

    if error_count > 0:
        print(f"❌ Found {error_count} error(s) in settings.json")
        return 1
    elif messages:
        print(f"⚠️  Found {len(messages)} warning(s) in settings.json")
        return 0
    else:
        return 0


if __name__ == '__main__':
    sys.exit(main())
