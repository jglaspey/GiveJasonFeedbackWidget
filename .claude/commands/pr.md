# PR

Manage pull requests for the current feature.

**Usage:** `/pr [action]`

## Actions

### `/pr` or `/pr create`
Create a PR for the current feature branch.

### Steps:

1. **Verify on feature branch**
```bash
git branch --show-current
```
Must be on a `feature/*` branch, not main.

2. **Push current branch**
```bash
git push -u origin $(git branch --show-current)
```

3. **Get feature info from feature-list.json**
Find the feature matching the current branch to get issue number and description.

4. **Create PR**
```bash
gh pr create \
  --title "FEATURE_NAME" \
  --body "## Summary

FEATURE_DESCRIPTION

Closes #ISSUE_NUMBER

## Changes

- [Describe changes]

## Verification

- [ ] Feature implemented per requirements
- [ ] Tests passing
- [ ] Code reviewed

---
*Created via /pr command*"
```

5. **Update feature-list.json**
Set `github.prNumber` to the new PR number.

6. **Report**
```
## PR Created

**PR:** #456 (link)
**Title:** FEATURE_NAME
**Closes:** #123

Ready for review.
```

---

### `/pr status`
Check the status of the current feature's PR.

```bash
gh pr view --json state,reviews,checks,mergeable
```

Report:
- State (open, merged, closed)
- Review status
- CI check status
- Merge conflicts

---

### `/pr update`
Update the PR description with latest progress.

```bash
gh pr edit PR_NUMBER --body "UPDATED_BODY"
```

---

### `/pr merge`
Merge the PR if checks pass.

1. **Check PR status**
```bash
gh pr checks
```

2. **If all checks pass, merge**
```bash
gh pr merge --squash --delete-branch
```

3. **Update feature-list.json**
Set `status: "completed"` and `completedAt` timestamp.

4. **Update project-progress.json**
Clear `currentWork` back to general.

5. **Report**
```
## PR Merged

**PR:** #456
**Feature:** feature-XXX - DESCRIPTION
**Status:** Completed

Switched back to main branch.
```

---

### `/pr list`
List all open PRs.

```bash
gh pr list --state open
```
