# V1 Dev Harness - Minimal Viable Product

## Philosophy: Bootstrap, Don't Boil the Ocean

**V1 Goal:** Get a working dev harness that immediately provides value and can be used to build V2.

**V2 Goal:** Use the V1 harness to build the autonomous learning framework.

This is dogfooding - if the V1 harness is good, building the autonomous learning framework should be easier using it.

## V1 Scope (Week 1-2)

### What's IN V1

✅ **Core Structure**
- Directory layout (dev harness + business process template)
- .gitignore patterns
- README and documentation

✅ **CLAUDE.md**
- Adapted from Obra's dotfile
- Agent-specific rules added
- Ready to use

✅ **3-5 Foundational Skills** (manually created from existing knowledge)
1. **settings.json-patterns**: Your validated findings
2. **agent-project-setup**: Structure, logging, resumability rules
3. **git-operations**: Based on steipete's rules
4. **agent-sdk-basics**: Use SDK not API, session management
5. **parallel-processing**: Worker patterns, SQLite coordination

✅ **Business Process Template**
- Directory structure (functional/ + outputs/)
- Base .claude/CLAUDE.md
- Example scripts with logging
- .env template
- .gitignore

✅ **Example Subagents** (slash commands or Task tool patterns)
- Git commit helper
- Time tracking logger

✅ **One Working Example**
- Simple business process using the template
- Validates the harness works

### What's NOT in V1

❌ Autonomous learning framework (build in V2 using V1!)
❌ Large skills library (build over time)
❌ Advanced templates (iterate based on usage)
❌ Comprehensive testing harness (add as needed)
❌ Multi-instance orchestration (V2 project)

## V1 Implementation Steps

### Step 1: Directory Structure (30 min)

```bash
agent_dev_harness/
├── .claude/
│   ├── CLAUDE.md              # Development rules
│   ├── settings.json          # Permissive for development
│   └── skills/                # Foundational skills
│       ├── settings-json-patterns/
│       ├── agent-project-setup/
│       ├── git-operations/
│       ├── agent-sdk-basics/
│       └── parallel-processing/
├── templates/
│   └── business_process/
│       ├── .claude/
│       │   ├── CLAUDE.md      # Process-specific template
│       │   └── settings.json  # Restrictive template
│       ├── functional/
│       │   ├── scripts/
│       │   ├── prompts/
│       │   └── workers/
│       ├── outputs/.gitkeep
│       ├── .env.example
│       ├── .gitignore
│       └── README.md
├── projects/                   # Your business processes live here
├── docs/                       # Documentation
│   ├── IMPLEMENTATION_PLAN.md
│   ├── AUTONOMOUS_LEARNING_SPEC.md
│   └── skills_reference.md
├── README.md
└── V1_PLAN.md                 # This file
```

### Step 2: CLAUDE.md (1 hour)

Start with Obra's, add sections:

```markdown
## Agent Development Context

You are helping build AI agents for business processes. This dev harness
creates agents that run in separate project directories.

### Project Structure Rules
- Business processes live in projects/ with their own .claude configs
- Separate functional code from outputs
- Use timestamp-based run directories
- Isolate prompts from scripts

### Agent SDK Usage
- ALWAYS use Agent SDK for local scripts (not Anthropic API)
- Uses Claude subscription, not API credits
- Session management patterns in skills/agent-sdk-basics/

### Parallel Processing
- >100 items: Use Python workers
- Workers log to SQLite (no race conditions)
- Run workers in subagent (context isolation)
- See skills/parallel-processing/ for patterns

### Path and Configuration
- NO hardcoded machine-specific paths
- Use .env for secrets and config
- Paths relative to project root or from env vars

### Resumability
- Long operations: Log progress
- Errors: Separate errors/ directory with context
- Enable resuming from last successful item

### Debugging
- Document attempts in debugging_log.md
- Track what works and what doesn't
- Don't repeat failed approaches

## Subagents Available

- git-commit: Helps create atomic commits with good messages
- time-tracker: Logs time spent with work descriptions
```

### Step 3: Create 5 Foundational Skills (3 hours)

These are MANUALLY created from knowledge we already have.

**Skill 1: settings-json-patterns** (from your testing)
- No spaces before colons
- Wildcards in directories only
- Permission format patterns
- Common configurations
- Debugging tips

**Skill 2: agent-project-setup** (from your requirements list)
```yaml
---
name: AI Agent Project Hygiene
description: Structure and patterns for maintainable business process agents
when_to_use: |
  - Starting new business process project
  - Organizing long-running agent scripts
  - Need resumability and error handling
  - Symptoms: "messy project structure", "hard to debug", "can't resume"
version: 1.0.0
---

## Directory Structure

functional/           # Code that runs the process
  scripts/           # Python scripts
  prompts/           # Isolated prompt files
  workers/           # Parallel processing workers
outputs/             # Run-specific outputs (gitignored)
  run_YYYY-MM-DD_HHMMSS/
    logs/
    results/
    errors/

## Key Principles

1. Separate functional from outputs
2. Prompts in files, not embedded in code
3. Timestamp-based run directories
4. SQLite for worker coordination
5. Comprehensive logging
6. Machine-agnostic paths

[... detailed patterns ...]
```

**Skill 3: git-operations** (adapted from steipete)
- Atomic commits
- Safety rules
- Path quoting
- Coordination between instances

