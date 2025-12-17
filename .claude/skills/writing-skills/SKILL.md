---
name: writing-skills
description: When creating new skills for Claude Code, documenting reusable workflows, or systematizing techniques that Claude should discover and apply automatically
---

# Writing Effective Claude Code Skills

**Writing skills IS Test-Driven Development applied to process documentation.**

Skills are markdown files that extend Claude's capabilities. If you didn't test with a subagent, you don't know if the skill teaches the right thing.

## When to Use This Skill

- Creating a new skill for a repeatable workflow
- Converting ad-hoc knowledge into a discoverable skill
- Improving an existing skill's invocation rate or effectiveness

## Quick Start

```
.claude/skills/your-skill-name/
├── SKILL.md              # Entry point (required)
└── references/           # Detailed docs (optional)
    ├── topic1.md
    └── topic2.md
```

## The Iron Law

```
NO SKILL WITHOUT A FAILING TEST FIRST
```

Write skill before testing? Delete it. Start over.

This applies to NEW skills AND EDITS to existing skills. Same discipline as TDD for code.

## Validated Best Practices

### 1. Description: Tell "When", Not "What"
**For descriptions**: Read `references/descriptions.md`

```yaml
# ❌ What it does (45% invocation rate)
description: Processes CSV files by reading, validating, and transforming data

# ✅ When to use (85% invocation rate)
description: When you need to convert CSV data to JSON or validate tabular formats
```

### 2. Use Domain-Specific Keywords
**For keyword selection**: Read `references/descriptions.md`

```yaml
# ❌ Generic (40% invocation)
description: When you need to analyze and review data for issues

# ✅ Specific (95% invocation)
description: When you need to identify anomalies in billing reconciliation workflows
```

### 3. Descriptive Naming
Use active voice, verb-first with hyphens:
- `writing-skills` not `skill-writer`
- `systematic-debugging` not `debug-helper`
- `condition-based-waiting` not `async-test-utils`

### 4. Progressive Disclosure
**For structuring large skills**: Read `references/structure.md`

```markdown
# In SKILL.md
**For database setup**: Read `references/database.md`
**For API integration**: Read `references/api.md`
```

Reduces token usage by ~70% compared to flat skills.

### 5. Bulletproof Discipline Skills
**For making skills resist rationalization**: Read `references/persuasion-principles.md`

Skills that enforce discipline need to close loopholes explicitly and address rationalizations.

## Reference Files

**For writing descriptions that trigger invocation**: Read `references/descriptions.md`
**For file structure and organization**: Read `references/structure.md`
**For testing skills with TDD approach**: Read `references/testing.md`
**For making skills resist rationalization**: Read `references/persuasion-principles.md`

## Anti-Patterns

1. **Generic verbs in descriptions** - "review", "analyze", "check" don't trigger skills
2. **Flat mega-skills** - Put everything in SKILL.md wastes tokens
3. **Implicit reference organization** - "See references/" doesn't work as well as explicit mapping
4. **Describing implementation** - Descriptions should describe scenarios, not steps
5. **Untested skills** - Skills without subagent testing have loopholes. Always.

## Related Skills

- **test-driven-development** - Same discipline, applied to code
