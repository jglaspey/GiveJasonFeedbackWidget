Alright — here’s the cleanest, most practical way to understand how you’d actually use the Anthropic Agent SDK (initializer + coding agent) in a real project.

No buzzwords. Just the mechanics.

🚦 First: The Core Idea in Plain Terms

Think of the SDK like this:

Initializer Agent = “Project architect + product manager + repo bootstrapper.”
It creates the environment the long-running agent needs to not get lost later.

Coding Agent = “The engineer who wakes up every morning, checks the task list, picks one item, builds/test/commit, logs progress, and goes home.”

The breakthrough is that this coding agent keeps working for days/weeks because everything it needs to remember is stored in:

a structured progress log,

a feature/task list,

a project definition,

a repo with incremental commits,

and a consistent calling harness.

Every session, it reads these artifacts back in.
So it never “forgets where it left off.”

🧪 Now: A Real-World Example (Let’s use one you know)

Let’s say you want to build a simplified version of “Roofing Estimate Analyzer.”

Normally, agents choke on this because:

they forget the PRD

forget what files exist

try to do everything at once

stop in the middle of a task

regress on previous work

don’t track incremental progress

and can’t resume the next day

The SDK fixes that by splitting the job into 2 stages.

🏗️ STEP 1 — You create the initializer agent

You tell it something like:

“Create a new TypeScript project called REA Lite.
Use Next.js.
Include: /agents, /logs, /features.json, /tasks.md, /src.
Create a PRD file.
Write a plan broken into ~20 implementable features.”

The initializer agent then:

✔️ Creates the actual repo

Like:

/REA-lite
  /src
  /agents
  features.json
  tasks.md
  progress.log
  project.md (PRD)
  package.json

✔️ Writes the initial files

package.json

readme

stub components

boilerplate Next.js pages

✔️ Generates:

a master feature list (the canonical truth)

a task list (state machine of TODO → IN-PROGRESS → DONE)

a persistent progress log

✔️ And commits all of this to git

This is the “world” the coding agent will live in.

🤖 STEP 2 — You run the coding agent

Now the magic:
You don’t tell the agent “build the whole app.”

You tell it:

“Use the project harness.
Pick exactly ONE feature from features.json that is not done.
Implement it end-to-end.
Write tests.
Update progress.log.
Commit.”

This creates a deterministic cycle:

The coding agent loads:

tasks.md

features.json

project.md

progress.log

the whole repo snapshot

It selects ONE task (never more).

It implements it fully.

It updates:

the log

the task list

the codebase

tests

It commits.

It exits.

Next time you call it — even a week later — the next cycle begins with perfect continuity.

🔄 What “long-running” means here

It does not mean persistent background processes.

It means:
“The agent’s understanding of the project persists across many invocations.”

Because all memory is externalized into:

project files

progress logs

structured task lists

commit history

The LLM is stateless,
but the project harness makes the system stateful.

🧠 Why this is different from LangGraph / CrewAI / your current setups

Your existing agentic systems try to maintain memory inside the graph / state machine.

Anthropic flips the model:

➡️ The project files ARE the memory.
➡️ The agent simply reads them every time.

This means:

You can stop/start days later

You can have multiple agents working on same repo

No hallucinated tasks

No forgetting PRDs

No “complete app in one shot” failures

No circular agent loops

No “I got confused, let’s start over” moments

If you think about it, it’s how real engineers work.

🧩 A Concrete Usage Scenario (super clear)

Imagine you have a folder:

/projects/roofing-lite/


You run:

await initializer.run({
  name: "roofing-lite",
  description: "Extract images from roof reports and pair with line items.",
  tech_stack: "Next.js + OpenAI Vision + Supabase",
});


It outputs:

a repo

tasks list

feature breakdown

scaffolded pages

a clear project structure

Next:

await codingAgent.run({
  projectRoot: "./projects/roofing-lite",
});


The coding agent sees:

Next feature to implement: “Upload PDF → store → extract images”

It:

generates the upload UI

writes the API route

integrates Supabase storage

tests the upload endpoint

updates the progress log

marks the feature as done

commits the work

Next time you run it,
it moves to the next feature.

No confusion.
No forgetting.
No multi-feature overreach.

👍 Let me make it even more concrete for YOUR world

Here are 3 examples that map directly to your work:

1. CopyClub Content System

Initializer:

Creates the repo & architecture

