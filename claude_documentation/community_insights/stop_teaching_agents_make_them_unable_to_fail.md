I've been working with AI agents for code generation, and I kept hitting the same wall: the agent would make the same mistakes every session. Wrong naming conventions, forgotten constraints, broken patterns I'd explicitly corrected before.

Then it clicked: I was treating a stateless system like it had memory.

The Core Problem: Investment Has No Persistence
With human developers:

You explain something once → they remember

They make a mistake → they learn

Investment in the person persists

With AI agents:

You explain something → session ends, they forget

They make a mistake → you correct it, they repeat it next time

Investment in the agent evaporates

This changes everything about how you design collaboration.

The Shift: Investment → System, Not Agent
Stop trying to teach the agent. Instead, make the system enforce what you want.

Claude Code gives you three tools. Each solves the stateless problem at a different layer:

The Tools: Automatic vs Workflow
Hooks (Automatic)

Triggered by events (every prompt, before tool use, etc.)

Runs shell scripts directly

Agent gets output, doesn't interpret

Use for: Context injection, validation, security

Skills (Workflow)

Triggered when task relevant (agent decides)

Agent reads and interprets instructions

Makes decisions within workflow

Use for: Multi-step procedures, complex logic

MCP (Data Access)

Connects to external sources (Drive, Slack, GitHub)

Agent queries at runtime

No hardcoding

Use for: Dynamic data that changes

Simple Rule
If you need...	Use...
Same thing every time	Hook
Multi-step workflow	Skill
External data access	MCP
Example: Git commits use a Hook (automatic template on "commit" keyword). Publishing posts uses a Skill (complex workflow: read → scan patterns → adapt → post).

How they work: Both inject content into the conversation. The difference is the trigger:

Hook:  External trigger
       └─ System decides when to inject

Skill: Internal trigger
       └─ Agent decides when to invoke
Here are 4 principles that make these tools work:

1. INTERFACE EXPLICIT (Not Convention-Based)
The Problem:

Human collaboration:

You: "Follow the naming convention"
Dev: [learns it, remembers it]
AI collaboration:

You: "Follow the naming convention"
Agent: [session ends]
You: [next session] "Follow the naming convention"
Agent: "What convention?"
The Solution: Make it impossible to be wrong

// ✗ Implicit (agent forgets)
// "Ports go in src/ports/ with naming convention X"

// ✓ Explicit (system enforces)
export const PORT_CONFIG = {
  directory: 'src/ports/',
  pattern: '{serviceName}/adapter.ts',
  requiredExports: ['handler', 'schema']
} as const;

// Runtime validation catches violations immediately
validatePortStructure(PORT_CONFIG);
Tool: MCP handles runtime discovery

Instead of the agent memorizing endpoints and ports, MCP servers expose them dynamically:

// ✗ Agent hardcodes (forgets or gets wrong)
const WHISPER_PORT = 8770;

// ✓ MCP server provides (agent queries at runtime)
const services = await fetch('http://localhost:8772/api/services').then(r => r.json());
// Returns: { whisper: { endpoint: '/transcribe', port: 8772 } }
The agent can't hardcode wrong information because it discovers everything at runtime. MCP servers for Google Drive, Slack, GitHub, etc. work the same way - agent asks, server answers.

2. CONTEXT EMBEDDED (Not External)
The Problem:

README.md: "Always use TypeScript strict mode"
Agent: [never reads it or forgets]
The Solution: Embed WHY in the code itself

/**
 * WHY STRICT MODE:
 * - Runtime errors become compile-time errors
 * - Operational debugging cost → 0
 * - DO NOT DISABLE: Breaks type safety guarantees
 * 
 * Initial cost: +500 LOC type definitions
 * Operational cost: 0 runtime bugs caught by compiler
 */
{
  "compilerOptions": {
    "strict": true
  }
}
The agent sees this every time it touches the file. Context travels with the code.

Tool: Hooks inject context automatically

When files don't exist yet, hooks provide context the agent needs:

# UserPromptSubmit hook - runs before agent sees your prompt
# Automatically adds project context

#!/bin/bash
cat  /dev/"; then
  echo '{"permissionDecision": "deny", "reason": "Dangerous command blocked"}' 
  exit 0
fi

echo '{"permissionDecision": "allow"}'
Agent can't execute rm -rf even if it tries. The hook blocks it structurally. Security happens at the system level, not agent discretion.

4. ITERATION PROTOCOL (Error → System Patch)
The Problem: Broken loop

Agent makes mistake → You correct it → Session ends → Agent repeats mistake
The Solution: Fixed loop

Agent makes mistake → You patch the system → Agent can't make that mistake anymore
Example:

// ✗ Temporary fix (tell the agent)
// "Port names should be snake_case"

