---
name: Project Discovery
description: When designing a new workflow before implementation, understanding requirements for a business process, or validating feasibility of uncertain approaches
---

# Project Discovery

A structured methodology for understanding and validating business process workflows before building them.

## When to Use This Skill

- Starting a new project via `/new-project` command
- Designing a workflow before implementation
- Validating that an approach is feasible before committing

## The Three Phases

### Phase 1: Discovery
Understand what we're building through conversational questions.

**For discovery question patterns**: Read `references/discovery.md`

### Phase 2: Brainstorming
Explore approaches for each step, especially uncertain ones.

**For brainstorming patterns**: Read `references/brainstorming.md`

### Phase 3: Validation
Prove out risky assumptions before committing.

**For validation patterns**: Read `references/validation.md`

## What Comes Next

After discovery completes, you have a validated `project_spec.md`. The next step is **implementation planning**, which includes scaffolding the project structure. That's a separate concern handled by a planning workflow.

## Key Principles

### One Question at a Time
Don't overwhelm with lists of questions. Ask one, listen, ask the next based on the answer. More conversational, less interrogation.

### Multiple Choice When Possible
Reduces cognitive load. Instead of "What are your inputs?" offer options:
- Files you already have
- An API
- Web scraping/search
- Manual entry

### Lead with Recommendation
During brainstorming, don't present equal options. Say "I'd recommend X because Y, but we could also do Z if [conditions]." Opinionated with escape hatches.

### Build Spec Incrementally
Don't dump a complete spec at the end. Build sections as you go, validate each: "Here's what I understand about the purpose - does this look right?"

### Prove Before Committing
If a step depends on an assumption (API has the data, CLI tool exists, etc.), test it before building the full workflow.

## Artifacts

### Discovery Scaffold
Created at start of discovery:
```
projects/<name>/
├── project_spec.md      # Built incrementally
└── validation/          # Feasibility scripts
```

### project_spec.md Structure
```markdown
# [Project Name]

## Purpose
[What this workflow accomplishes]

## Current Process
[Manual steps if replacing existing process]

## Inputs
[Data sources, formats, locations]

## Outputs
[Expected results, formats, destinations]

## Constraints
[Cost limits, rate limits, tool requirements]

## Workflow Steps
[Each step with chosen approach]

## Validation Results
[What we tested and learned]

## Open Questions
[Anything still uncertain]
```

## Skipping Phases

Not every project needs all three phases. At the start, ask:
- "Where do you want to start?"
  - From scratch (full discovery)
  - I have requirements (skip to brainstorming)
  - I know the approach (skip to validation)

## Related Skills

- **agent-project-setup**: Which patterns to apply when building
- **directory-structure**: Project layout patterns
- **path-management**: Machine-agnostic paths
