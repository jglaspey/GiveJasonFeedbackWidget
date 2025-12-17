# Brainstorming Phase

Explore approaches for uncertain steps before committing.

## When to Brainstorm

Brainstorm when a step has:
- Multiple valid approaches with different tradeoffs
- Uncertainty about feasibility
- Dependencies on external systems (APIs, tools)
- Cost or performance implications

## The Pattern

For each uncertain step:

### 1. State the Challenge
"For [step], we need to [goal]. There are a few ways to approach this."

### 2. Present 2-3 Options
Lead with your recommendation:

"I'd recommend **Option A** because [reasons].

Alternatively:
- **Option B**: [description] - better if [condition]
- **Option C**: [description] - but [tradeoff]"

### 3. Discuss Tradeoffs
Be specific about:
- Reliability (how often will this work?)
- Cost (API fees, compute time)
- Complexity (how hard to build/maintain?)
- Speed (how long per item?)

### 4. Pick or Test
Either:
- Decide now if the choice is clear
- Flag for validation if uncertain

## Common Decision Points

### Data Acquisition
| Approach | Best When | Tradeoffs |
|----------|-----------|-----------|
| Direct API | Official API exists with needed data | Rate limits, auth complexity |
| Web scraping | No API, structured HTML | Fragile, may violate ToS |
| Agentic search | Need to aggregate from multiple sources | Slower, less deterministic |
| Existing files | Data already collected | May be stale |

### Data Processing
| Approach | Best When | Tradeoffs |
|----------|-----------|-----------|
| Python script | Complex transformations | More code to maintain |
| Claude processing | Unstructured to structured | Cost per item, slower |
| CLI tools | Standard formats (jq, csvkit) | Limited flexibility |

### Output Delivery
| Approach | Best When | Tradeoffs |
|----------|-----------|-----------|
| Local files | Analysis, archival | Manual distribution |
| API push | Integration with other systems | Auth, error handling |
| Email/notification | Human review needed | Not programmatic |

## Documenting Decisions

Update `project_spec.md` with chosen approaches:

```markdown
## Workflow Steps

### Step 1: Gather company data
**Approach**: Apollo API for initial list, agentic search for enrichment
**Rationale**: Apollo has structured data but limited fields; search fills gaps
**Validated**: [Yes/No - link to validation]

### Step 2: Filter by criteria
**Approach**: Python script with configurable rules
**Rationale**: Rules will change frequently, need flexibility
```

## When to Move to Validation

Move to validation when:
- An approach depends on an untested assumption
- You're choosing between options that seem equivalent
- The user expresses uncertainty ("I think the API can do this...")
- Stakes are high (lots of work depends on this working)
