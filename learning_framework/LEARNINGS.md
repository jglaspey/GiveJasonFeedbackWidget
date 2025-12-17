# Learning Framework - Development Learnings

## 2025-12-01: Initial Implementation

### What We Built

Started with MVP approach instead of full orchestration:

1. **SQLite knowledge base** (`knowledge_base.py`)
   - Simple schema for features, experiments, patterns, gotchas, best practices
   - Confidence scoring based on experiment success rate + pattern confidence

2. **CLI for manual recording** (`record_experiment.py`)
   - Record experiment outcomes
   - Add patterns, gotchas, best practices
   - Show current knowledge summary

3. **Test plan format** (`test_plans/skills_invocation.yaml`)
   - Simplified from the original design doc
   - Focus on hypotheses and test prompts
   - Manual testing process documented in the plan itself

### Design Decisions

**Why no orchestrator yet:**
- The original design assumed Agent SDK API that may not match reality
- Two-instance coordination is complex - manual testing validates the approach first
- Can iterate faster on the knowledge schema with manual input

**Knowledge base structure:**
- Used SQLite Row factory for easy dict conversion
- JSON for nested data (configuration, examples, evidence)
- Confidence scores at multiple levels (feature, pattern, best practice)

**CLI design:**
- Single tool with modes (experiment, pattern, gotcha, practice, show)
- Mutually exclusive mode flags keep it simple
- Verbose help with examples since this will be used manually

### Things That Worked

1. **Starting simple** - Took ~30 minutes to get working e2e
2. **sqlite3.Row factory** - Makes dict conversion trivial
3. **Combining all recording into one CLI** - Less cognitive overhead

### Things to Watch

1. **Confidence calculation** - Current formula (40% experiments, 60% patterns) is arbitrary
2. **Evidence tracking** - Pattern `evidence` field is list of experiment IDs but not populated
3. **Expected "uncertain"** - Experiment success=True when expected is uncertain, may be wrong

### Next Steps (When Ready)

1. **Run real skill invocation tests** - Create actual test skills, test with Claude Code
2. **Refine knowledge schema** - May need to track more context per experiment
3. **Build analysis prompts** - Dev instance prompts for analyzing results
4. **Consider automation** - Once patterns are clear, automate the tester

### Questions to Answer

1. What does the actual Agent SDK API look like for spawning Claude instances?
2. Can we observe tool calls from a Claude Code transcript?
3. What's the minimal viable "Tester" instance setup?

---

## 2025-12-01: Skill Discovery Insight

**Learning:** Skills are discovered relative to where Claude Code is launched. The `.claude/skills/`
directory must be at the project root where you run `claude`.

**Implication for tester_workspace:**
- Need to `cd tester_workspace` and run `claude` from there
- OR make tester_workspace its own project with proper structure
- The skills won't be discovered if you run from parent directory

**Testing approach:**
```bash
cd learning_framework/tester_workspace
claude  # skills should now be available
```

---

## 2025-12-01: Agent SDK API Verification

**Verified:** The claude-agent-sdk API matches our skill documentation.

**Key exports:**
- `query()` - one-shot async iterator for prompts
- `ClaudeSDKClient` - context manager for conversations
- `ClaudeAgentOptions` - configuration dataclass

**ClaudeAgentOptions key fields (verified from `help()`):**
- `cwd` - working directory for file operations
- `permission_mode` - 'default', 'acceptEdits', 'plan', 'bypassPermissions'
- `max_turns` - limit conversation turns
- `system_prompt` - override system prompt
- `settings` - path to settings.json

**Message types yielded:**
- `UserMessage`, `AssistantMessage`, `SystemMessage`, `ResultMessage`, `StreamEvent`

**Created `run_experiment.py`:**
- Uses Agent SDK to spawn Claude in tester_workspace
- Captures tool calls including Skill usage
- Outputs suggested recording command

**Question answered:** Yes, we can observe tool calls from the SDK responses. The `tool_use`
messages include the tool name and input, which lets us detect skill invocation.

---

## 2025-12-01: Experiment Runner Works, Skills Not Discovered

**Success:** `run_experiment.py` successfully:
- Spawns Claude via Agent SDK in tester_workspace
- Captures tool calls (Read tool observed)
- Parses AssistantMessage.content blocks correctly
- Shows ResultMessage with usage stats

**SDK Message Structure (key learning):**
- Messages are dataclasses, not dicts
- `AssistantMessage.content` is a list of blocks (TextBlock, ToolUseBlock)
- `ToolUseBlock` has `.name` and `.input` attributes
- `SystemMessage` has init data showing discovered tools, skills, etc.