**Skill 4: agent-sdk-basics**
```yaml
---
name: Claude Agent SDK Basics
description: Using Agent SDK instead of Anthropic API for local scripts
when_to_use: |
  - Writing Python scripts that call Claude
  - Building business process automation
  - Local development (not production API)
  - Symptoms: "API costs too high", "using anthropic.Anthropic()"
version: 1.0.0
---

## Why Agent SDK?

- Uses Claude subscription (no API charges)
- Better for local development
- Supports all Claude Code features

## Basic Pattern

```python
from anthropic import Anthropic

# ❌ DON'T - Uses API credits
client = Anthropic(api_key="...")
message = client.messages.create(...)

# ✅ DO - Uses subscription
from claude_agent_sdk import create_session

session = await create_session()
response = await session.send_message("Your prompt")
```

[... more patterns ...]
```

**Skill 5: parallel-processing**
- When to use workers
- SQLite coordination
- Subagent for orchestration
- Error isolation
- Progress tracking

### Step 4: Business Process Template (2 hours)

Create a ready-to-use template in `templates/business_process/`

**Key files:**
- `.claude/CLAUDE.md` - Process-specific instructions template
- `.claude/settings.json` - Restrictive permissions
- `functional/scripts/example_process.py` - Shows logging, resumability
- `functional/prompts/example_prompt.txt` - Isolated prompt
- `.env.example` - What env vars needed
- `README.md` - How to use the template

### Step 5: Example Subagents (1 hour)

**Option A: Slash Commands**
`.claude/commands/git-commit.md`:
```markdown
You are helping create a git commit.

Follow these rules:
1. Review git status and git diff
2. Create atomic commit (only related changes)
3. Write clear commit message (what + why)
4. Follow this repository's commit style
5. Use steipete's safety rules (skills/git-operations/)

Do NOT commit secrets or .env files.
```

**Option B: Task Tool Patterns**
Document in CLAUDE.md:
```markdown
When asked to commit changes:
- Use Task tool with description "Create git commit"
- Subagent has git-operations skill
- Follows atomic commit rules
```

Time tracker similar approach.

### Step 6: Create Example Project (2 hours)

Build a real but simple business process:

```
projects/example_web_scraper/
├── .claude/
│   ├── CLAUDE.md          # "You scrape websites and extract data"
│   └── settings.json      # Can read config/, write outputs/
├── functional/
│   ├── scripts/
│   │   └── scraper.py     # Main script with logging
│   ├── prompts/
│   │   └── extract_data.txt
│   └── config/
│       └── urls.txt
├── outputs/
│   └── run_2025-01-15_143022/
│       ├── logs/
│       │   └── progress.log
│       └── results/
│           └── scraped_data.json
└── .env.example
```

This validates:
- Template works
- Skills are useful
- CLAUDE.md guides correctly
- Patterns are practical

### Step 7: Documentation (1 hour)

- Update README.md for V1 scope
- Create skills reference doc
- Write template usage guide
- Document subagent patterns

## V1 Success Criteria

After ~10-12 hours of work, you should have:

✅ Working dev harness with clear structure
✅ Adapted CLAUDE.md ready to use
✅ 5 foundational skills (manually created)
✅ Business process template (copy & customize)
✅ Example subagents (git, time tracking)
✅ One working example project
✅ Good documentation

**Most importantly:** You can start using it immediately to build business processes!

## Using V1 to Build V2

Once V1 is working:

1. **Create new project in V1 harness:**
   ```bash
   cp -r templates/business_process projects/autonomous_learning_framework
   cd projects/autonomous_learning_framework
   ```

2. **Customize for the learning framework:**
   - .claude/CLAUDE.md: "You are building an autonomous learning framework"
   - functional/: The orchestrator, test plans, etc.
   - Use V1 skills: agent-project-setup, parallel-processing, etc.

3. **Benefits:**
   - V1 harness guides you
   - Skills provide patterns
   - Subagents help with commits, time tracking
   - Validates V1 is useful (dogfooding)

4. **As you build V2, you'll discover:**
   - What skills are missing
   - What CLAUDE.md rules to add
   - What template improvements needed
   - Real-world pain points

5. **Iterate V1 based on V2 experience**

## V1 Timeline

- **Day 1** (4 hours): Steps 1-2 (structure + CLAUDE.md)
- **Day 2** (4 hours): Step 3 (create 2-3 skills)
- **Day 3** (4 hours): Step 3 continued (finish skills) + Step 4 (template)
- **Day 4** (3 hours): Steps 5-6 (subagents + example)
- **Day 5** (1 hour): Step 7 (documentation) + polish

**Total: ~16 hours over 1-2 weeks**

## V1 to V2 Transition

**V1 delivers:**
- Immediate productivity boost
- Proven patterns
- Foundation to build on

**V2 uses V1 to build:**
- Autonomous learning framework
- More sophisticated skills
- Advanced patterns
- Refined templates

**Then V3:**
- Large skills library
- Community contributions
- Advanced automation
- Training resources

## What to Build First in V1?

I recommend this order:

1. ✅ Directory structure (quick win)
2. ✅ CLAUDE.md (enables everything)
3. ✅ settings-json-patterns skill (you have data!)
4. ✅ agent-project-setup skill (most universally useful)
5. ✅ Business process template (need this to be useful)
6. ✅ Example project (validates it works)
7. → git-operations skill (useful for V2 development)
8. → agent-sdk-basics skill (useful for V2 development)
9. → parallel-processing skill (may not need immediately)
10. → Subagents (nice to have, not critical)

**Minimum viable V1: Steps 1-6 (~8-10 hours)**

Ready to start building V1?