// ✓ Permanent fix (update the system)
function validatePortName(name: string) {
  if (!/^[a-z_]+$/.test(name)) {
    throw new Error(
      `Port name must be snake_case: "${name}"
      
      Valid:   whisper_port
      Invalid: whisperPort, Whisper-Port, whisper-port`
    );
  }
}
Now the agent cannot create incorrectly named ports. The mistake is structurally impossible.

Tool: Skills make workflows reusable

When the agent learns a workflow that works, capture it as a Skill:

--- 
name: setup-typescript-project
description: Initialize TypeScript project with strict mode and validation
---

1. Run `npm init -y`
2. Install dependencies: `npm install -D typescript @types/node`
3. Create tsconfig.json with strict: true
4. Create src/ directory
5. Add validation script to package.json
Next session, agent uses this Skill automatically when it detects "setup TypeScript project" in your prompt. No re-teaching. The workflow persists across sessions.

Real Example: AI-Friendly Architecture
Here's what this looks like in practice:

// Self-validating, self-documenting, self-discovering

export const PORTS = {
  whisper: {
    endpoint: '/transcribe',
    method: 'POST' as const,
    input: z.object({ audio: z.string() }),
    output: z.object({ text: z.string(), duration: z.number() })
  },
  // ... other ports
} as const;

// When the agent needs to call a port:
// ✓ Endpoints are enumerated (can't typo) [MCP]
// ✓ Schemas auto-validate (can't send bad data) [Constraint]
// ✓ Types autocomplete (IDE guides agent) [Interface]
// ✓ Methods are constrained (can't use wrong HTTP verb) [Validation]
Compare to the implicit version:

// ✗ Agent has to remember/guess
// "Whisper runs on port 8770"
// "Use POST to /transcribe"  
// "Send audio as base64 string"

// Agent will:
// - Hardcode wrong port
// - Typo the endpoint
// - Send wrong data format
Tools Reference: When to Use What
Need	Tool	Why	Example
Same every time	Hook	Automatic, fast	Git status on commit
Multi-step workflow	Skill	Agent decides, flexible	Post publishing workflow
External data	MCP	Runtime discovery	Query Drive/Slack/GitHub
Hooks: Automatic Behaviors
Trigger: Event (every prompt, before tool, etc.)

Example: Commit template appears when you say "commit"

Pattern: Set it once, happens automatically forever

Skills: Complex Workflows
Trigger: Task relevance (agent detects need)

Example: Publishing post (read → scan → adapt → post)

Pattern: Multi-step procedure agent interprets

MCP: Data Connections
Trigger: When agent needs external data

Example: Query available services instead of hardcoding

Pattern: Runtime discovery, no hardcoded values

How they work together:

User: "Publish this post"
→ Hook adds git context (automatic)
→ Skill loads publishing workflow (agent detects task)
→ Agent follows steps, uses MCP if needed (external data)
→ Hook validates final output (automatic)
Setup:

Hooks: Shell scripts in .claude/hooks/ directory

# Example: .claude/hooks/commit.sh
echo "Git status: $(git status --short)"
Skills: Markdown workflows in ~/.claude/skills/{name}/SKILL.md

---
name: publish-post
description: Publishing workflow
---
1. Read content
2. Scan past posts  
3. Adapt and post
MCP: Install servers via claude_desktop_config.json

{
  "mcpServers": {
    "filesystem": {...},
    "github": {...}
  }
}
All three available in Claude Code and Claude API. Docs: https://docs.claude.com

The Core Principles
Design for Amnesia

Every session starts from zero

Embed context in artifacts, not in conversation

Validate, don't trust

Investment → System

Don't teach the agent, change the system

Replace implicit conventions with explicit enforcement

Self-documenting code > external documentation

Interface = Single Source of Truth

Agent learns from: Types + Schemas + Runtime introspection (MCP)

Agent cannot break: Validation + Constraints + Fail-fast (Hooks)

Agent reuses: Workflows persist across sessions (Skills)

Error = System Gap

Agent error → system is too permissive

Fix: Don't correct the agent, patch the system

Goal: Make the mistake structurally impossible

The Mental Model Shift
Old way: AI agent = Junior developer who needs training

New way: AI agent = Stateless worker that needs guardrails

The agent isn't learning. The system is.

Every correction you make should harden the system, not educate the agent. Over time, you build an architecture that's impossible to use incorrectly.

TL;DR
Stop teaching your AI agents. They forget everything.

Instead:

Explicit interfaces - MCP for runtime discovery, no hardcoding

Embedded context - Hooks inject state automatically

Automated constraints - Hooks validate, block dangerous actions

Reusable workflows - Skills persist knowledge across sessions

The payoff: Initial cost high (building guardrails), operational cost → 0 (agent can't fail).

Relevant if you're working with code generation, agent orchestration, or LLM-powered workflows. The same principles apply.

Would love to hear if anyone else has hit this and found different patterns.