**Issue Discovered:** Skills array is empty `'skills': []` in init message.

**Tested:**
1. Created skills in `tester_workspace/.claude/skills/` with proper structure
2. Initialized git repo in tester_workspace
3. Still no skills discovered

**Hypotheses for why skills aren't discovered:**
1. Skills may need specific YAML frontmatter format
2. May need to be registered somewhere else
3. Agent SDK `cwd` option may not affect skill discovery path
4. Need to investigate skill discovery mechanism

**Next step:** Research how Claude Code discovers skills - check if there's a config
or if it's based on specific directory traversal logic.

---

## 2025-12-01: SOLVED - Skill Discovery with add_dirs

**Solution found!** The `add_dirs` option in ClaudeAgentOptions is the key.

```python
options = ClaudeAgentOptions(
    cwd=str(workspace),
    add_dirs=[str(workspace)],  # THIS is what enables skill discovery
    setting_sources=['project', 'local']
)
```

**With this change:**
```
'skills': ['test-skill-detailed', 'test-skill-minimal']
```

**Key learnings:**
1. `cwd` alone is not enough - it sets working directory but not skill search path
2. `add_dirs` adds directories to Claude's search path for skills and settings
3. `setting_sources` controls which settings files are loaded

**Observation:** Claude also sees skills described in CLAUDE.md - it responded with
the harness skills list even though those are in a different directory. This suggests
CLAUDE.md references are separate from actual skill loading.

**Skills in init message = skills that can be invoked via Skill tool**

Now ready to test actual skill invocation!

---

## 2025-12-01: First Skill Invocation Experiments

**Ran 7 experiments** testing different prompts to see what triggers skill invocation.

### Experiments Run

| Prompt | Skill Invoked? | Notes |
|--------|----------------|-------|
| "Use the test-skill-detailed skill to analyze test.txt" | YES | Explicit skill name |
| "Analyze test.txt for patterns and anomalies" | YES | Multiple keywords from description |
| "Read test.txt and tell me what's in it" | NO | Generic phrase |
| "Review test.txt" | NO | Single generic keyword |
| "Analyze test.txt" | NO | Single generic keyword |
| "Look for patterns in test.txt" | NO | Single keyword from description |
| "Find anomalies in test.txt" | YES | Distinctive domain keyword |

### Patterns Discovered

**1. Explicit skill name always works (95% confidence)**
- Saying "Use the X skill" reliably triggers invocation
- This is the most reliable method

**2. Distinctive keywords in description help (70% confidence)**
- Words that are unique to the skill's domain trigger invocation
- "anomalies" worked because it's distinctive
- "patterns" alone didn't work because it's more generic
- Combination "patterns and anomalies" worked (matches description exactly)

### Gotcha Discovered

**Generic verbs don't trigger skills (medium severity)**
- Common verbs like 'review', 'analyze', 'check' alone don't trigger skill invocation
- Even if they're in the skill description
- Workaround: Use distinctive domain-specific terms or explicitly name the skill

### Implications for Skill Design

To make skills invoke reliably:
1. Use distinctive, domain-specific keywords in the description
2. Avoid relying on generic verbs like "analyze", "review", "check"
3. Consider the frontmatter `description` field carefully - it seems to influence invocation
4. Document synonyms but don't expect them all to trigger invocation

### Next Experiments to Run

1. Test if changing the skill description affects invocation
2. Test with the minimal skill (has sparse description)
3. Test what happens with multiple matching skills
4. Test if system prompt mentions affect invocation

---

## 2025-12-01: Hooks Configuration - Root Cause and Validation

**Critical Discovery:** Hooks exist in `.claude/hooks/` but were never firing because
`.claude/settings.json` doesn't exist. Only `.claude/settings.local.json` exists,
which contains permissions but no hooks configuration.

### What Was Missing

The hook scripts were present and functional when tested in isolation:
```bash
# This works - exits 2 and shows block message
echo '{"tool_name": "Bash", "tool_input": {"command": "git reset --hard"}}' | \
  python .claude/hooks/validate-git-command.py
```

But they never fired because Claude Code needs `settings.json` to configure when
hooks should run and which scripts to execute.

### Solution Validated in tester_workspace

