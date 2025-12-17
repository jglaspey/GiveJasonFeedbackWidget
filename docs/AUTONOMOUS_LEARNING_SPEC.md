# Autonomous Learning Framework - Technical Specification

## Inspiration Sources

1. **Your Settings.json Testing**: Manual dual-instance learning
2. **Obra's Writing Skills TDD**: RED-GREEN-REFACTOR for documentation
3. **Simon Willison's Async Code Research**: Parallel exploration with consolidation

## The Core Insight

You discovered an effective learning pattern manually:
```
Dev Instance → Designs test → Updates tester config → Restart tester
User → Tells tester to run test → Tester records results
User → Tells dev to read results → Dev updates test plan
Repeat until comprehensive understanding
```

We can automate this entire cycle!

## Architecture

### Component 1: Test Orchestrator

**File:** `learning_framework/test_orchestrator.py`

**Purpose:** Manages the learning cycle without human intervention

**Key Functions:**

```python
class LearningOrchestrator:
    def __init__(self):
        self.dev_session = None      # Agent SDK session for Dev instance
        self.tester_session = None   # Agent SDK session for Tester instance
        self.knowledge_db = KnowledgeBase()
        self.current_test_plan = None

    async def run_learning_cycle(self, feature_to_learn: str):
        """
        Complete RED-GREEN-REFACTOR cycle for a feature
        """
        # RED: Establish baseline without skill
        baseline = await self.run_baseline_tests(feature_to_learn)

        # GREEN: Create skill, test until passing
        skill = await self.dev_creates_skill(baseline)
        while not await self.skill_tests_pass(skill):
            skill = await self.dev_refines_skill(skill)

        # REFACTOR: Find edge cases, close loopholes
        while edge_cases := await self.find_edge_cases(skill):
            skill = await self.dev_handles_edge_cases(skill, edge_cases)

        # FINALIZE: Store in knowledge base
        await self.knowledge_db.store_skill(skill)

    async def run_baseline_tests(self, feature: str):
        """
        Test Tester instance WITHOUT the skill to see natural behavior
        """
        test_plan = await self.dev_creates_baseline_plan(feature)

        # Configure Tester WITHOUT skill
        await self.configure_tester(skills=[], settings={})

        # Run tests and capture behavior
        results = []
        for test_case in test_plan.test_cases:
            result = await self.tester_executes(test_case)
            results.append({
                'test': test_case,
                'behavior': result.transcript,
                'outcome': result.success,
                'rationalizations': self.extract_rationalizations(result)
            })

        return BaselineResults(test_plan, results)

    async def dev_creates_skill(self, baseline: BaselineResults):
        """
        Dev analyzes baseline and creates skill to fix issues
        """
        prompt = f"""
        You tested feature: {baseline.feature}

        Baseline behavior (WITHOUT skill):
        {format_baseline(baseline)}

        Following the TDD-for-skills approach, create a skill that:
        1. Addresses the specific failures observed
        2. Uses keywords from error messages
        3. Includes symptoms in when_to_use
        4. Provides clear examples

        Write the skill to: {self.skills_dir}/{baseline.feature}/SKILL.md
        """

        await self.dev_session.send_message(prompt)
        # Wait for skill file to be written
        return self.load_skill(baseline.feature)
```

### Component 2: Test Plan Structure

**File:** `learning_framework/test_plans/feature_template.yaml`

