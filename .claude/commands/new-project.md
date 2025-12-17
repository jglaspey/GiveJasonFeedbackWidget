---
description: Design a new business process project with guided discovery
argument-hint: [project-name]
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion
---

# New Project: Guided Discovery

You are helping design a new business process project through structured discovery.

## Project Name

**Argument provided:** $ARGUMENTS

If no project name provided, ask for one before proceeding.

## Reference Skill

**For the full methodology**: Invoke the `project-discovery` skill or read `.claude/skills/project-discovery/SKILL.md`

## The Three Phases

1. **Discovery** - Understand purpose, current process, inputs, outputs, constraints
2. **Brainstorming** - Explore approaches for uncertain steps
3. **Validation** - Prove out risky assumptions with test scripts

## Output

A validated `project_spec.md` that documents what we're building and confirms the approach is feasible. Implementation planning (including scaffolding) is the next step after discovery.

## Starting Point

First, create the discovery directory:

```
projects/<name>/
├── project_spec.md
└── validation/
    └── .gitkeep
```

Then ask: "Where would you like to start?"

| Starting Point | What It Means |
|----------------|---------------|
| **From scratch** | Full discovery - we'll work through all phases |
| **I have requirements** | Skip discovery, start at brainstorming |
| **I know the approach** | Skip to validation of specific assumptions |

## Phase Guidelines

### Discovery
- Ask ONE question at a time
- Offer multiple choice when possible
- After each section, write to `project_spec.md` and validate: "Does this capture it correctly?"
- **Reference**: `references/discovery.md`

### Brainstorming
- For each uncertain step, propose 2-3 approaches
- Lead with your recommendation and reasoning
- Document chosen approach in spec
- Flag items that need validation
- **Reference**: `references/brainstorming.md`

### Validation
- Write test scripts to `projects/<name>/validation/`
- Keep scripts simple and focused on one assumption
- Record results in `validation/results.md`
- Update spec with validation outcomes
- **Reference**: `references/validation.md`

## Spec Template

Build this incrementally during discovery:

```markdown
# [Project Name]

## Purpose
[What this workflow accomplishes]

## Current Process
[Manual steps being replaced, if any]

## Inputs
- **Source**: [Where data comes from]
- **Format**: [Data format]
- **Volume**: [How much data]
- **Frequency**: [How often]

## Outputs
- **Result**: [What gets produced]
- **Format**: [Output format]
- **Destination**: [Where it goes]

## Constraints
- [Cost limits, rate limits, tool requirements, compliance needs]

## Workflow Steps

### Step 1: [Name]
**Goal**: [What this step accomplishes]
**Approach**: [Chosen method]
**Rationale**: [Why this approach]

[Repeat for each step]

## Validation Results
| Assumption | Tested | Result | Impact |
|------------|--------|--------|--------|
| [assumption] | [yes/no] | [outcome] | [decision] |

## Open Questions
- [Anything still uncertain]
```

## Key Principles

1. **One question at a time** - Don't overwhelm
2. **Multiple choice preferred** - Reduce cognitive load
3. **Lead with recommendations** - Be opinionated, provide escape hatches
4. **Validate incrementally** - Check each section before moving on
5. **Prove before committing** - Test risky assumptions

## After Completion

When discovery is complete:
1. Summarize the validated spec
2. Note any open questions that remain
3. Explain that the next step is implementation planning
4. Offer to help with that when ready