Created `settings.json` with hooks configuration:
```json
{
  "hooks": {
    "PreToolUse": [{
      "matcher": "Bash|Write|Edit",
      "hooks": [{"type": "command", "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/validate-git-command.py"}]
    }],
    "PostToolUse": [{
      "matcher": "Bash",
      "hooks": [{"type": "command", "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/post-test-commit-check.py"}]
    }],
    "SubagentStop": [{
      "hooks": [{"type": "command", "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/verify-git-subagent.py"}]
    }],
    "Stop": [{
      "hooks": [
        {"type": "command", "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/final-commit-check.py"},
        {"type": "command", "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/track-session-time.py"}
      ]
    }],
    "UserPromptSubmit": [{
      "hooks": [{"type": "command", "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/session-start-tracking.py"}]
    }]
  }
}
```

### Validation Results

**Test 1: PreToolUse blocks dangerous git commands** ✅
- Prompt: "Please run 'git reset --hard' to clean up the workspace"
- Result: Hook blocked the command with error message
- Hook fired multiple times as Claude tried workarounds (git restore, etc.)
- Exit code 2 correctly prevents tool execution

**Test 2: UserPromptSubmit records session start** ✅
- Session start file created at `/tmp/claude_session_start_{session_id}`
- Timestamp recorded correctly in ISO format
- Works via Agent SDK spawned instances

**Test 3: Stop hook fires when session ends** ✅
- Claude said "Hello and goodbye!"
- Hook immediately fired: "🛑 STOP: You have uncommitted changes"
- Claude launched git-operations subagent (as designed!)
- Hook fires repeatedly until clean exit

### Key Findings

1. **$CLAUDE_PROJECT_DIR works** - Hooks find their scripts regardless of cwd
2. **Multiple hooks on same event work** - Both final-commit-check and track-session-time configured on Stop
3. **Hooks fire in Agent SDK context** - Not just interactive Claude Code
4. **Exit code 2 blocks and shows message** - Claude sees the error and can respond
5. **Stop hook persistence** - Keeps blocking until issue resolved or explained

### Gotcha Discovered

**Git operations in tester_workspace need permissions**
- The git-operations subagent's `git add` and `git commit` commands got "requires approval"
- This is because tester_workspace settings don't allow these commands
- Need to add git permissions to tester_workspace OR use acceptEdits permission mode

### Next Steps

1. Apply this configuration to main harness `.claude/settings.json`
2. Merge permissions from settings.local.json with hooks from settings.json
3. Test complete workflow: session → work → tests → commit prompt → stop check

---

## 2025-12-01: Skill Size Impact Testing

**Tested the community claim that skills over 200 lines cause "context sludge".**

### Test Setup

Created test skills of varying sizes:
- 50-line skill with 5 numbered steps
- 200-line skill with 20 numbered steps (at claimed threshold)
- 500-line skill with 50 numbered steps (well over threshold)

### Results

| Skill Size | Steps | Steps Output | Duration | Degradation? |
|------------|-------|--------------|----------|--------------|
| 50 lines   | 5     | 5/5 (100%)   | ~8s      | None         |
| 200 lines  | 20    | 20/20 (100%) | ~8s      | None         |
| 500 lines  | 50    | 50/50 (100%) | ~17s     | None         |

### Key Finding

**The 200-line threshold claim is NOT supported on Opus 4.5.**

All steps from all skills were correctly processed and output, including the 500-line
skill with 50 steps. No skipping, summarizing, or degradation was observed.

### Implications

- Community advice may be model-version specific
- Always validate claims empirically rather than accepting at face value
- Opus 4.5 can handle large skills without the claimed "context sludge"

---

## 2025-12-01: Progressive Disclosure Testing

**Tested whether Claude selectively reads reference files based on task topic.**

### Test Setup

Created tiered skill with:
- Entry point `skill.md` with explicit topic-to-file mapping
- `references/database.md` for database topics
- `references/api.md` for API topics
- `references/testing.md` for testing topics

### Results

| Prompt Topic | Files Read | Files NOT Read |
|--------------|-----------|----------------|
| Database setup | skill.md, database.md | api.md, testing.md |
| API integration | skill.md, api.md | database.md, testing.md |

### Key Finding

**Progressive disclosure works when explicitly instructed.**

Claude follows clear instructions in skill.md about which reference files to read
for specific topics. This enables token-efficient tiered loading.

### Best Practice

Use explicit topic-to-file mapping in skill entry points:
```markdown
### Database Operations
**Reference:** Read `references/database.md` when the user asks about databases.
```

---

## 2025-12-01: Hooks and Skills Interaction

**Tested orthogonality between hooks and skills.**

### Key Finding

**Hooks and skills are orthogonal - they operate at different layers.**

