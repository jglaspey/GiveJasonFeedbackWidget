# AI Agent Development Harness - Implementation Plan

## Vision

A two-tier development environment:
- **Parent (Dev Harness)**: Tools, skills, and workflows for building AI agents
- **Child (Business Process)**: Specific agent implementations with their own configurations

The dev harness uses autonomous learning to continuously improve its knowledge of Claude Code and Agent SDK features through TDD-style experimentation.

## Architecture Overview

```
agent_dev_harness/                    # DEV HARNESS (Parent)
├── .claude/
│   ├── CLAUDE.md                     # Development-focused instructions
│   ├── settings.json                 # Permissive for development
│   └── skills/                       # Skills for building agents
│       ├── claude-code-features/     # How to use Claude Code
│       ├── agent-patterns/           # Common agent patterns
│       ├── agent-project-setup/          # Best practices
│       └── git-operations/           # Version control
├── learning_framework/               # Autonomous learning system
│   ├── test_orchestrator.py         # Manages test instances
│   ├── test_plans/                   # What to learn
│   ├── test_results/                 # Structured findings
│   └── knowledge_base.db             # Accumulated learnings
├── templates/                        # Project templates
│   └── business_process/
│       ├── .claude/
│       ├── functional/               # Process logic
│       └── outputs/                  # Run-specific outputs
└── projects/                         # Active business processes
    └── example_process/              # BUSINESS PROCESS (Child)
        ├── .claude/
        │   ├── CLAUDE.md             # Process-specific instructions
        │   ├── settings.json         # Process-specific permissions
        │   └── mcp.json              # Process-specific tools
        ├── functional/
        │   ├── scripts/
        │   ├── prompts/              # Isolated prompts
        │   └── workers/              # Parallel processing
        └── outputs/
            ├── run_2025-01-15_143022/
            │   ├── logs/
            │   ├── results/
            │   └── errors/
            └── run_2025-01-15_150433/
```

## Phase 1: Foundation Setup

### 1.1 Directory Structure
- Create base directories as shown above
- Set up .gitignore patterns (outputs/, logs/, .env, etc.)
- Initialize git repository if needed

### 1.2 Base CLAUDE.md Creation
Adapt Obra's dotfile for agent development context:

**Keep from Obra:**
- Foundational rules (honesty, systematic work, no shortcuts)
- Relationship dynamics (honest feedback, pushing back)
- Code quality rules (YAGNI, minimal changes, no duplication)
- Testing requirements (TDD, pristine output)
- Debugging framework (root cause analysis)
- Version control discipline

**Adapt for agent development:**
- Add rules about isolating prompts from scripts
- Add rules about project structure (functional vs outputs)
- Add rules about using Agent SDK instead of API
- Add rules about resumability and logging
- Add rules about parallel processing patterns
- Add rules about machine-agnostic paths

### 1.3 Initial Settings.json
Create development-friendly settings with appropriate wildcards:
```json
{
  "allowed_tools": [
    "Bash(ls:*)",
    "Bash(cat:*)",
    "Read(*)",
    "Write(*)",
    "Edit(*)",
    "Grep(*)",
    "Task(*)"
  ]
}
```

## Phase 2: Autonomous Learning Framework

This is the most innovative part - implementing the dual-instance testing approach automatically.

### 2.1 Test Orchestrator Design

**Core Components:**

1. **Test Orchestrator** (`test_orchestrator.py`)
   - Manages two Claude Code instances via Agent SDK
   - Instance A (Dev): Designs tests, interprets results, updates knowledge
   - Instance B (Tester): Runs tests in clean environment
   - Coordinates the learning cycle

2. **Test Plan Structure**
   ```yaml
   feature: skills_invocation
   hypothesis: Skills with detailed when_to_use get invoked more reliably
   experiments:
     - name: minimal_description
       skill_config: {...}
       test_scenarios: [...]
     - name: detailed_symptoms
       skill_config: {...}
       test_scenarios: [...]
   success_criteria: {...}
   ```