Builds a PRD from scratch

Writes the content pipeline scaffold

Coding agent:

Implements 1 type of lesson card at a time

Writes the ingestion pipeline

Commits each step

Can stop/start for weeks until it’s done

2. Lost Valley Dashboard

Initializer:

Creates a schema doc

Creates empty UI screens

Creates tasks.json

Coding agent (session 4):

Sees “Implement resident roster screen”

Builds it fully

Updates logs

Commits

It never loses the plot.

3. EOD Agentic Flow

Initializer:

Sets up /agents, /pdf_parsers, /state, /logs

Defines 20 features for v0

Writes initial docstrings and stub functions

Coding agent:

Grabs “Implement line-item diffing”

Writes code

Writes tests

Updates progress

Commits

Again:
Never forgets.
Never restarts.
Never derails.

📌 Summary (the TL;DR clarity you wanted)

To use the SDK correctly:

Initializer builds the entire project ecosystem.
This is the one-time “design + scaffold + project memory” agent.

Coding Agent works like a disciplined engineer.
One feature per run. Reads the logs. Writes code. Commits. Updates memory.

The memory is externalized in files, not inside the agent.

Your job is just invoking the agents periodically.
They maintain continuity through the project artifacts.

If you want, I can:

✅ write an example initializer config
✅ write an example coding agent harness
✅ show you how to use this with your CopyEmpire repo
✅ sketch the folder structure Anthropic recommends
✅ build a full demo project for you using this style

Just tell me what direction you want to explore next.

0. Big picture: what actually changes for you?

Cursor: nothing changes. It’s still just your editor with AI baked in.

Claude Code (CLI / web / VS Code): still great for interactive “pair programming” sessions.

Claude Agent SDK: this is a Node/Python library you install inside a project so you can script / automate what Claude Code does (read files, edit, run commands, use MCP, etc). 
Claude Console
+1

So the SDK doesn’t replace Cursor. It’s more like: “Instead of me asking Claude Code manually, I write a TypeScript script that calls Claude’s agent harness for me.”

1. Where do I install the SDK?

You install it like any other npm package, in the repo where the agent will run.

In the root of that repo (could be CopyEmpire, your EOD agent, or a new agent-runner repo):

npm install @anthropic-ai/claude-agent-sdk
# or
pnpm add @anthropic-ai/claude-agent-sdk
# or
yarn add @anthropic-ai/claude-agent-sdk


Anthropic’s docs: 
GitHub
+1

npm install @anthropic-ai/claude-agent-sdk

You do not install it into Cursor or into Claude Code.
It just lives in your normal Node/TypeScript project.

2. Auth: how does it talk to Claude?

You give it an API key, same as any other Claude integration.

In your project:

Create .env:

ANTHROPIC_API_KEY=sk-ant-...


Load it (if you’re not already using dotenv):

// src/env.ts
import 'dotenv/config';

if (!process.env.ANTHROPIC_API_KEY) {
  throw new Error('ANTHROPIC_API_KEY not set');
}


The official docs say: set ANTHROPIC_API_KEY in the environment for basic authentication. 
Claude Console

You don’t need to hook it into your Claude Code subscription / CLI directly; the SDK uses the API.

3. Minimal “does this work?” script

Let’s make this dead simple. In your repo:

mkdir -p src
touch src/agent-test.ts


src/agent-test.ts:

import 'dotenv/config';
import { query } from '@anthropic-ai/claude-agent-sdk';

async function main() {
  const stream = query({
    prompt: "Say hello and list the files in this repo.",
    options: {
      // Make it behave like Claude Code and use .claude / CLAUDE.md if you want
      systemPrompt: { type: 'preset', preset: 'claude_code' },
      settingSources: ['project'], // load .claude settings & CLAUDE.md :contentReference[oaicite:3]{index=3}
      cwd: process.cwd(),
      allowedTools: ['Read', 'ListFiles'], // keep tools tight at first
    },
  });

  for await (const msg of stream) {
    if (msg.type === 'message') {
      const textParts = msg.content
        .filter((c) => c.type === 'text')
        .map((c: any) => c.text)
        .join('\n');
      process.stdout.write(textParts);
    }
  }
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});


Run it (with ts-node/tsx, or compile):

npx tsx src/agent-test.ts


If that runs and you see Claude talking + listing files, the SDK is wired up.