- Hooks fire on tool events (PreToolUse, PostToolUse, Stop)
- Skills are invoked by Claude's decision logic based on prompt content
- Adding hooks does not affect skill invocation behavior
- They don't interfere with each other

### Timing

- UserPromptSubmit hooks run before Claude processes the prompt
- PreToolUse hooks run before tool execution (can block/modify)
- PostToolUse hooks run after tool completes
- Stop hooks run when session ends

---

## 2025-12-01: Hook Path Quoting - Spaces in $CLAUDE_PROJECT_DIR

**Problem discovered:** Hook commands using `$CLAUDE_PROJECT_DIR` were failing with error:
```
/bin/sh: /Users/justinkistner/Documents/CopyClub: is a directory
```

**Root cause:** The project path contains a space ("CopyClub GitHub"). When bash expands
`$CLAUDE_PROJECT_DIR/.claude/hooks/foo.py` without quotes, it splits at the space:
- Arg 1: `/Users/justinkistner/Documents/CopyClub`
- Arg 2: `GitHub/agent-dev-harness/.claude/hooks/foo.py`

**Solution:** Wrap hook commands in escaped quotes in settings.json:

```json
// ❌ WRONG
"command": "$CLAUDE_PROJECT_DIR/.claude/hooks/validate-git-command.py"

// ✅ CORRECT
"command": "\"$CLAUDE_PROJECT_DIR/.claude/hooks/validate-git-command.py\""
```

**Prevention measures added:**
1. Gotcha added to `settings-json-patterns` skill with detection and fix
2. Pre-commit hook (`lint-settings-json.py`) catches unquoted paths
3. Quick reference table updated with hook quoting patterns

**Key learning:** Always quote shell variable expansions in settings.json hook commands,
even if your current path doesn't have spaces. Future clones might.

---

## 2025-12-01: Externalized Memory Pattern

**Tested cross-session state persistence via project files.**

### Test Setup

Created `tasks.json` with structured task state:
```json
{
  "tasks": [
    {"id": 1, "name": "Setup database", "status": "completed"},
    {"id": 2, "name": "Create API", "status": "completed"},
    {"id": 3, "name": "Build UI", "status": "pending"}
  ]
}
```

### Results

Claude correctly:
1. Read the tasks.json file
2. Identified Task 3 as the next task (first pending)
3. Provided reasoning about dependencies

### Key Finding

**Structured JSON is reliably parsed for state persistence.**

The externalized memory pattern works well with JSON files containing status fields.
This validates the long-running agent architecture from community insights.

### Best Practice

Use JSON with explicit status fields for task state:
- `status: "completed"` / `status: "pending"` / `status: "in_progress"`
- Enables reliable cross-session state tracking
- Claude understands the semantics and picks correct next task

---

## 2025-12-02: Coloring Page Topic Taxonomy (topic_source_analysis)

**Analyzed 3 competitor coloring page sites to understand topic organization.**

### Competitors Analyzed
- Coloring Bunny (coloringbunny.com) - 15 categories
- Monday Mandala (mondaymandala.com) - Flat URL structure, diverse content types
- Creative Kids Color (creativekidscolor.com) - 12 coloring + word puzzle categories

### Hypothesis Results

| ID | Statement | Result |
|----|-----------|--------|
| h1 | Competitors use more than 3 top-level source types | **CONFIRMED** - Found 7 distinct types |
| h2 | Age/difficulty is a major organizing principle | **PARTIAL** - Exists but not top-level |
| h3 | Licensed vs original handled differently | **CONFIRMED** - Pop culture is siloed |

### Key Pattern Discovered: Multi-Dimensional Taxonomy

Our initial model (seasonal, trending, evergreen) was too simplistic. Topics are organized across multiple dimensions:

**Topic Dimension:**
- Evergreen (animals, nature, vehicles, fantasy)
- Seasonal (holidays, months, seasons)
- Pop Culture (movies/TV, games, anime)

**Format Dimension:**
- Traditional coloring pages
- Color-by-number
- Templates (cut-outs)
- Mandalas/patterns

**Audience Dimension:**
- Kids (simple outlines)
- Adults (mindfulness, detailed)

**Content Type Dimension (beyond coloring):**
- Worksheets (educational)
- Word puzzles (crosswords, scrambles, searches)
- Party planning content
- Utility printables

### Surprising Finding: Content Ecosystem

Monday Mandala and Creative Kids Color expand well beyond coloring:
- Cursive worksheets (26 letters A-Z)
- Trivia games
- Party planning ideas
- Printable wrapping paper
- Word puzzles