3. **Learning Cycle** (inspired by Simon Willison's async research)
   ```
   1. Dev instance creates test plan with hypotheses
   2. Dev instance prepares Tester environment (settings, skills, etc.)
   3. Orchestrator launches Tester instance
   4. Tester runs experiments, records results
   5. Dev instance analyzes results
   6. Dev instance updates knowledge base
   7. Dev instance creates new hypotheses
   8. Repeat until knowledge is "bulletproof"
   ```

### 2.2 Knowledge Base Schema

SQLite database tracking:
- Features tested
- Configurations tried
- Results observed
- Patterns discovered
- Edge cases found
- Confidence scores
- Date learned

### 2.3 Implementing Instance Control

**Key Question:** Can Claude Code control another Claude Code instance?

**Approach:**
1. Use Agent SDK to create programmatic instances
2. Each instance has its own session and state
3. Orchestrator manages communication via structured data
4. Results written to shared filesystem location

**Alternative if direct control isn't feasible:**
1. Orchestrator writes commands to test instance
2. Manual execution of tests (semi-automated)
3. Results parsed automatically

## Phase 3: Skills Creation (TDD Approach)

Following the writing-skills methodology strictly.

### 3.1 Settings.json Skill (Already Have Data!)

**RED Phase:**
- You already have baseline behavior from manual testing
- Document the rationalizations/errors you encountered

**GREEN Phase:**
- Create skill with findings:
  - No spaces before colons: `Bash(test:*)` not `Bash(test :*)`
  - Wildcards only in directories, not filenames
  - Quote patterns with special characters
  - etc.

**REFACTOR Phase:**
- Test edge cases autonomously
- Add discovered gotchas

### 3.2 Skills Invocation Skill

**RED Phase:**
- Create skill with minimal description
- Test with Tester instance
- Document when it fails to invoke

**GREEN Phase:**
- Add detailed when_to_use with symptoms
- Test again
- Document improvements

**REFACTOR Phase:**
- Try edge cases (hooks + skills, overlapping domains)
- Document interaction patterns

### 3.3 Custom Tools Skill

**Learning Focus:**
- When are custom tools better than MCP servers?
- How to structure tool definitions?
- Common pitfalls in tool creation?
- Permission implications?

### 3.4 Project Hygiene Skill

Based on your requirements:

```yaml
---
name: AI Agent Project Hygiene
description: Structure and patterns for maintainable, resumable agent processes
when_to_use: |
  - Starting a new business process project
  - Process runs multiple times with different inputs
  - Long-running operations that might fail
  - Parallel processing requirements
  - Need to refine prompts without code changes
version: 1.0.0
---

## Core Principles

1. **Separation of Concerns**
   - functional/: Code that runs the process
   - outputs/: Data from specific runs
   - Never mix them

2. **Resumability First**
   - Always log progress to files
   - Use run-specific directories with timestamps
   - Store errors separately for analysis

3. **Prompt Isolation**
   - Store prompts as separate files
   - Scripts reference prompts, don't contain them
   - Easy iteration without touching code

... [detailed patterns] ...
```

### 3.5 Git Operations Skill

Based on steipete's rules, adapted for business process context:
- Atomic commits
- Never destructive operations without approval
- Path safety with special characters
- Coordination between instances

### 3.6 Parallel Processing Skill

```yaml
---
name: Parallel Processing with Python Workers
description: Patterns for concurrent operations with proper logging and error handling
when_to_use: |
  - Iterating over lists with >100 items
  - API calls that can run in parallel
  - Independent operations on multiple files
  - Symptoms: Long sequential processing, bored waiting
---

## Pattern

1. Use subagent for worker orchestration
2. Workers write to SQLite (no file race conditions)
3. Progress tracked in database
4. Resumable on failure
5. Error isolation per item

... [implementation details] ...
```

## Phase 4: Specific Learning Investigations

### 4.1 Skills Deep Dive
- Invocation triggers (description quality, keywords, context)
- Interaction with hooks
- Multi-skill conflicts
- Performance impact

### 4.2 Custom Tools
- MCP vs custom tools tradeoffs
- Tool definition patterns
- Permission granting
- Error handling

### 4.3 Hooks Investigation
- Hook types and use cases
- Combining with skills
- Performance considerations
- Security implications

### 4.4 Settings.json Mastery
- Permission patterns
- Wildcard behaviors
- Tool combinations
- Edge cases

## Phase 5: Template Creation

### 5.1 Business Process Template
Ready-to-use template with:
- Proper directory structure
- Base CLAUDE.md
- Example scripts with logging
- Prompt isolation examples
- .env template
- .gitignore
- README with usage

### 5.2 Worker Pattern Template
- SQLite schema for worker coordination
- Worker script template
- Orchestrator template
- Error handling patterns
- Progress tracking

## Phase 6: Validation

### 6.1 Create Example Business Process
Build a real business process using the harness:
- Demonstrate all patterns
- Test the template
- Validate skills are invoked correctly
- Refine based on learnings

### 6.2 Documentation
- README for the harness itself
- Tutorial for using the harness
- Skill reference documentation
- Troubleshooting guide

## Success Metrics

1. **Autonomous Learning Works**
   - Can run experiments without manual intervention
   - Produces reliable, documented findings
   - Updates knowledge base automatically

2. **Skills Are Bulletproof**
   - Tested with multiple scenarios
   - Edge cases documented
   - Confidence scores high

3. **Business Process Template Accelerates Development**
   - New projects start in minutes
   - Best practices are automatic
   - Fewer mistakes, more consistency

4. **Knowledge Accumulates**
   - Database grows with learnings
   - Skills improve over time
   - New discoveries feed back into skills

## Next Steps

1. Start with Phase 1: Create directory structure
2. Adapt CLAUDE.md
3. Build minimal test orchestrator
4. Test with one skill (settings.json - you have data!)
5. Refine orchestrator based on learnings
6. Expand to other skills

## Open Questions to Resolve

1. **Can Agent SDK control multiple Claude Code instances?**
   - Test with minimal example
   - Document limitations
   - Fallback approach if needed

2. **What's the best way to pass context between instances?**
   - Structured files (JSON/YAML)?
   - SQLite database?
   - Combination?

3. **How to measure "bulletproof" for skills?**
   - Test coverage?
   - Confidence scoring?
   - Number of edge cases handled?

4. **Time tracking subagent implementation?**
   - How to capture work descriptions?
   - Integration with git commits?
   - Format for time logs?
