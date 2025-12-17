# Skill File Structure

## Evidence

All claims in this document are backed by experiments in `learning_framework/knowledge_base.db`:
- Pattern #12: "Progressive disclosure reduces context by 70%+" (0.90 confidence)
- Pattern #7: "Claude follows explicit reference instructions" (0.90 confidence)
- Experiment #21: "Three-tier progressive disclosure reduces token usage"
- Experiment #25: "Explicit 'for X, read references/X.md' instructions work reliably"

## Directory Layout

```
.claude/skills/your-skill-name/
├── SKILL.md              # Entry point (required)
├── references/           # Detailed documentation
│   ├── topic1.md
│   └── topic2.md
├── scripts/              # Executable utilities (optional)
│   └── helper.py
└── assets/               # Templates, examples (optional)
    └── template.json
```

## SKILL.md Requirements

### YAML Frontmatter (Required)

```yaml
---
name: Skill Display Name        # Max 64 characters
description: When you need...   # Max 1024 characters, "when" framing
---
```

### Body Structure

```markdown
# Skill Title

Brief overview (1-2 sentences).

## When to Use This Skill

- Scenario 1
- Scenario 2

## Quick Reference

Key information for common cases.

## Reference Files

**For topic X**: Read `references/x.md`
**For topic Y**: Read `references/y.md`
```

## Progressive Disclosure Pattern

**Validated finding**: Experiment #21, Pattern #12 (0.90 confidence)

### Flat (Inefficient)
```
SKILL.md (400 lines)
├── Topic 1 content (100 lines)
├── Topic 2 content (150 lines)
└── Topic 3 content (150 lines)
```
All 400 lines loaded even when user needs only Topic 1.

### Tiered (Efficient)
```
SKILL.md (50 lines)
├── Entry point with explicit mapping
└── references/
    ├── topic1.md (100 lines)
    ├── topic2.md (150 lines)
    └── topic3.md (150 lines)
```
Only 50 + relevant topic loaded (~100-200 lines vs 400).

## Explicit Reference Mapping

**Validated finding**: Experiment #25, Pattern #7 (0.90 confidence)

```markdown
## Reference Files

**For database setup**: Read `references/database.md`
**For API integration**: Read `references/api.md`
**For testing patterns**: Read `references/testing.md`
```

This outperforms implicit organization like:
```markdown
See the references/ directory for detailed documentation.
```

## Size Guidelines (Opus 4.5)

**Validated finding**: Experiment #24, learning_framework/LEARNINGS.md "Skill Size Impact Testing"

| Component | Recommendation | Hard Limit |
|-----------|---------------|------------|
| SKILL.md body | Under 100 lines | 500 lines works |
| Individual reference | Under 150 lines | No limit observed |
| Total skill content | Any size | No limit observed |

The community "200 line degradation" claim was not observed on Opus 4.5.

## Scripts Directory

For executable utilities that support the skill:

```
scripts/
├── init_skill.py      # Initialize new skill structure
├── validate.py        # Validate skill format
└── test_invocation.py # Test skill triggers correctly
```

Reference scripts with explicit instructions:
```markdown
To create a new skill, run: `python scripts/init_skill.py {name}`
```

## Assets Directory

For templates, examples, and boilerplate:

```
assets/
├── skill_template.md   # Starter template
├── example_output.json # Expected output format
└── checklist.md        # Quality checklist
```