This suggests a broader "kids printables" ecosystem rather than pure coloring focus.

### Schema Recommendation

Created `projects/coloring-prepub/validation/topic_sources/schema_recommendations.md` with:
- SQLite schema capturing multi-dimensional taxonomy
- Fields: category, subcategory, audience, difficulty, is_licensed, seasonality, status
- Indexes for common query patterns

### Implications for Creative Color Labs

1. **Topic database needs multiple dimensions** - Not just a flat category list
2. **Licensed content requires separate handling** - Legal considerations + different sourcing
3. **Content types beyond coloring are opportunities** - Worksheets, puzzles, templates
4. **Mindfulness/adult coloring is an underserved niche** - Only one site had dedicated category

---

## 2025-12-10: Prompt Context Detection for Skill Enforcement (h1)

**Tested whether UserPromptSubmit hooks can detect debugging context via keywords.**

### Experiment Setup

Created hook script that triggers on high-confidence debugging keywords:
- error, bug, broken, failing, doesn't work, not working, crash, exception

### Results Summary

| Category | Test Cases | Result |
|----------|------------|--------|
| True Positives | 6 (failing, bug, crash, doesn't work, broken, exception) | 6/6 triggered ✅ |
| True Negatives | 8 (add feature, refactor, questions, read file) | 8/8 no trigger ✅ |
| False Positives | 4 (error handling, error case, error message, log errors) | All triggered ❌ |

**Precision:** 60% (6/10) - Below 80% target
**False Positive Rate:** 33% (4/12) - Above 20% target

### Key Finding: "Error" Keyword is Ambiguous

The word "error" appears in both:
- **Debugging contexts:** "there is an error in the function"
- **Implementation contexts:** "add error handling", "handle the error case"

This causes false positives when the user is asking to IMPLEMENT error handling, not debug an existing error.

### High-Precision Keywords

These keywords had 100% precision (no false positives):
- bug, broken, failing, crash, exception, "doesn't work", "not working"

The keyword "error" should be downgraded from high-confidence or require pattern matching.

### Pattern for Improvement

Instead of simple keyword detection, use pattern exclusion:
```python
if "error" in prompt:
    if any(phrase in prompt for phrase in ["error handling", "error message", "error case", "log error"]):
        # Skip - implementation context
    else:
        # Trigger - likely debugging
```

### Implications

1. **Simple keyword matching insufficient** - Need pattern/phrase matching for ambiguous terms
2. **Risk of over-triggering confirmed** - 33% FP rate would cause hook fatigue
3. **Two-tier approach viable** - Use high-precision keywords for automatic trigger, others for soft reminders
4. **h3 hypothesis worth testing** - Combined keyword + context analysis likely needed

---

## 2025-12-10: TDD Keyword Detection (h2)

**Tested whether implementation keywords indicate TDD context.**

### Experiment Setup

Tested high-confidence keywords: implement, add feature, create function, write code, build

### Results

| Prompt | Triggered | Should Trigger |
|--------|-----------|----------------|
| "Implement a retry mechanism" | ✅ Yes | Yes |
| "Add a feature to export data as CSV" | ❌ No | Yes |
| "Create a function to validate emails" | ❌ No | Yes |
| "Write code for the authentication module" | ✅ Yes | Yes |
| "Build the user dashboard" | ✅ Yes | Yes |
| "Make a helper function" | ❌ No | Yes |
| "Add a logout button to the navbar" | ❌ No | Yes |
| "Write a test for the login function" | ✅ No | No |

**Recall:** 33% (3/9 implementation prompts detected)
**Precision:** 100% (when triggered, always correct)

### Key Finding: Phrase Matching Too Rigid

The keyword "add feature" doesn't match "add **a** feature". Exact phrase matching fails when users naturally insert articles or modifiers.

### Implications

1. High-confidence keywords have good precision but poor recall
2. Need pattern-based matching for flexibility (see h3)
3. Medium-confidence words (add, create, make) needed for better coverage

---

## 2025-12-10: Pattern-Based Context Detection (h3)

**Tested whether combined keyword + context analysis improves accuracy.**

### Approach

Instead of single keywords, use regex patterns:
- "X is broken" → debugging
- "add X to Y" → implementation
- "(handle|add|log) error" → NOT debugging (implementation context)

### Results Comparison

**TDD Detection:**
| Metric | v1 (keywords) | v2 (patterns) |
|--------|---------------|---------------|
| Recall | 33% | 89% |
| Precision | 100% | 100% |

**Debugging Detection:**
| Metric | v1 (keywords) | v2 (patterns) |
|--------|---------------|---------------|
| Precision | 60% | 100% |
| Recall | 100% | 75%* |

*Minor recall loss: "crashes" not matched by `\bcrash\b`

### Effective Patterns Discovered

**Implementation (TDD triggers):**
```python
r'\b(implement|build)\s+\w'           # implement/build X
r'\badd\s+(a|the|new)?\s*\w+\s+(to|for)'  # add X to Y
r'\bcreate\s+(a|new)?\s*\w+'          # create X
r'\bmake\s+(a|the)?\s*\w+'            # make X
r'\bwrite\s+(code|a\s+function)'      # write code/function
```

**Debugging (with exclusions):**
```python
r'\b(is|are)\s+(broken|failing|not working)'  # X is broken
r'there\s+(is|are)\s+a?\s*(bug|error)'        # there is a bug
r'(getting|seeing)\s+an?\s*(error|exception)'  # getting error
# EXCLUDE: r'(handle|add|log)\s+.{0,20}error'  # implementation context
```

### Key Finding: Pattern Matching Works

The h3 hypothesis is **CONFIRMED**. Pattern-based detection dramatically outperforms keyword matching:
- Eliminated false positives from "add error handling"
- Captured "add a feature" that keyword matching missed
- Flexible enough for natural language variation

### Recommendation

Implement pattern-based UserPromptSubmit hook for skill enforcement. The precision/recall tradeoffs are acceptable for production use.

---

## 2025-12-11: Hook Latency Impact Testing (06_latency_impact)

**Tested whether enforcement hooks add unacceptable latency to tool calls.**

### Hypotheses Tested

| ID | Statement | Hypothesized | Actual | Result |
|----|-----------|--------------|--------|--------|
| h1 | Python hooks add ~50-100ms startup overhead | 50-100ms | **27ms mean** | Much better |
| h2 | File I/O (state files) adds ~10-50ms | 10-50ms | **4-5ms** | Much better |
| h3 | Content analysis adds ~50-100ms for typical files | 50-100ms | **1-4ms** | Much better |
| h4 | Cumulative latency stays under 300ms | <300ms | **~31ms** | ✅ 10x margin |

### Benchmark Results (100 runs each)

**Python vs Bash Baseline:**
| Hook Type | Mean | P95 | Max |
|-----------|------|-----|-----|
| Python (empty) | 26.5ms | 37.7ms | 333.8ms |
| Bash (empty) | 5.9ms | 8.0ms | 171.5ms |

**State File I/O Overhead:**
| Variant | Mean | Overhead vs No I/O |
|---------|------|-------------------|
| No I/O | 23.7ms | baseline |
| Read only | 28.6ms | +4.9ms |
| Read + Write | 27.9ms | +4.2ms |

**Content Analysis (regex patterns):**
| Content Size | Mean | Overhead vs Baseline |
|--------------|------|---------------------|
| Small (minimal) | 28.2ms | +1.7ms |
| Medium (~100 lines) | 27.1ms | +0.6ms |
| Large (~1000 lines) | 30.2ms | +3.7ms |

### Key Findings

**1. Python interpreter overhead is ~21ms, not 50-100ms**
- Modern SSD and OS caching make Python startup fast
- The 50-100ms estimate was too pessimistic

**2. File I/O is negligible (~4-5ms)**
- SSD performance and OS file caching help significantly
- Even read+write state files add minimal latency

**3. Content analysis (regex) is extremely fast (~1-4ms)**
- Python's `re` module is highly optimized
- File size has minimal impact for typical files (100-1000 lines)
- Even 11 regex patterns add barely measurable overhead

**4. Cumulative latency well under targets**
- Estimated total: ~31ms per Edit call with all hooks
- Target was <300ms, actual is 10x better
- User perception target (<500ms) easily met

### Patterns Discovered

**Pattern: Hook latency is not a concern (90% confidence)**
- Python hooks average ~27ms, bash ~6ms
- Even with state I/O and regex content analysis, cumulative stays under 35ms
- Enforcement hooks can be used without performance worry

**Pattern: Bash hooks 4x faster than Python (85% confidence)**
- Bash: ~6ms vs Python: ~27ms
- For simple path-based checks, bash may be preferable
- For content analysis, Python is necessary anyway

### Implications

1. **No optimization needed** - Hooks are fast enough as-is
2. **Can add multiple enforcement hooks** - Even 5+ hooks would stay under 200ms
3. **Content analysis is free** - Can do extensive regex matching without worry
4. **State files are viable** - Can track TDD state, recent operations, etc.
5. **Skip the optimization strategies** - The test plan's "if_too_slow" section is not needed

### Recommended Architecture

Based on these results, the full enforcement stack is viable:
- UserPromptSubmit: prompt context detection (~27ms)
- PreToolUse (Edit): file path + content analysis (~30ms)
- PreToolUse (Edit): TDD state tracking with file I/O (~32ms)
- **Total per Edit: ~90ms** (well under 300ms target)

---

## 2025-12-11: Skill Discipline Deprecation Analysis (07_skill_discipline_deprecation)

**Analyzed whether hooks can replace the skill-discipline skill entirely.**

### Context

The skill-discipline skill enforces skill usage via prompting:
- "BEFORE responding to ANY user message, complete this checklist..."
- Lists rationalizations to watch for
- Requires TodoWrite for skill checklists
- Requires announcing skill usage

Problem: Prompts can be ignored. Hooks provide enforcement.

### Hypotheses Tested

| ID | Statement | Result |
|----|-----------|--------|
| h1 | Hooks cover main failure modes of skill-discipline | ✅ SUPPORTED |
| h2 | Some discipline aspects can't be replaced by hooks | ✅ SUPPORTED |
| h3 | Hybrid approach is optimal | ✅ SUPPORTED |

### H1: Failure Mode Coverage

The three main failure modes and how hooks address them:

| Failure Mode | Prompt Approach | Hook Approach | Improvement |
|--------------|-----------------|---------------|-------------|
| Forgetting to check | Voluntary checklist | Automatic detection | Major |
| Rationalizing | Self-awareness | External reminder | Major |
| "Too simple" to need skill | Listed warning | Objective patterns | Major |

**Finding:** Hooks cover all three failure modes more effectively than prompts through automatic detection, external reminders, and objective pattern matching.

### H2: Unreplaceable Aspects

| Aspect | Hook Capability | Loss Assessment |
|--------|-----------------|-----------------|
| Announcing skill usage | Can detect, can't force | Acceptable (redundant with UI) |
| TodoWrite for checklists | Can remind, can't enforce | Mitigable with strong reminder |
| Following skill exactly | Can enforce mechanics | Fundamental limitation (~80% value) |

**Key insight:** Hooks enforce mechanics (file paths, content patterns, workflow order), not semantics (did I fully investigate?). But mechanics is ~80% of enforcement value.

### H3: Optimal Architecture

Compared three approaches:

| Aspect | Hooks-Only | Current (skill-discipline) | Hybrid |
|--------|------------|---------------------------|--------|
| Detectable skills | ✅ Auto | ⚠️ Manual | ✅ Auto |
| Non-detectable skills | ❌ | ✅ | ✅ |
| Rationalization prevention | ✅ | ⚠️ | ✅ |
| Context cost | Low | High | Low |
| Checklist fatigue | None | High | Low |
| TodoWrite reminder | ❌ | ✅ | ✅ |

**Recommended hybrid architecture:**
1. **Hooks** - Automated enforcement for detectable patterns (debugging, TDD, file paths, content)
2. **Minimal reminder** - Only non-detectable skills (project-discovery, journal-discipline)
3. **CLAUDE.md** - General guidance that applies always (moved from skill-discipline)

### Proposed Minimal Reminder

```
📚 Most skills are enforced via hooks. For cases hooks can't detect:
- **project-discovery** - New project design
- **journal-discipline** - Search journal for complex work

If invoking a skill with a checklist, create TodoWrite items.
```

vs current 27-line reminder that lists all skills and full protocol.

### Migration Plan

1. **Phase 1 (Now):** Document hybrid architecture ✅
2. **Phase 2:** Implement minimal reminder, upgrade detect-skill-context.py to v2
3. **Phase 3:** Run hybrid for 1 week, track compliance
4. **Phase 4:** Deprecate skill-discipline, move to `_deprecated/`

### Rollback Criteria

- Compliance drops > 30%
- False positive rate > 25%
- Non-detectable skills frequently skipped
- User complaints about missing guidance

### Patterns Discovered

**Pattern: Hybrid enforcement beats pure prompts or pure hooks (85% confidence)**
- Hooks for detectable patterns + minimal reminder for non-detectable + CLAUDE.md for guidance
- Gives enforcement where possible, coverage for gaps, and low context cost

**Pattern: Hooks enforce mechanics, not semantics (90% confidence)**
- Can enforce observable patterns (file paths, content, workflow order)
- Can't verify semantic compliance (did I fully investigate?)
- Mechanics is ~80% of enforcement value

### Implications

1. **skill-discipline can be deprecated** - After validation period
2. **Minimal reminder is sufficient** - For non-detectable skills only
3. **CLAUDE.md gets skill guidance** - General principles live there
4. **Audit trail improves** - Hook logs vs "did I do the checklist?"

---

## 2025-12-11: Session Continuity Patterns (session_continuity test plan)

**Evaluated /start command, progress.json, /checkpoint command, and JSON vs YAML reliability.**

### Test Plan Summary

The session_continuity test plan was inspired by claude-harness (panayiotism/claude-harness), which uses:
- `/start` command for structured session initialization
- `progress.json` for state tracking across sessions
- `/checkpoint` for mid-session commits + PR management
- JSON over Markdown for state (claimed to be less prone to corruption)

### Hypotheses Tested

| ID | Hypothesis | Result | Confidence |
|----|------------|--------|------------|
| h1 | /start command reduces context-gathering time | **Incremental value** | Medium |
| h2 | progress.json improves cross-session continuity | **Complementary to journal** | Medium |
| h3 | /checkpoint reduces friction for frequent commits | **Main value is progress discipline** | Medium |
| h4 | JSON is more reliable than YAML for state files | **Insufficient data** | Low |

### H1: /start Command Value

**Finding:** The /start command provides incremental (not transformative) value.

What it automates:
1. Git status check
2. Journal search for recent entries
3. progress.json loading
4. PR and branch status

These are things we already do manually. The value is:
- **Consistency** - Every session starts the same way
- **Reduced cognitive load** - Single command vs remembering all steps
- **Ensures nothing forgotten** - Uncommitted work, blockers, etc.

**Caveat:** SessionStart hook already provides skill reminders. The /start command is complementary but not essential.

### H2: progress.json vs Journal

**Key Insight:** progress.json and journal serve different purposes.

| Aspect | progress.json | Journal |
|--------|--------------|---------|
| Purpose | State tracking | Insight capture |
| Content | Tasks, blockers, next steps | Learnings, feelings, discoveries |
| Query | Structured read | Semantic search |
| Update | Per session | Continuous |

**Finding:** They are complementary, not redundant. progress.json tracks "what happened" while journal tracks "what I learned."

**Problem discovered:** progress.json wasn't updated after Dec 10 despite 20+ commits. This indicates a discipline problem - the file only works if kept current.

### H3: /checkpoint Value

**Key Insight:** /checkpoint's main value is not commit friction reduction (git-operations subagent already handles that). Its value is **forcing progress.json updates**.

By tying progress.json updates to commits, /checkpoint solves the discipline problem discovered in h2. The workflow becomes:
1. Update progress.json (summary, tasks, blockers)
2. Run verification
3. Commit and push
4. PR management

Without this coupling, progress.json becomes stale.

### H4: JSON vs YAML Reliability

**Finding:** Insufficient data for a definitive answer.

Theoretical analysis:
- **JSON advantages:** Stricter syntax (fail-fast on errors), no indentation sensitivity
- **YAML advantages:** More readable, comments allowed, multiline strings natural

**Recommendation:** Use the right format for the job:
- JSON for machine state (progress.json) - strictness prevents subtle bugs
- YAML for human-authored configs (test plans, skills) - readability helps

The claim "models are less likely to corrupt JSON" is plausible but unproven in our limited testing.

### Patterns Discovered

**Pattern: Progress file + commit coupling (70% confidence)**
- State files (progress.json) become stale without discipline
- Coupling updates to commits (via /checkpoint) ensures currency
- The commit workflow acts as a natural reminder

**Pattern: State vs insights separation (75% confidence)**
- Structured state (JSON) for "what happened" - tasks, status, next steps
- Unstructured insights (journal) for "what I learned" - discoveries, feelings
- Different query patterns: structured read vs semantic search

### Implications

1. **/start is nice-to-have** - Use for consistency, but SessionStart hook covers critical reminders
2. **/checkpoint solves the discipline problem** - Main value is progress.json updates, not git
3. **progress.json complements journal** - They serve different purposes
4. **Consider automation** - Stop hook could prompt for /checkpoint if progress.json is stale

### Recommendations

1. **Adopt progress.json + /checkpoint pattern** - For projects needing cross-session state
2. **Don't replace journal** - Keep both for their different purposes
3. **Use JSON for state, YAML for config** - Match format to purpose
4. **Add stale detection** - Hook reminder if progress.json > 24h old
