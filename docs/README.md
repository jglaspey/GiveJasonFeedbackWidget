# AI Agent Development Harness

A meta-development environment for building business process AI agents with Claude Code and the Agent SDK.

## What Is This?

This harness solves a key problem: **How do you systematically build and improve AI agents when the tooling itself is still evolving?**

Traditional approach:
- Trial and error with Claude Code features
- Inconsistent project structures
- Hard to share learnings across projects
- Repeat same mistakes

This harness provides:
- **Autonomous learning framework** that systematically explores Claude Code/Agent SDK features
- **Curated skills** distilling best practices and hard-won knowledge
- **Project templates** enforcing good patterns automatically
- **Two-tier architecture** separating agent development from agent execution

## Architecture

```
agent_dev_harness/          → DEV HARNESS (you work here)
├── .claude/
│   ├── CLAUDE.md           → Development-focused rules
│   └── skills/             → Skills for building agents
├── learning_framework/     → Autonomous feature exploration
├── templates/              → Ready-to-use project templates
└── projects/               → Your business process projects
    └── my_process/         → BUSINESS PROCESS (agent runs here)
        ├── .claude/        → Process-specific config
        ├── functional/     → Process logic
        └── outputs/        → Run-specific results
```

## Key Innovations

### 1. Autonomous Learning Framework

Inspired by TDD and systematic testing, this framework:
- Runs experiments to understand Claude Code features
- Uses dual-instance testing (Dev + Tester)
- Records findings in knowledge base
- Generates bulletproof skills

**Example:** Learning how skills invocation works
```bash
python -m learning_framework.orchestrator learn "skills_invocation"
# Orchestrator automatically:
# 1. Designs baseline tests
# 2. Runs tests WITHOUT skill
# 3. Creates skill based on findings
# 4. Tests WITH skill
# 5. Finds edge cases
# 6. Refines until bulletproof
```

### 2. Bulletproof Skills

Not just documentation - systematically validated knowledge:
- **settings.json patterns**: Exact syntax that works (not just validates)
- **Skills invocation**: When they trigger, when they don't
- **Custom tools**: Real use cases and gotchas
- **Project hygiene**: Proven patterns for maintainable agents

Each skill includes:
- Symptoms triggering its use
- Concrete examples
- Common mistakes
- Confidence scores

### 3. Best Practice Enforcement

Skills encode practices like:
- Test scripts in `test_scripts/`
- Parallel operations use Python workers
- Progress logs for resumability
- SQLite for concurrent workers
- Prompts isolated from code
- Agent SDK instead of API
- Machine-agnostic paths
- Output organization by run

### 4. Two-Tier Development

