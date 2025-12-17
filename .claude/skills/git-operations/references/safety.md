# ABOUTME: Dangerous git commands, absolute safety rules, and protection mechanisms
# ABOUTME: Referenced from git-operations skill when handling destructive operations or special cases

# Git Safety Rules and Dangerous Commands

## Absolute Safety Rules

These rules MUST NEVER be violated:

### Rule 1: Never Run Destructive Operations Without Explicit Approval

**ABSOLUTELY NEVER run these commands without explicit, written approval:**

- `git reset --hard`
- `git reset HEAD~` (or any commit-removing reset)
- `git push --force`
- `git push --force-with-lease` to main/master
- `git clean -fd`
- `git checkout` to an older commit (data loss risk)
- `git restore` to revert files you didn't author

**Why:** These commands permanently delete work. No undo.

**Exception:** You may run `git restore --staged` to unstage files (this is safe).

**Enforcement:** PreToolUse hook blocks these commands.

### Rule 2: Never Edit Environment Files

**NEVER edit, commit, or restore these files:**
- `.env`
- `.env.local`
- `.env.production`
- Any file containing secrets/credentials
- `credentials.json`
- `secrets.yaml`

**Why:** Only the user may change environment configuration. Agents touching these files creates security risks.

**Enforcement:** PreToolUse hook blocks Write/Edit operations on these files.

### Rule 3: Always Quote Special Characters in Paths

**Paths containing these characters MUST be quoted:**
- Brackets: `[` `]`
- Parentheses: `(` `)`
- Spaces
- Asterisks (unless intentional glob)

```bash
# ❌ WRONG - Shell will interpret brackets as glob
git add src/app/[candidate]/page.tsx

# ✅ CORRECT - Quoted path
git add "src/app/[candidate]/page.tsx"

# ❌ WRONG - Space causes two arguments
git add my file.txt

# ✅ CORRECT - Quoted path
git add "my file.txt"
```

**Why:** Shell interprets special characters, causing wrong files to be affected.

**Enforcement:** Your responsibility - hooks can't easily detect this.

### Rule 4: Never Amend Commits Without Approval

**Never use `git commit --amend` unless:**
1. User explicitly requested amend, OR
2. Pre-commit hook modified files and you need to update the commit

**Before amending, ALWAYS check:**
```bash
# Check authorship
git log -1 --format='%an %ae'

# Check if pushed
git status  # Look for "Your branch is ahead"
```

**NEVER amend if:**
- Commit was authored by someone else
- Commit has been pushed to remote
- You're unsure

**Why:** Amending rewrites history. If others have the commit, this causes conflicts.

### Rule 5: Coordinate Before Touching Other Agents' Work

**Before removing or reverting files:**
1. Check `git log <file>` to see who last edited it
2. If another agent (or user), STOP and coordinate
3. Never delete another agent's in-progress work

**Why:** Multiple agents may be working simultaneously. Deleting their work is catastrophic.

## Safe File Management

### Safe File Deletions

**You MAY delete files when:**
- ✅ Your changes make them obsolete (e.g., refactor moved code)
- ✅ Feature removal makes them unnecessary
- ✅ User explicitly requested deletion

**You MUST NOT delete files when:**
- ❌ Trying to fix a type/lint error (other agents may be editing)
- ❌ File was authored by another agent (coordinate first)
- ❌ Unsure why the file exists

**Before deleting:**
```bash
# Check who last modified
git log --oneline -n 5 -- path/to/file.txt

# Check if other agents are working on it
git status  # Look for uncommitted changes in related files
```

### Safe File Moves/Renames

**Moving/renaming files is allowed:**
```bash
git mv old_name.py new_name.py
git commit -m "Rename old_name to new_name for clarity"
```

**Git tracks renames automatically.**

## Safe Git Patterns

### Pattern 1: Atomic Commit of Specific Files

**For tracked files:**
```bash
# 1. Check what you're committing
git status

# 2. Commit only the files you modified (quote paths with special chars)
git commit -m "Your message" -- path/to/file1.py path/to/file2.py
```

**For brand-new files:**
```bash
# 1. Clear staging area
git restore --staged :/

# 2. Add only the files you created
git add "path/to/file1.py" "path/to/file2.py"

# 3. Commit those files
git commit -m "Your message" -- "path/to/file1.py" "path/to/file2.py"
```

**Why:** Ensures you only commit your changes, not unrelated files.

### Pattern 2: Pre-Commit Check

**Always before committing:**
```bash
# 1. Check status
git status

# 2. Review diff
git diff

# 3. Review staged changes (if any)
git diff --staged

# 4. If everything looks good, commit
git commit -m "Your message"
```

### Pattern 3: Safe Rebase (Only When Necessary)

**If you must rebase:**
```bash
# 1. Export env vars to avoid editor opening
export GIT_EDITOR=:
export GIT_SEQUENCE_EDITOR=:

# 2. Rebase with automatic mode
git rebase main --no-edit
```

**NEVER use `git rebase -i` (interactive mode)** - requires manual editor interaction.

### Pattern 4: Handling Pre-Commit Hook Changes

**If pre-commit hook modifies files:**
```bash
# 1. Check authorship
git log -1 --format='%an %ae'
# Should show your name/email

# 2. Check not pushed
git status
# Should show "Your branch is ahead" (local only)

# 3. Amend commit
git commit --amend --no-edit
```

**Only amend if BOTH conditions are true:**
- You authored the commit
- Commit not pushed to remote

## Troubleshooting

### Problem: "I tried to commit but git rejected it"

**Check:**
1. Do you have write permissions to the repo?
2. Is the remote accessible?
3. Are there merge conflicts?
4. Did you quote special characters in paths?

### Problem: "Hook blocked my git command"

**This is intentional.** Review what you were trying to do:
- Was it destructive? (reset, force push, etc.)
- Get explicit user approval first
- Or find a safer alternative

### Problem: "I committed the wrong files"

**Don't panic:**
```bash
# Check what you committed
git show HEAD

# If commit is local (not pushed), you can fix:
# Option 1: Amend (if you authored it)
git commit --amend

# Option 2: Reset (ONLY if local and you authored it)
git reset HEAD~1  # Keeps changes, uncommits
```

**If already pushed:** Ask user for help.

## Quick Reference

| Action | Command | Safety Level |
|--------|---------|--------------|
| Commit specific files | `git commit -m "msg" -- file1 file2` | ✅ Safe |
| Check status | `git status` | ✅ Safe |
| View diff | `git diff` | ✅ Safe |
| View log | `git log --oneline -n 10` | ✅ Safe |
| Stage files | `git add "file.txt"` | ✅ Safe |
| Unstage all | `git restore --staged :/` | ✅ Safe |
| Reset hard | `git reset --hard` | ⛔ NEVER without approval |
| Force push | `git push --force` | ⛔ NEVER to main/master |
| Amend commit | `git commit --amend` | ⚠️ Only if you authored + not pushed |
| Edit .env | - | ⛔ NEVER |