```yaml
feature: "Feature to learn (e.g., 'skills_invocation')"
version: "1.0.0"
learning_goals:
  - "What we want to understand"
  - "Questions to answer"
  - "Behaviors to document"

hypotheses:
  - id: "H1"
    statement: "Skills with detailed when_to_use descriptions are invoked more reliably"
    test_approach: "Create two skills, vary only the description detail"

  - id: "H2"
    statement: "Skills are more likely invoked when keywords match user message"
    test_approach: "Test same skill with messages containing/lacking keywords"

experiments:
  - id: "E1"
    hypothesis: "H1"
    configuration:
      skill_name: "test_skill_minimal"
      when_to_use: "For testing"
      description: "A test skill"
    test_cases:
      - user_message: "Can you run a test?"
        expected_behavior: "Should invoke skill"
        success_criteria: "Skill appears in transcript"
      - user_message: "Do something for me"
        expected_behavior: "May not invoke skill"
        success_criteria: "Document what happens"

  - id: "E2"
    hypothesis: "H1"
    configuration:
      skill_name: "test_skill_detailed"
      when_to_use: |
        When user asks to test, validate, or verify something.
        Symptoms: Mentions "test", "check", "verify" in message.
        Use when: Building or debugging features.
      description: "Validates functionality through systematic testing"
    test_cases:
      - user_message: "Can you run a test?"
        expected_behavior: "Should definitely invoke skill"
        success_criteria: "Skill invoked within 2 messages"

metrics:
  - name: "invocation_rate"
    formula: "invoked_cases / total_cases"
    threshold: "> 0.8 for detailed, < 0.5 for minimal"

  - name: "time_to_invocation"
    formula: "messages until skill invoked"
    threshold: "< 3 messages for detailed"

edge_cases_to_discover:
  - "What if multiple skills match?"
  - "What if skill keywords conflict with natural conversation?"
  - "Does skill invocation affect performance?"
  - "Can user request override skill usage?"

post_experiment_questions:
  - "Were hypotheses confirmed?"
  - "What unexpected behaviors emerged?"
  - "What new questions arose?"
  - "Confidence level in findings (1-10)?"
```

### Component 3: Tester Instance Manager

**File:** `learning_framework/tester_manager.py`

```python
class TesterInstance:
    """
    Manages a fresh Claude Code instance for testing
    """
    def __init__(self, test_workspace: Path):
        self.workspace = test_workspace
        self.session = None

    async def configure(self,
                       skills: List[Skill],
                       settings: Dict,
                       mcp_servers: Optional[Dict] = None):
        """
        Set up Tester environment
        """
        # Write skills to .claude/skills/
        for skill in skills:
            skill_path = self.workspace / ".claude" / "skills" / skill.name
            skill_path.mkdir(parents=True, exist_ok=True)
            (skill_path / "SKILL.md").write_text(skill.content)

        # Write settings.json
        settings_path = self.workspace / ".claude" / "settings.json"
        settings_path.write_text(json.dumps(settings, indent=2))

        # Write mcp.json if provided
        if mcp_servers:
            mcp_path = self.workspace / ".claude" / "mcp.json"
            mcp_path.write_text(json.dumps(mcp_servers, indent=2))

    async def start_session(self):
        """
        Start fresh Claude Code session in workspace
        """
        # This is the KEY QUESTION: Can we do this via Agent SDK?
        self.session = await create_claude_session(
            working_directory=self.workspace,
            model="claude-sonnet-4"
        )

    async def execute_test(self, test_case: TestCase) -> TestResult:
        """
        Run a test case and capture full behavior
        """
        # Send test message
        response = await self.session.send_message(test_case.user_message)

        # Capture full transcript
        transcript = await self.session.get_transcript()

        # Analyze what happened
        return TestResult(
            test_case=test_case,
            response=response,
            transcript=transcript,
            tools_used=self.extract_tools(transcript),
            skills_invoked=self.extract_skills(transcript),
            errors=self.extract_errors(transcript),
            success=self.evaluate_success(test_case, transcript)
        )

    async def reset(self):
        """
        Clean slate for next test
        """
        if self.session:
            await self.session.close()
        # Clear workspace or create new one

    def extract_skills(self, transcript: str) -> List[str]:
        """
        Identify which skills were invoked during test
        """
        # Look for skill invocation markers in transcript
        # This might require specific markers or patterns
        invoked = []
        for line in transcript.split('\n'):
            if 'Invoking skill:' in line or 'Using skill:' in line:
                skill_name = self.parse_skill_name(line)
                invoked.append(skill_name)
        return invoked
```

### Component 4: Knowledge Base

**File:** `learning_framework/knowledge_base.py`

**Schema:**

