#!/usr/bin/env python3
# ABOUTME: SessionStart hook that reads and displays progress context.
# ABOUTME: Injects currentWork and lastSession summary into session start.

import json
import sys
import os
from pathlib import Path
from datetime import datetime


def main():
    # Get project directory
    project_dir = os.environ.get('CLAUDE_PROJECT_DIR', os.getcwd())
    progress_path = Path(project_dir) / 'project-progress.json'
    feature_path = Path(project_dir) / 'feature-list.json'

    if not progress_path.exists():
        sys.exit(0)

    try:
        data = json.loads(progress_path.read_text())
    except Exception:
        sys.exit(0)

    # Build context message
    lines = ["📋 **Session Context**", ""]

    # Current work
    current = data.get("currentWork", {})
    work_type = current.get("type", "general")

    if work_type == "plan":
        plan = current.get("plan", "unknown")
        task = current.get("planTask")
        lines.append(f"**Current Work:** Plan - `{plan}` (Task {task})")
    elif work_type == "debug":
        issue = current.get("debugIssue", "unknown")
        phase = current.get("debugPhase", "investigating")
        lines.append(f"**Current Work:** Debugging - {issue} ({phase})")
    elif work_type == "feature":
        feature_id = current.get("featureId", "unknown")
        # Try to get feature details
        if feature_path.exists():
            try:
                features = json.loads(feature_path.read_text()).get("features", [])
                feature = next((f for f in features if f.get("id") == feature_id), None)
                if feature:
                    lines.append(f"**Current Work:** Feature - {feature.get('name')} ({feature_id})")
                    if feature.get("github", {}).get("issueNumber"):
                        lines.append(f"  Issue: #{feature['github']['issueNumber']}")
                else:
                    lines.append(f"**Current Work:** Feature - {feature_id}")
            except Exception:
                lines.append(f"**Current Work:** Feature - {feature_id}")
        else:
            lines.append(f"**Current Work:** Feature - {feature_id}")
    else:
        lines.append("**Current Work:** General")

    # Last session
    last = data.get("lastSession", {})
    if last.get("summary"):
        date = last.get("date", "unknown")
        duration = last.get("duration_minutes", 0)
        summary = last.get("summary", "")
        lines.append("")
        lines.append(f"**Last Session:** {date} ({duration} min)")
        lines.append(f"  {summary[:100]}{'...' if len(summary) > 100 else ''}")

    # Next steps
    next_steps = last.get("nextSteps", [])
    if next_steps:
        lines.append("")
        lines.append("**Next Steps:**")
        for step in next_steps[:3]:
            lines.append(f"  - {step}")

    # Print to stderr (shown to Claude)
    print("\n".join(lines), file=sys.stderr)
    sys.exit(0)


if __name__ == "__main__":
    main()
