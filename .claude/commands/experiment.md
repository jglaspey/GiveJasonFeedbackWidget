---
description: Run a learning framework experiment from a test plan
argument-hint: [test-plan-name] [hypothesis-id]
allowed-tools: Read, Bash, Grep, Glob, Write, Edit
---

# Run Learning Framework Experiment

You are helping run a structured experiment from the learning framework.

## Context

- Test plans location: `learning_framework/test_plans/`
- Experiment runner: `learning_framework/run_experiment.py`
- Record results: `learning_framework/record_experiment.py`
- Knowledge base: `learning_framework/knowledge_base.db`
- Learnings log: `learning_framework/LEARNINGS.md`
- **Tester workspace:** `learning_framework/tester_workspace/`

## IMPORTANT: Use tester_workspace for Claude Config Tests

When testing ANY Claude Code configuration, use the tester_workspace which has its own git repo for isolation.

| Config Type | Create in tester_workspace |
|-------------|---------------------------|
| Hooks | `.claude/hooks/*.py` + `.claude/settings.json` |
| Skills | `.claude/skills/*/SKILL.md` |
| Commands | `.claude/commands/*.md` |
| Agents | Define in `.claude/settings.json` |
| MCP servers | `.claude/mcp.json` |
| CLAUDE.md | `.claude/CLAUDE.md` |
| Permissions | `.claude/settings.json` |

**Why it works:** The `add_dirs=[tester_workspace]` option tells the SDK to load `.claude/` configs from that directory, including hooks from `settings.json`. No nested git repo needed.

### Testing Workflow

```bash
# 1. Set up config in tester_workspace
cd learning_framework/tester_workspace/.claude/
# Create/edit hooks/, skills/, commands/, settings.json, etc.

# 2. Quick validation (for hook scripts)
echo '{"tool_input": {"file_path": "tests/test_example.py"}}' | .claude/hooks/your-hook.py

# 3. Clear marker file and run integration test
rm -f /tmp/hook_fired_marker.txt
cd learning_framework
python3 test_with_proxy.py --no-proxy "Your test prompt here"

# 4. Verify hooks fired
cat /tmp/hook_fired_marker.txt
```

### Verifying Hooks Fire (CRITICAL)

**Hook stdout is NOT visible in SDK message stream.** To verify hooks executed:

1. **Marker file approach (recommended)**: Add to your hook:
   ```python
   with open('/tmp/hook_fired_marker.txt', 'a') as f:
       f.write(f"Hook fired at {time.time()}\n")
   ```
2. **Direct test**: Pipe JSON to hook script directly
3. **Behavioral observation**: Look for changes in Claude's response

### Using with claude-code-logger Proxy

You can combine workspace testing with the proxy to see full API traffic:

```bash
# Terminal 1: Start proxy
npx claude-code-logger start --verbose

# Terminal 2: Run test through proxy
rm -f /tmp/hook_fired_marker.txt
cd learning_framework
python3 test_with_proxy.py "Your test prompt here"

# Check hook fired
cat /tmp/hook_fired_marker.txt
```

The proxy shows system prompts, tool calls, and results - but NOT hook stdout (use marker file for that).

## Current test plans
!`ls -1 learning_framework/test_plans/*.yaml 2>/dev/null | xargs -I{} basename {} .yaml`

## Your Task

**Arguments provided:** $ARGUMENTS

### If no arguments provided:
1. List available test plans with their hypotheses
2. Ask which experiment to run

### If test plan name provided (e.g., `/experiment skill_creation`):
1. Read the test plan at `learning_framework/test_plans/$1.yaml`
2. List the hypotheses with their IDs
3. Ask which hypothesis to test

### If both test plan and hypothesis provided (e.g., `/experiment skill_creation h1`):
1. Read the test plan
2. Find the specified hypothesis
3. Design and run the experiment:
   - Set up any required test fixtures
   - Run the test using `run_experiment.py` if testing skill invocation
   - Or run manual tests as needed
4. Record results to knowledge_base.db using `record_experiment.py`
5. Update LEARNINGS.md if significant insights discovered
6. Suggest next steps

## Recording Results

After running an experiment, record it with:
```bash
cd learning_framework && python record_experiment.py \
    --feature FEATURE_NAME \
    --hypothesis "Hypothesis text" \
    --prompt "Test prompt used" \
    --expected invoked|not_invoked|uncertain \
    --actual invoked|not_invoked \
    --notes "Observations"
```

For patterns discovered:
```bash
cd learning_framework && python record_experiment.py \
    --add-pattern \
    --feature FEATURE_NAME \
    --pattern-name "Pattern name" \
    --description "What we learned" \
    --confidence 0.8
```

For gotchas discovered:
```bash
cd learning_framework && python record_experiment.py \
    --add-gotcha \
    --feature FEATURE_NAME \
    --title "Gotcha title" \
    --description "What went wrong" \
    --avoid "How to avoid it" \
    --severity low|medium|high|critical
```

## After Each Experiment

1. **Record to knowledge_base.db** - REQUIRED, use `record_experiment.py`
2. **Update LEARNINGS.md** - For significant discoveries
3. **Propose applications** - How should we apply this learning?

## Proposing Applications

After recording results, consider whether the learning suggests:

| Learning Type | Potential Application |
|--------------|----------------------|
| Skill invocation pattern | Update skill descriptions/keywords |
| Hook behavior | Create/modify hook scripts |
| Best practice | Add to existing skill or create new one |
| Gotcha/pitfall | Add to skill gotchas section |
| SDK pattern | Update agent-sdk-basics skill |
| Project structure | Update templates/business_process |
| New capability | Create new skill, agent, or command |

**Always ask:** "What concrete change to the harness would encode this learning?"

### Application Examples

- **"Explicit skill names work better"** → Update writing-skills with naming guidelines
- **"Hooks need settings.json"** → Add to settings-json-patterns skill
- **"Progressive disclosure works"** → Document pattern in writing-skills references
- **"Subagents can't ask for confirmation"** → Update agent definitions to note this
- **"JSON state files work for continuity"** → Add to sequential-processing skill

## Completing a Test Plan

When ALL hypotheses in a test plan have been tested:

1. Summarize findings in LEARNINGS.md
2. Move test plan to completed: `mv learning_framework/test_plans/NAME.yaml learning_framework/test_plans/completed/`
3. Propose harness improvements based on learnings
4. Create issues or TODOs for suggested changes

## Important

- Follow TDD principles: form hypothesis → test → record → analyze
- Only record ACTUAL results, not what you expected
- ALWAYS record to knowledge_base.db before moving on
- Be honest about confidence levels
- Propose concrete applications for every learning

## Known Issues

**Agent SDK doesn't hot-reload .claude configs:** If you modify `.claude/` files (hooks, settings.json, skills, etc.) in the tester_workspace, you must restart any running Agent SDK process for changes to take effect. The spawned Claude instance loads configs at startup.

**Workflow implication:** Set up ALL configs in tester_workspace BEFORE running `run_experiment.py`. If you need to modify configs mid-experiment, you'll need to run a fresh `run_experiment.py` call afterward.

**Hook output not visible in SDK:** The Agent SDK captures structured messages but not raw hook stdout. To verify hooks work:
1. Test script directly with piped JSON input
2. Look for behavioral changes in Claude's response (e.g., mentions TDD after implementation prompt)
3. Check if hook creates side effects (files, logs) that confirm execution