```sql
-- Features being learned
CREATE TABLE features (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    category TEXT,  -- 'claude-code', 'agent-sdk', 'patterns', etc.
    date_started TIMESTAMP,
    date_completed TIMESTAMP,
    confidence_score REAL  -- 0-10 scale
);

-- Test plans for features
CREATE TABLE test_plans (
    id INTEGER PRIMARY KEY,
    feature_id INTEGER REFERENCES features(id),
    version TEXT,
    yaml_content TEXT,  -- Full test plan YAML
    created_at TIMESTAMP
);

-- Individual experiments
CREATE TABLE experiments (
    id INTEGER PRIMARY KEY,
    test_plan_id INTEGER REFERENCES test_plans(id),
    experiment_id TEXT,  -- E1, E2, etc.
    hypothesis TEXT,
    configuration JSON,
    executed_at TIMESTAMP
);

-- Test results
CREATE TABLE test_results (
    id INTEGER PRIMARY KEY,
    experiment_id INTEGER REFERENCES experiments(id),
    test_case JSON,
    transcript TEXT,
    tools_used JSON,
    skills_invoked JSON,
    errors JSON,
    success BOOLEAN,
    notes TEXT
);

-- Discovered patterns
CREATE TABLE patterns (
    id INTEGER PRIMARY KEY,
    feature_id INTEGER REFERENCES features(id),
    pattern_type TEXT,  -- 'success', 'failure', 'edge_case', 'gotcha'
    description TEXT,
    example TEXT,
    discovered_at TIMESTAMP,
    confidence REAL
);

-- Skills created from learning
CREATE TABLE skills_created (
    id INTEGER PRIMARY KEY,
    feature_id INTEGER REFERENCES features(id),
    skill_name TEXT,
    version TEXT,
    file_path TEXT,
    created_at TIMESTAMP,
    bulletproof BOOLEAN  -- Passed all refactor tests?
);

-- Learning insights
CREATE TABLE insights (
    id INTEGER PRIMARY KEY,
    feature_id INTEGER REFERENCES features(id),
    insight_text TEXT,
    source TEXT,  -- 'baseline', 'green_phase', 'refactor_edge_case'
    importance INTEGER,  -- 1-5
    added_at TIMESTAMP
);
```

**Key Methods:**

```python
class KnowledgeBase:
    def store_baseline_results(self, feature, results):
        """Record what happened without skill"""

    def store_skill_test_results(self, skill, results):
        """Record what happened with skill"""

    def get_related_learnings(self, feature):
        """Find similar features we've learned"""

    def calculate_confidence(self, feature):
        """
        Confidence based on:
        - Number of tests passed
        - Edge cases covered
        - Time since last test
        - Consistency of results
        """

    def generate_skill_from_learnings(self, feature):
        """Create skill content from accumulated knowledge"""
```

### Component 5: Dev Instance Coordinator

**File:** `learning_framework/dev_coordinator.py`

```python
class DevCoordinator:
    """
    The Dev instance that designs tests and interprets results
    """
    async def design_baseline_tests(self, feature: str) -> TestPlan:
        """
        Given a feature to learn, create comprehensive test plan
        """
        prompt = f"""
        We want to deeply understand: {feature}

        Create a test plan following this structure:
        - What are we trying to learn?
        - What hypotheses should we test?
        - What experiments will test each hypothesis?
        - What edge cases might exist?
        - How will we measure success?

        Use the template at: learning_framework/test_plans/feature_template.yaml
        """

    async def analyze_baseline(self, results: List[TestResult]) -> Analysis:
        """
        Look at results and identify patterns
        """
        prompt = f"""
        We ran baseline tests (WITHOUT skill) for {feature}.

        Results:
        {format_results(results)}

        Analyze:
        1. What worked well naturally?
        2. What failed or was inconsistent?
        3. What rationalizations did Claude use?
        4. What patterns emerge?
        5. What would a skill need to address?
        """

    async def create_skill(self, feature: str, analysis: Analysis) -> Skill:
        """
        Write skill following TDD-for-skills methodology
        """

    async def refine_skill(self, skill: Skill, failures: List[TestResult]) -> Skill:
        """
        Skill didn't pass all tests - improve it
        """

    async def design_edge_case_tests(self, skill: Skill) -> List[TestCase]:
        """
        After skill passes basic tests, find edge cases
        """
        prompt = f"""
        Skill {skill.name} passes all basic tests.

        Now find edge cases:
        - Boundary conditions
        - Conflicting scenarios
        - Performance edge cases
        - User override scenarios
        - Multi-skill interactions

        Create 5-10 edge case tests.
        """

    async def evaluate_bulletproof(self, skill: Skill, all_results: List[TestResult]) -> bool:
        """
        Determine if skill is ready for production use
        """
        criteria = {
            'success_rate': sum(r.success for r in all_results) / len(all_results),
            'edge_cases_covered': len([r for r in all_results if r.is_edge_case]),
            'consistency': self.calculate_consistency(all_results),
            'rationalizations_eliminated': not any(r.has_rationalizations for r in all_results)
        }

        return all(v > threshold for v, threshold in criteria.items())
```

