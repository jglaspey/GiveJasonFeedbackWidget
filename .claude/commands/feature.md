# Feature

Create a new feature with GitHub issue, branch, and local tracking.

**Usage:** `/feature <description>`

## Steps

### 1. Parse Feature Description
Extract the feature description from the argument. If no argument provided, ask for one.

### 2. Generate Feature ID
```bash
# Count existing features to generate next ID
cat feature-list.json 2>/dev/null | python3 -c "import json,sys; d=json.load(sys.stdin); print(len(d.get('features',[]))+1)" || echo "1"
```

Feature ID format: `feature-XXX` (zero-padded, e.g., `feature-001`)

### 3. Create GitHub Issue
```bash
gh issue create --title "FEATURE_DESCRIPTION" --body "## Description

FEATURE_DESCRIPTION

## Verification Criteria

- [ ] Feature implemented
- [ ] Tests passing
- [ ] Code reviewed

---
*Created via /feature command*"
```

Capture the issue number from the output.

### 4. Create Feature Branch
```bash
# Ensure we're on main and up to date
git checkout main
git pull origin main

# Create and checkout feature branch
git checkout -b feature/feature-XXX-short-name
```

Branch naming: `feature/feature-XXX-short-slug` (slugify description, max 30 chars)

### 5. Update feature-list.json
Add the new feature to tracking:
```json
{
  "id": "feature-XXX",
  "name": "Short name",
  "description": "Full description",
  "status": "in_progress",
  "branch": "feature/feature-XXX-short-name",
  "github": {
    "issueNumber": 123,
    "prNumber": null
  },
  "verification": [
    "Feature implemented",
    "Tests passing",
    "Code reviewed"
  ],
  "createdAt": "2025-12-11T00:00:00Z",
  "completedAt": null
}
```

### 6. Update project-progress.json
Set currentWork to this feature:
```json
{
  "currentWork": {
    "type": "feature",
    "featureId": "feature-XXX",
    "plan": null,
    "planTask": null,
    "debugIssue": null,
    "debugPhase": null
  }
}
```

### 7. Report
```
## Feature Created

**ID:** feature-XXX
**Description:** DESCRIPTION
**Issue:** #123 (link)
**Branch:** feature/feature-XXX-short-name

Ready to work. When done, run `/checkpoint` to commit and create PR.
```

---

## Arguments

- `/feature <description>` - Create new feature with the given description
- `/feature list` - Show all features and their status
- `/feature status` - Show current feature details
