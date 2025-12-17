# Discovery Phase

The goal is to understand what we're building through natural conversation.

## Question Flow

Ask questions one at a time. Listen to the answer before asking the next.

### 1. Purpose/Goal
Start broad, then narrow:
- "What's the end goal of this workflow?"
- "What problem does this solve?"
- "What does success look like?"

### 2. Current Process (if replacing manual work)
- "Is this something done manually today?"
- If yes: "Walk me through the current steps"
- "What's painful about the current process?"
- "What takes the most time?"

### 3. Inputs
Offer options rather than open-ended:
- "Where does the data come from?"
  - Files you already have (CSV, JSON, PDF, etc.)
  - An API you'll call
  - Web scraping or search
  - Manual entry
  - Combination

Then drill down:
- "What format is the data in?"
- "How often does new data arrive?"
- "Is there an example file I can look at?"

### 4. Outputs
- "What's the end result?"
  - Transformed data files
  - Reports or summaries
  - Actions taken (emails sent, records created)
  - Notifications

Then specifics:
- "What format should the output be?"
- "Where does it need to go?"
- "Who or what consumes this output?"

### 5. Constraints
- "Any limitations I should know about?"
  - Cost (API fees, rate limits)
  - Time (must complete within X hours)
  - Tools (must use specific software)
  - Compliance (data handling rules)

## Writing to Spec

After each major section, update `project_spec.md` and validate:

```markdown
## Purpose
[What you understood]

Does this capture it correctly?
```

Wait for confirmation before moving to next section.

## Detecting Complexity

As you discover requirements, flag items that need brainstorming:
- Steps with multiple possible approaches
- Data sources you're not sure will work
- Transformations that seem complex

These become inputs to the Brainstorming phase.
