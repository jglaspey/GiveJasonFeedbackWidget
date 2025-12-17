# Autonomous Learning Framework - Architecture Design

## Vision

An autonomous system that uses two Claude Code instances (Dev and Tester) to systematically learn Claude Code and Agent SDK features through TDD-style experimentation, accumulating bulletproof knowledge in a database.

**Inspired by:**
- Your manual settings.json testing process
- Simon Willison's async code research approach
- TDD methodology for skill development

## Core Architecture

### Two-Instance Pattern

```
┌─────────────────────────────────────────────────────────────┐
│                    Test Orchestrator                        │
│                  (Python Script)                            │
│                                                             │
│  ┌──────────────────────┐      ┌──────────────────────┐   │
│  │   Dev Instance       │      │   Tester Instance    │   │
│  │   (Claude Code)      │      │   (Claude Code)      │   │
│  │                      │      │                      │   │
│  │  - Design tests      │◄────►│  - Run tests         │   │
│  │  - Analyze results   │      │  - Record results    │   │
│  │  - Update knowledge  │      │  - Clean env         │   │
│  │  - Generate hypotheses│     │  - Restart as needed │   │
│  └──────────────────────┘      └──────────────────────┘   │
│           │                              │                  │
│           ▼                              ▼                  │
│  ┌────────────────────────────────────────────────────┐   │
│  │           Shared Filesystem                        │   │
│  │  - Test plans (YAML)                              │   │
│  │  - Test results (JSON)                            │   │
│  │  - Knowledge base (SQLite)                        │   │
│  └────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Directory Structure

```
agent_dev_harness/
├── learning_framework/
│   ├── orchestrator.py              # Main orchestration script
│   ├── dev_instance.py              # Dev instance manager
│   ├── tester_instance.py           # Tester instance manager
│   │
│   ├── test_plans/                  # What to learn
│   │   ├── skills_invocation.yaml
│   │   ├── custom_tools.yaml
│   │   ├── hooks_integration.yaml
│   │   └── mcp_servers.yaml
│   │
│   ├── test_results/                # Findings from tests
│   │   ├── skills_invocation/
│   │   │   ├── 2025-01-15_143022.json
│   │   │   └── 2025-01-15_150433.json
│   │   └── custom_tools/
│   │       └── 2025-01-15_144512.json
│   │
│   ├── knowledge_base.db            # SQLite database
│   │
│   ├── tester_workspace/            # Isolated workspace for tester
│   │   ├── .claude/
│   │   │   ├── settings.json       # Modified by Dev instance
│   │   │   └── skills/             # Test skills
│   │   └── test_files/             # Files for testing
│   │
│   └── prompts/                     # Isolated prompts for instances
│       ├── dev_analyze_results.txt
│       ├── dev_create_hypothesis.txt
│       └── tester_run_experiment.txt
```

## Knowledge Base Schema

### SQLite Database: `knowledge_base.db`

```sql
-- Features being learned
CREATE TABLE features (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,        -- e.g., 'skills_invocation'
    description TEXT,
    category TEXT,                     -- e.g., 'claude-code', 'agent-sdk'
    confidence_score REAL DEFAULT 0.0, -- 0.0 to 1.0
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Individual experiments/tests
CREATE TABLE experiments (
    id INTEGER PRIMARY KEY,
    feature_id INTEGER NOT NULL,
    hypothesis TEXT NOT NULL,          -- What we're testing
    configuration TEXT NOT NULL,       -- JSON of test config
    expected_outcome TEXT,
    actual_outcome TEXT,
    success BOOLEAN,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    FOREIGN KEY (feature_id) REFERENCES features(id)
);

-- Patterns discovered
CREATE TABLE patterns (
    id INTEGER PRIMARY KEY,
    feature_id INTEGER NOT NULL,
    pattern_name TEXT NOT NULL,
    description TEXT NOT NULL,
    evidence TEXT,                     -- JSON array of experiment IDs
    confidence_score REAL DEFAULT 0.0,
    examples TEXT,                     -- JSON array of examples
    edge_cases TEXT,                   -- JSON array of edge cases
    discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (feature_id) REFERENCES features(id)
);

-- Gotchas and pitfalls discovered
CREATE TABLE gotchas (
    id INTEGER PRIMARY KEY,
    feature_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    how_to_avoid TEXT,
    severity TEXT CHECK(severity IN ('low', 'medium', 'high', 'critical')),
    discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (feature_id) REFERENCES features(id)
);

-- Best practices learned
CREATE TABLE best_practices (
    id INTEGER PRIMARY KEY,
    feature_id INTEGER NOT NULL,
    practice TEXT NOT NULL,
    rationale TEXT,
    when_to_use TEXT,
    examples TEXT,                     -- JSON array
    confidence_score REAL DEFAULT 0.0,
    FOREIGN KEY (feature_id) REFERENCES features(id)
);
```

## Test Plan Schema

### YAML Format: `test_plans/skills_invocation.yaml`

```yaml
feature:
  name: skills_invocation
  description: Understanding how and when skills are automatically invoked
  category: claude-code

learning_goals:
  - Determine what makes a skill description effective
  - Understand interaction between skills and hooks
  - Identify keywords that trigger invocation
  - Test edge cases where skills aren't invoked

hypotheses:
  - id: h1
    statement: "Skills with detailed 'when_to_use' sections are invoked more reliably"
    experiments:
      - minimal_description
      - detailed_symptoms
      - keyword_rich

  - id: h2
    statement: "Skills work independently of hooks - hooks don't affect invocation"
    experiments:
      - skill_only
      - hook_only
      - skill_plus_hook

experiments:
  - id: minimal_description
    hypothesis_id: h1
    description: Test skill with minimal description
    setup:
      skill_config:
        name: test-skill-minimal
        description: "Does a thing"
        when_to_use: "Use this"
      test_files:
        - path: test.txt
          content: "test content"
    test_scenarios:
      - user_prompt: "Please analyze test.txt using the test skill"
        expected: skill_invoked
      - user_prompt: "Analyze test.txt"
        expected: skill_not_invoked
    success_criteria:
      - skill_invocation_rate > 0.5

  - id: detailed_symptoms
    hypothesis_id: h1
    description: Test skill with detailed symptoms and keywords
    setup:
      skill_config:
        name: test-skill-detailed
        description: "Analyzes text files for patterns"
        when_to_use: |
          - Analyzing text files
          - Looking for patterns
          - Symptoms: file analysis, pattern detection
          - Keywords: analyze, review, inspect, pattern
      test_files:
        - path: test.txt
          content: "test content"
    test_scenarios:
      - user_prompt: "Analyze test.txt for patterns"
        expected: skill_invoked
      - user_prompt: "Review test.txt"
        expected: skill_invoked
      - user_prompt: "Look at test.txt"
        expected: unknown
    success_criteria:
      - skill_invocation_rate > 0.8

success_metrics:
  overall:
    - "All hypotheses tested"
    - "Confidence score >= 0.8 for discovered patterns"
    - "At least 3 edge cases documented"

  knowledge_quality:
    - "Can write bulletproof skill descriptions"
    - "Can predict invocation behavior"
    - "Can avoid common pitfalls"
```

## Test Result Schema

### JSON Format: `test_results/skills_invocation/2025-01-15_143022.json`

```json
{
  "timestamp": "2025-01-15T14:30:22Z",
  "feature": "skills_invocation",
  "experiment_id": "detailed_symptoms",
  "hypothesis_id": "h1",
  "configuration": {
    "skill_config": {
      "name": "test-skill-detailed",
      "description": "Analyzes text files for patterns",
      "when_to_use": "..."
    }
  },
  "results": [
    {
      "scenario": "Analyze test.txt for patterns",
      "expected": "skill_invoked",
      "actual": "skill_invoked",
      "success": true,
      "evidence": {
        "transcript_excerpt": "...",
        "tool_calls": ["Task(test-skill-detailed)"]
      }
    },
    {
      "scenario": "Review test.txt",
      "expected": "skill_invoked",
      "actual": "skill_not_invoked",
      "success": false,
      "evidence": {
        "transcript_excerpt": "...",
        "tool_calls": ["Read(test.txt)"]
      }
    }
  ],
  "summary": {
    "success_rate": 0.5,
    "met_success_criteria": false,
    "insights": [
      "Keyword 'analyze' triggered invocation",
      "Keyword 'review' did not trigger invocation",
      "May need to add 'review' to skill description"
    ],
    "next_steps": [
      "Test with 'review' added to keywords",
      "Try more synonyms: inspect, examine, check"
    ]
  }
}
```

## Learning Cycle Implementation

### Phase 1: Initialization

**Script:** `orchestrator.py`

1. Load test plan from YAML
2. Initialize knowledge base (if needed)
3. Start Dev instance (Claude Code in dev harness)
4. Start Tester instance (Claude Code in tester_workspace)

### Phase 2: Test Design (Dev Instance)

**Prompt:** `prompts/dev_create_hypothesis.txt`

```
You are a test designer for learning Claude Code features systematically.

Current Feature: {feature_name}
Description: {feature_description}

Test Plan: {test_plan_yaml}

Your job:
1. Review the test plan and hypotheses
2. Design the next experiment to run
3. Create the configuration for Tester instance
4. Specify exactly what to test and how to measure success

Output a JSON configuration that Tester can execute.
```

Dev instance outputs:
- Experiment configuration (JSON)
- Expected outcomes
- Success criteria

### Phase 3: Environment Preparation

**Script:** `orchestrator.py`

1. Parse Dev instance output
2. Modify `tester_workspace/.claude/settings.json` with test config
3. Create test skills in `tester_workspace/.claude/skills/`
4. Prepare test files in `tester_workspace/test_files/`
5. Restart Tester instance (to load new config)

### Phase 4: Test Execution (Tester Instance)

**Prompt:** `prompts/tester_run_experiment.txt`

```
You are a test executor. Run the experiment exactly as specified.

Experiment: {experiment_config}

For each test scenario:
1. Execute the user prompt
2. Record what happened
3. Note which tools were called
4. Check if expected outcome occurred

Output structured JSON results for each scenario.
```

Tester instance:
- Runs each test scenario
- Records outcomes
- Saves results to `test_results/`

### Phase 5: Analysis (Dev Instance)

**Prompt:** `prompts/dev_analyze_results.txt`

```
You are a test analyst. Analyze the experiment results.

Experiment: {experiment_id}
Expected: {expected_outcomes}
Actual Results: {test_results_json}

Your job:
1. Compare expected vs actual outcomes
2. Identify patterns in the results
3. Note any surprises or unexpected behavior
4. Extract insights and learnings
5. Determine confidence level in findings
6. Suggest next experiments

Update the knowledge base with your findings.
```

Dev instance:
- Analyzes results
- Updates knowledge_base.db
- Generates next hypothesis or refines current one

### Phase 6: Knowledge Accumulation

**Script:** `orchestrator.py`

1. Parse Dev instance analysis
2. Insert/update records in knowledge_base.db:
   - Add experiment results
   - Update patterns
   - Document gotchas
   - Record best practices
   - Update confidence scores

### Phase 7: Iteration Decision

**Logic in orchestrator.py:**

```python
if all_hypotheses_tested and confidence_high:
    # Move to next feature
    feature = get_next_feature()
elif current_hypothesis_needs_more_testing:
    # Design new experiment for same hypothesis
    refine_experiment()
elif hypothesis_validated or hypothesis_rejected:
    # Move to next hypothesis
    next_hypothesis()
else:
    # Continue testing current hypothesis
    iterate_experiment()
```

## Implementation Files

### 1. `learning_framework/orchestrator.py`

Main orchestration script:

```python
#!/usr/bin/env python3
# ABOUTME: Main orchestrator for autonomous learning framework
# ABOUTME: Manages Dev and Tester instances, coordinates learning cycle

import asyncio
import json
import sqlite3
import yaml
from pathlib import Path
from datetime import datetime
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions

class LearningOrchestrator:
    def __init__(self, harness_root: Path):
        self.harness_root = harness_root
        self.learning_dir = harness_root / 'learning_framework'
        self.db_path = self.learning_dir / 'knowledge_base.db'
        self.test_plans_dir = self.learning_dir / 'test_plans'
        self.test_results_dir = self.learning_dir / 'test_results'
        self.tester_workspace = self.learning_dir / 'tester_workspace'

        self._init_database()

    def _init_database(self):
        """Initialize SQLite database with schema."""
        conn = sqlite3.connect(self.db_path)
        # Create tables from schema
        conn.executescript('''
            -- (schema SQL from above)
        ''')
        conn.commit()
        conn.close()

    async def run_learning_cycle(self, feature_name: str):
        """Run complete learning cycle for a feature."""

        # 1. Load test plan
        test_plan = self._load_test_plan(feature_name)

        # 2. Initialize feature in DB
        feature_id = self._init_feature(test_plan)

        # 3. For each hypothesis
        for hypothesis in test_plan['hypotheses']:
            print(f"\nTesting hypothesis: {hypothesis['statement']}")

            # 4. For each experiment
            for experiment_id in hypothesis['experiments']:
                experiment = self._get_experiment(test_plan, experiment_id)

                # 5. Dev designs test
                config = await self._dev_design_test(experiment)

                # 6. Prepare tester environment
                self._prepare_tester_env(config)

                # 7. Tester runs experiment
                results = await self._tester_run_experiment(config)

                # 8. Dev analyzes results
                analysis = await self._dev_analyze_results(results)

                # 9. Update knowledge base
                self._update_knowledge_base(feature_id, experiment, results, analysis)

                # 10. Check if we should continue
                if self._should_stop(feature_id):
                    print(f"Feature {feature_name} learning complete!")
                    return

    async def _dev_design_test(self, experiment: dict) -> dict:
        """Dev instance designs the test configuration."""
        # Implementation using ClaudeSDKClient
        pass

    async def _tester_run_experiment(self, config: dict) -> dict:
        """Tester instance runs the experiment."""
        # Implementation using ClaudeSDKClient
        pass

    async def _dev_analyze_results(self, results: dict) -> dict:
        """Dev instance analyzes experiment results."""
        # Implementation using ClaudeSDKClient
        pass

    # ... (additional methods)

async def main():
    harness_root = Path(__file__).parent.parent
    orchestrator = LearningOrchestrator(harness_root)

    # Start learning about skills invocation
    await orchestrator.run_learning_cycle('skills_invocation')

if __name__ == '__main__':
    asyncio.run(main())
```

### 2. `learning_framework/dev_instance.py`

Wrapper for Dev Claude Code instance:

```python
#!/usr/bin/env python3
# ABOUTME: Dev instance manager - designs tests and analyzes results
# ABOUTME: Uses Agent SDK to interact with Claude in dev harness context

import asyncio
from pathlib import Path
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions

class DevInstance:
    """Manages the Dev Claude Code instance."""

    def __init__(self, harness_root: Path):
        self.harness_root = harness_root
        self.prompts_dir = harness_root / 'learning_framework' / 'prompts'

        self.options = ClaudeAgentOptions(
            cwd=str(harness_root),
            permission_mode='acceptEdits',
            system_prompt=self._load_system_prompt()
        )

    def _load_system_prompt(self) -> str:
        """Load system prompt for Dev instance."""
        return '''
You are a systematic test designer and analyst for learning Claude Code features.

Your responsibilities:
1. Design experiments to test hypotheses
2. Analyze experiment results objectively
3. Update knowledge base with findings
4. Generate new hypotheses based on learnings

Be rigorous, scientific, and thorough.
'''

    async def design_experiment(self, test_plan: dict, experiment: dict) -> dict:
        """Ask Dev instance to design next experiment."""
        prompt_template = (self.prompts_dir / 'dev_create_hypothesis.txt').read_text()
        prompt = prompt_template.format(
            feature_name=test_plan['feature']['name'],
            feature_description=test_plan['feature']['description'],
            test_plan_yaml=yaml.dump(test_plan),
            experiment=yaml.dump(experiment)
        )

        async with ClaudeSDKClient(options=self.options) as client:
            responses = []
            async for message in client.send(prompt):
                if message.get('type') == 'text':
                    responses.append(message.get('content', ''))

            # Parse JSON from response
            return self._parse_json_response('\n'.join(responses))

    async def analyze_results(self, experiment: dict, results: dict) -> dict:
        """Ask Dev instance to analyze experiment results."""
        # Similar implementation
        pass

    def _parse_json_response(self, response: str) -> dict:
        """Extract JSON from Claude's response."""
        # Implementation to extract JSON
        pass
```

### 3. `learning_framework/tester_instance.py`

Wrapper for Tester Claude Code instance:

```python
#!/usr/bin/env python3
# ABOUTME: Tester instance manager - runs experiments in isolated environment
# ABOUTME: Uses Agent SDK to interact with Claude in tester workspace

import asyncio
from pathlib import Path
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions

class TesterInstance:
    """Manages the Tester Claude Code instance."""

    def __init__(self, tester_workspace: Path):
        self.workspace = tester_workspace
        self.prompts_dir = tester_workspace.parent / 'prompts'

        self.options = ClaudeAgentOptions(
            cwd=str(tester_workspace),
            permission_mode='acceptEdits',
            settings_path=str(tester_workspace / '.claude' / 'settings.json'),
            system_prompt=self._load_system_prompt()
        )

    def _load_system_prompt(self) -> str:
        """Load system prompt for Tester instance."""
        return '''
You are a precise test executor. Run experiments exactly as specified.

Your responsibilities:
1. Execute each test scenario precisely
2. Record outcomes objectively
3. Note which tools/skills were invoked
4. Report results in structured format

Be thorough and accurate in your observations.
'''

    async def run_experiment(self, config: dict) -> dict:
        """Run experiment and return structured results."""
        prompt_template = (self.prompts_dir / 'tester_run_experiment.txt').read_text()
        prompt = prompt_template.format(
            experiment_config=json.dumps(config, indent=2)
        )

        async with ClaudeSDKClient(options=self.options) as client:
            responses = []
            async for message in client.send(prompt):
                if message.get('type') == 'text':
                    responses.append(message.get('content', ''))

            # Parse structured results
            return self._parse_results('\n'.join(responses))

    def _parse_results(self, response: str) -> dict:
        """Extract structured results from response."""
        # Implementation
        pass
```

## Usage Example

```bash
# Start the learning framework
cd learning_framework

# Learn about skills invocation
python orchestrator.py --feature skills_invocation

# Learn about custom tools
python orchestrator.py --feature custom_tools

# Query knowledge base
python query_knowledge.py --feature skills_invocation --show-patterns
```

## Output: Generated Skill

After learning, the framework can generate bulletproof skills:

```markdown
---
name: Skills Invocation Mastery
description: Proven patterns for reliable skill invocation
confidence: 0.95
tested_scenarios: 47
version: 1.0.0
---

# Skills Invocation - Bulletproof Patterns

## Confidence Level: 95% (47 experiments)

### Pattern 1: Keyword-Rich Descriptions

**Discovery:** Skills with multiple synonyms in when_to_use are invoked 3x more reliably.

**Evidence:**
- Tested: 15 variations
- Success rate: minimal description (32%), keyword-rich (91%)

**Best Practice:**
```yaml
when_to_use: |
  - Analyzing code (synonyms: review, inspect, examine, audit, check)
  - Symptoms: need code analysis, want code review
  - Keywords: analyze, review, code, inspection
```

### Pattern 2: Skills + Hooks Work Independently

**Discovery:** Hooks don't affect skill invocation - they're orthogonal systems.

**Evidence:**
- Tested: 12 combinations
- Skills invoke regardless of hooks present

...
```

## Next Steps

1. **Implement orchestrator.py** - Core coordination logic
2. **Create test plans** - Start with skills_invocation
3. **Build instance managers** - Dev and Tester wrappers
4. **Test manually first** - Verify two-instance pattern works
5. **Iterate and refine** - Improve based on learnings

## Success Criteria

The framework is successful when:
1. ✅ Can run experiments autonomously (no manual intervention)
2. ✅ Produces reliable, structured findings
3. ✅ Updates knowledge base automatically
4. ✅ Generated skills have high confidence scores
5. ✅ Can predict behavior based on learnings
6. ✅ Discovers edge cases automatically

## Version History

- 1.0.0: Initial architecture design for autonomous learning framework