## Usage Flow

### Step 1: Initialize Learning for a Feature

```bash
python -m learning_framework.orchestrator learn "skills_invocation"
```

### Step 2: Orchestrator Runs Automatically

```
1. Dev: Creates test plan
2. Dev: Prepares Tester environment (no skill)
3. Orchestrator: Starts Tester instance
4. Tester: Runs all baseline tests
5. Tester: Records results to DB
6. Dev: Reads results, creates skill
7. Dev: Prepares Tester with skill
8. Orchestrator: Restarts Tester instance
9. Tester: Runs tests with skill
10. Tester: Records results to DB
11. Dev: Compares baseline vs. skill results
    - If not passing: Refine skill, goto 7
    - If passing: Continue to edge cases
12. Dev: Designs edge case tests
13. Repeat steps 7-11 with edge cases
14. Dev: Evaluates if bulletproof
    - If yes: Store in knowledge base, done
    - If no: More edge cases, goto 12
```

### Step 3: Review Results

```bash
python -m learning_framework.report "skills_invocation"
```

Generates markdown report:
- What we learned
- Skill created
- Test results summary
- Confidence score
- Open questions

## Critical Implementation Questions

### Q1: Can Agent SDK control multiple Claude Code instances?

**Need to test:**
```python
# Can we do this?
dev_session = await agent_sdk.create_session(
    working_directory="/path/to/dev",
    model="claude-sonnet-4"
)

tester_session = await agent_sdk.create_session(
    working_directory="/path/to/tester",
    model="claude-sonnet-4"
)

# Run them independently?
dev_response = await dev_session.send_message("Analyze this...")
tester_response = await tester_session.send_message("Run test...")
```

**If YES:** Full automation possible
**If NO:** Semi-automation:
- Orchestrator writes commands
- Human executes in separate windows
- Orchestrator parses results

### Q2: How to capture skill invocation from transcript?

Options:
1. Parse transcript text (fragile)
2. Add logging to Claude Code (need to modify)
3. Use hooks to log skill usage
4. Monitor which files get read (skills are read when invoked)

### Q3: How to measure "bulletproof"?

Proposed formula:
```
confidence = (
    0.4 * test_pass_rate +
    0.2 * edge_cases_covered +
    0.2 * result_consistency +
    0.1 * time_stability +
    0.1 * expert_review
)

bulletproof = confidence > 0.85
```

## Next Steps to Validate Approach

1. **Minimal Test**: Can Agent SDK control two instances?
   - Create simple script
   - Two sessions with different contexts
   - Verify independence

2. **Settings.json Skill**: Use existing data
   - You already have baseline + findings
   - Create the skill manually
   - Test with orchestrator

3. **First Full Cycle**: Pick simplest feature
   - Run complete RED-GREEN-REFACTOR
   - Document what works/doesn't
   - Refine orchestrator

4. **Scale Up**: Add more features
   - Skills invocation
   - Custom tools
   - Hooks
   - etc.

## Success Criteria

✅ Orchestrator runs without human intervention
✅ Produces reliable, documented findings
✅ Creates bulletproof skills
✅ Knowledge accumulates in database
✅ Can answer: "What do we know about X feature?"
✅ Skills improve with each learning cycle

## Timeline Estimate

- Week 1: Validate Agent SDK multi-instance control
- Week 2: Build basic orchestrator
- Week 3: Test with settings.json skill (have data!)
- Week 4: Refine based on learnings
- Week 5-8: Learn remaining features systematically
- Week 9: Documentation and templates
- Week 10: Validation with real business process

## Risk Mitigation

**Risk:** Can't control multiple instances
**Mitigation:** Semi-automated with human in loop

**Risk:** Skill invocation not detectable
**Mitigation:** Use hooks or file monitoring

**Risk:** Tests not reproducible
**Mitigation:** Seed random, control environment, retry 3x

**Risk:** Learning takes too long
**Mitigation:** Parallel experiments, prioritize high-value features
