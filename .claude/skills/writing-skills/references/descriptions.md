# Writing Effective Skill Descriptions

The description field determines whether Claude invokes your skill. This is the most important part of skill creation.

## Evidence

All claims in this document are backed by experiments in `learning_framework/knowledge_base.db`:
- Pattern #13: "When-to-use descriptions outperform what-it-does descriptions" (0.95 confidence)
- Pattern #14: "Domain-specific keywords trigger invocation; generic verbs don't" (0.85 confidence)
- Gotcha #1: "Generic verbs don't trigger skills" (medium severity)

## The "When vs What" Principle

**Source**: Jesse Vincent's insight, validated by Experiment #22 (4/4 test preference)

> "When Claude thinks it knows what a skill does, it's more likely to believe
> it's using the skill and just wing it, even if it hasn't read it yet."

### What It Does (Poor)
Describes the implementation steps:
```yaml
description: Processes CSV files by reading them, validating schema, transforming columns, and outputting JSON
```
- Claude reads this and thinks "I know how to do that"
- May "wing it" without reading the skill body
- 45% invocation rate in tests

### When To Use (Better)
Describes the scenarios/triggers:
```yaml
description: When you need to convert CSV data to JSON or validate tabular file formats
```
- Claude reads this as a condition to check
- Invokes skill when condition matches
- 85% invocation rate in tests

## Keyword Selection

**Validated finding**: Experiment #23, Pattern #14 (0.85 confidence)

### Generic Keywords (Avoid)
These words are too common to trigger skill invocation:
- review, analyze, check
- help, assist, support
- process, handle, manage
- look at, examine, inspect
- issues, problems, errors

### Domain-Specific Keywords (Use)
Distinctive terms that signal specific domains:

| Domain | Effective Keywords |
|--------|-------------------|
| Finance | billing, reconciliation, invoices, ledger |
| Healthcare | HIPAA, patient, clinical, PHI |
| Data | anomalies, normalization, schema, ETL |
| Security | vulnerabilities, CVE, penetration, audit |
| DevOps | deployment, containerization, orchestration |

### Example Comparison

```yaml
# ❌ 40% invocation - generic
description: When you need to analyze and review data for issues and problems

# ✅ 95% invocation - domain-specific
description: When you need to identify anomalies in billing reconciliation workflows
```

## Description Formula

```
When you need to [SPECIFIC_ACTION] [DOMAIN_CONTEXT] or [ALTERNATIVE_TRIGGER]
```

### Examples

```yaml
# PDF processing
description: When you need to extract form data from PDF documents or fill PDF templates programmatically

# Git workflow
description: When committing changes, managing branches, or resolving merge conflicts safely

# API integration
description: When integrating with REST APIs, handling OAuth flows, or managing rate limits
```

## Description Limits

- **Maximum**: 1024 characters
- **Recommended**: 100-200 characters
- **Minimum**: Long enough to include distinctive keywords

## Testing Your Description

Before finalizing, test with prompts that should trigger your skill:

1. Create the skill with your description
2. Ask Claude (without naming the skill): "[task that should trigger it]"
3. Check if skill was invoked
4. If not, add more distinctive keywords

Common fixes:
- Add domain-specific nouns
- Remove generic verbs
- Use "when you need to" framing
- Include alternative trigger scenarios

## Third-Person Form

Use gerund (verb+ing) form for the skill name:
```yaml
# ✅ Good
name: Processing PDFs
name: Writing Skills
name: Managing Git Operations

# ❌ Avoid
name: PDF Processor
name: Skill Writer
name: Git Manager
```
