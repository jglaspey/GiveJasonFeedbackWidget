# Persuasion Principles for Skill Design

LLMs respond to the same persuasion principles as humans. Understanding this helps you design more effective skills - not to manipulate, but to ensure critical practices are followed even under pressure.

**Research foundation:** Meincke et al. (2025) tested 7 persuasion principles with N=28,000 AI conversations. Persuasion techniques more than doubled compliance rates (33% → 72%).

## Key Principles for Skills

### Authority
Deference to expertise, credentials, or official sources.

**How to use:**
- Imperative language: "YOU MUST", "Never", "Always"
- Non-negotiable framing: "No exceptions"
- Eliminates decision fatigue and rationalization

```markdown
# ❌ Weak
Consider writing tests first when feasible.

# ✅ Strong
Write code before test? Delete it. Start over. No exceptions.
```

### Commitment
Consistency with prior actions or public declarations.

**How to use:**
- Require announcements: "Announce skill usage"
- Force explicit choices
- Use TodoWrite for checklists

```markdown
# ❌ Weak
Consider letting your partner know which skill you're using.

# ✅ Strong
When you use a skill, you MUST announce: "I'm using [Skill Name]"
```

### Social Proof
Conformity to what others do or what's normal.

**How to use:**
- Universal patterns: "Every time", "Always"
- Failure modes: "X without Y = failure"

```markdown
# ❌ Weak
Some people find TodoWrite helpful for checklists.

# ✅ Strong
Checklists without TodoWrite tracking = steps get skipped. Every time.
```

## Closing Loopholes

Don't just state rules - forbid specific workarounds:

```markdown
# ❌ Leaves loopholes
Write code before test? Delete it.

# ✅ Closes loopholes
Write code before test? Delete it. Start over.

**No exceptions:**
- Don't keep it as "reference"
- Don't "adapt" it while writing tests
- Don't look at it
- Delete means delete
```

## Spirit vs Letter

Add this phrase early to cut off "spirit" rationalizations:

```markdown
**Violating the letter of the rules is violating the spirit of the rules.**
```

## Rationalization Tables

Capture excuses from testing and add explicit counters:

```markdown
| Excuse | Reality |
|--------|---------|
| "Too simple to test" | Simple code breaks. Test takes 30 seconds. |
| "I'll test after" | Tests passing immediately prove nothing. |
```

## Red Flags Lists

Make it easy to self-check when rationalizing:

```markdown
## Red Flags - STOP and Start Over

- Code before test
- "I already manually tested it"
- "Just this once"
- "This is different because..."

**All of these mean: Delete code. Start over.**
```

## When to Use Each Principle

| Skill Type | Use | Avoid |
|------------|-----|-------|
| Discipline-enforcing | Authority + Commitment + Social Proof | Liking |
| Guidance/technique | Moderate Authority | Heavy authority |
| Reference | Clarity only | Persuasion |

## Ethical Use

**Legitimate:** Ensuring critical practices are followed, preventing predictable failures

**Illegitimate:** Manipulation, false urgency, guilt-based compliance

**The test:** Would this serve the user's genuine interests if they fully understood it?