4. How does this relate to Claude Code + .claude + CLAUDE.md?

This is the neat part.

The TypeScript Agent SDK can reuse all the Claude Code project config you already have:

.claude/settings.json, .claude/settings.local.json

CLAUDE.md / .claude/CLAUDE.md (project memory / instructions)

.claude/agents, .claude/skills, .claude/commands etc 
Claude Console
+1

To opt into those, you pass:

options: {
  systemPrompt: { type: 'preset', preset: 'claude_code' }, // use Claude Code-style system prompt
  settingSources: ['project'],                             // load .claude + CLAUDE.md for this repo
}


So:

When you’re in Claude Code CLI or web, it reads that stuff automatically.

When you use the Agent SDK, it reads the same stuff if you tell it to.

That’s why the “initializer + coding agent” story works nicely: they can log and plan in files the SDK and Claude Code both understand.

5. What actually changes in your day-to-day workflow?
Right now (without SDK)

You sit in Cursor, maybe occasionally in Claude Code CLI/web.

You manually paste tasks / PRDs / “here’s what to do next”.

Claude Code does stuff, but there’s no programmatic harness that:

picks 1 feature,

implements it,

updates logs,

commits,

and can be re-run as a script.

With the Agent SDK

You add a couple of scripts to your repo, like:

scripts/initializer.ts

scripts/coding-agent.ts

They roughly do:

// scripts/initializer.ts
import { query } from '@anthropic-ai/claude-agent-sdk';

await query({
  prompt: `
You are the initializer agent.
- Scan the repo.
- Generate features.json, tasks.md, progress.log.
- Initialize git if needed.
- Mark all features as not implemented.
  `,
  options: {
    systemPrompt: { type: 'preset', preset: 'claude_code' },
    settingSources: ['project'],
    cwd: process.cwd(),
    allowedTools: ['Read', 'Write', 'Edit', 'ListFiles', 'CreateFile'],
  },
});

// scripts/coding-agent.ts
import { query } from '@anthropic-ai/claude-agent-sdk';

await query({
  prompt: `
You are the coding agent.

1. Read features.json, tasks.md, and progress.log.
2. Choose exactly ONE unfinished feature.
3. Implement it end-to-end (code, tests).
4. Update progress.log and tasks.md.
5. Stage and commit the changes.

Do not start a new feature after committing. Stop.
  `,
  options: {
    systemPrompt: { type: 'preset', preset: 'claude_code' },
    settingSources: ['project'],
    cwd: process.cwd(),
    allowedTools: [
      'Read',
      'Write',
      'Edit',
      'ListFiles',
      'Run',
      'GitStatus',
      'GitDiff',
      'GitCommit',
    ],
    permissionMode: 'acceptEdits', // or default if you want confirmations :contentReference[oaicite:5]{index=5}
  },
});


Now your “long-running agent” is just:

# one-time
npx tsx scripts/initializer.ts

# each time you want it to pick up the next feature:
npx tsx scripts/coding-agent.ts


You still open the repo in Cursor, inspect the code, refactor, etc.
The difference is you have a repeatable, resumable agent script that keeps reading the same logs and files and slowly completes the feature list.

6. What about the fact I’m “using Claude Code already”?

Main changes:

Installation location

Before: maybe you installed Claude Code CLI globally.

Now: you also install @anthropic-ai/claude-agent-sdk per project (as a dependency). 
GitHub
+1

How you “call” Claude

Before: talk to Claude Code via its UI (CLI/web/VS Code).

Now: talk to the same engine via query({ prompt, options }) in Node.

Config reuse

If you’re already using .claude/ and CLAUDE.md, just turn on
systemPrompt: { type: 'preset', preset: 'claude_code' } and settingSources: ['project'] so the SDK behaves like Claude Code for that project. 
Claude Console

Cursor

Completely unchanged.

It’s just your editor; the SDK is just another Node dep.

7. If you want, I can tailor this to ONE real repo

If you tell me:

which repo (e.g. eod-agentic-flow, CopyEmpire, lost-valley-today-dashboard, etc.), and

whether you’re using pnpm / npm, and how you usually run TS (ts-node, tsx, bun),

I can write:

exact install commands,

a scripts/initializer.ts and scripts/coding-agent.ts that match that repo,

and the package.json scripts you’d add so Storm / Justin can just run:

pnpm agent:init
pnpm agent:next


and let Claude chew through the features list.