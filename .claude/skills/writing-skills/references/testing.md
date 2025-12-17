# Testing Skills with TDD

**Source**: Jesse Vincent's approach to skill development

## Evidence

The learning framework at `learning_framework/` provides infrastructure for testing skills:
- `run_experiment.py` - Runs prompts against skills and captures behavior
- `record_experiment.py` - Records results to knowledge_base.db
- `knowledge_base.db` - Stores patterns, experiments, and gotchas with confidence scores

See Pattern #1: "Explicit skill name always works" (0.95 confidence) as baseline for testing.

## The Problem

Skills often fail silently:
- Claude doesn't invoke the skill when it should
- Claude invokes but ignores parts of the skill
- Claude "wings it" based on the description alone

## TDD for Skills

### 1. Write Tests First

Before creating the skill, define test prompts:

```markdown
## Test Prompts for [skill-name]

### Should Invoke
- "Help me with [specific task]"
- "I need to [domain action]"
- "[Domain keyword] in my [context]"

### Should NOT Invoke
- "Help me with [unrelated task]"
- Generic requests without domain keywords
```

### 2. Measure Baseline

Run test prompts WITHOUT the skill:
- Record Claude's default behavior
- Note what's missing from desired behavior
- Identify the gap the skill should fill

### 3. Create Minimal Skill

Write skill targeting identified gaps:
- Focus on "when to use" clarity first
- Add just enough content to fill the gap
- Don't over-engineer on first iteration

### 4. Test and Iterate

Run same test prompts WITH the skill:

```bash
# Using the learning framework runner
cd learning_framework
python3 run_experiment.py "Your test prompt" --workspace path/to/workspace
```

Check:
- Was skill invoked? (look for Skill tool call)
- Did Claude read the skill body?
- Did Claude follow the instructions?

### 5. Find Rationalizations

When skill isn't invoked, Claude has rationalized why not. Common patterns:

| Rationalization | Fix |
|-----------------|-----|
| "I can do this without a skill" | Make description more specific |
| "This doesn't match the skill" | Add more trigger scenarios |
| "The skill is for something else" | Clarify "when to use" section |

### 6. Iterate Until Compliant

Target: 90%+ invocation rate on test prompts

Each iteration:
1. Adjust description keywords
2. Clarify when-to-use section
3. Test again
4. Record what worked/didn't

## Recording Results

Use the learning framework to track experiments:

```bash
cd learning_framework

# Record an experiment
python3 record_experiment.py \
    --feature your_skill_name \
    --hypothesis "Description with X triggers invocation" \
    --prompt "Test prompt used" \
    --expected invoked \
    --actual invoked|not_invoked \
    --notes "Observations"

# Record a pattern discovered
python3 record_experiment.py \
    --add-pattern \
    --feature your_skill_name \
    --pattern-name "Pattern name" \
    --description "What you learned" \
    --confidence 0.8
```

## Compliance Checklist

Before considering a skill complete:

- [ ] Description uses "when" framing, not "what" framing
- [ ] Description contains domain-specific keywords
- [ ] Tested with 3+ prompts that should trigger
- [ ] Tested with 2+ prompts that should NOT trigger
- [ ] 90%+ invocation rate achieved
- [ ] Claude reads skill body (not just description)
- [ ] Claude follows instructions in skill

## Security Note

From Jesse Vincent:

> "Skills are prompt injection by design"

Any scripts in `scripts/` can run arbitrary code. This is intentional power, but:
- Review scripts before adding to skills
- Don't include skills from untrusted sources
- Be aware that skill content influences Claude's behavior