**Dev Harness (Parent):**
- Instance: Development Claude Code
- Purpose: Build and test agents
- Skills: Claude Code features, patterns, hygiene
- Permissions: Permissive (you're developing)

**Business Process (Child):**
- Instance: Execution Claude Code
- Purpose: Run specific business process
- Skills: Process-specific (if any)
- Permissions: Restrictive (production)

Benefits:
- Clear separation of concerns
- Different permission models
- Process can't accidentally modify harness
- Easy to create multiple processes

## Quick Start

### Prerequisites
- Claude Code installed
- Python 3.8+
- Git
- Claude subscription (for Agent SDK)

### 1. Validate Multi-Instance Control
```bash
cd validation_test
python test_multi_instance.py
```

### 2. Set Up Structure
```bash
# Creates directories, .gitignore, etc.
./scripts/setup.sh
```

### 3. Adapt CLAUDE.md
```bash
# Copy and customize for agent development
cp claude_documentation/community_insights/obra_claude_dotfile.md .claude/CLAUDE.md
# Add agent-specific rules (see QUICKSTART.md)
```

### 4. Create First Skill
```bash
# Settings.json patterns (you have data!)
mkdir -p .claude/skills/settings-json-patterns
# See QUICKSTART.md for complete skill content
```

### 5. Start Learning
```bash
# Pick a feature to deeply understand
python learning_framework/simple_orchestrator.py plan skills-invocation
```

**Full walkthrough:** See `QUICKSTART.md`

## Documentation

- **[QUICKSTART.md](QUICKSTART.md)**: Step-by-step first steps
- **[IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md)**: Complete project roadmap
- **[AUTONOMOUS_LEARNING_SPEC.md](AUTONOMOUS_LEARNING_SPEC.md)**: Technical details of learning framework
- **[claude_documentation/](claude_documentation/)**: Reference materials

## Project Status

**✅ V1: Minimal Viable Harness** (COMPLETE!)
- [x] Directory structure
- [x] Adapted CLAUDE.md with agent-specific rules
- [x] settings-json-patterns skill (from validated testing)
- [x] agent-project-setup skill (comprehensive patterns)
- [x] Business process template (ready to copy)
- [x] Example project (working demonstration)

**🚧 Next: Use V1 to Build V2** (Autonomous Learning Framework)
- [ ] Create new project using template: `projects/autonomous_learning_framework`
- [ ] Build test orchestrator using V1 patterns
- [ ] Implement dual-instance testing methodology
- [ ] Test with skills-invocation learning
- [ ] Expand autonomous learning capabilities

**📚 Additional Skills** (Build as needed)
- [ ] git-operations skill (based on steipete)
- [ ] agent-sdk-basics skill
- [ ] parallel-processing skill (detailed patterns)
- [ ] custom-tools skill (when we learn it)

**📝 Documentation**
- [x] V1_PLAN.md
- [x] IMPLEMENTATION_PLAN.md
- [x] AUTONOMOUS_LEARNING_SPEC.md
- [x] QUICKSTART.md
- [ ] Video walkthrough (optional)
- [ ] Blog post (optional)

## Use Cases

### For Agent Developers
- Systematic learning of Claude Code features
- Proven patterns and best practices
- Faster project setup
- Fewer repeated mistakes

### For Business Process Automation
- Quick start with templates
- Reliable, resumable processes
- Proper error handling
- Easy maintenance

### For Teams
- Shared knowledge base
- Consistent project structures
- Accumulated learnings
- Onboarding resource

## Philosophy

Inspired by:
- **Jesse Vincent (obra)**: Systematic discipline, TDD for everything
- **Peter Steinberger (steipete)**: Safety first, explicit rules
- **Simon Willison**: Parallel exploration, async research
- **Your own discovery**: Dual-instance testing methodology

Core beliefs:
1. **Systematic > Ad-hoc**: Structured learning beats trial-and-error
2. **Test-driven**: Even for documentation (RED-GREEN-REFACTOR)
3. **Bulletproof > Fast**: Take time to really understand
4. **Accumulate knowledge**: Each learning builds on previous
5. **Automate discipline**: Skills enforce best practices

## Community

This project synthesizes ideas from:
- Claude Code community (skills, hooks, patterns)
- Obra's superpowers (TDD for skills)
- Various thought leaders (see `claude_documentation/community_insights/`)

Contributions welcome:
- Share your skills
- Contribute learnings
- Improve templates
- Document edge cases

## License

[Your license choice]

## Roadmap

### Short Term (1-2 months)
- Complete Phase 1-2 (foundation + learning)
- Validate approach with 3-5 feature learnings
- Create initial skill library

### Medium Term (3-6 months)
- Build comprehensive skills library
- Multiple business process templates
- Public documentation site

### Long Term (6+ months)
- Community skill contributions
- Integration with Claude Code marketplace
- Advanced patterns (multi-agent, complex workflows)
- Training resources

## Questions? Issues?

- See documentation in this repo
- Check community insights
- Create GitHub issue
- Join discussions

## Acknowledgments

Special thanks to:
- **Jesse Vincent (obra)**: For the foundational CLAUDE.md and superpowers skills framework
- **Peter Steinberger (steipete)**: For git safety rules
- **Simon Willison**: For async research patterns
- **Claude Code team**: For building the platform
- **Community contributors**: For sharing insights

---

**Note:** This is a meta-development tool. The harness helps you build agents; your agents (business processes) live in the `projects/` subdirectories with their own configurations.
