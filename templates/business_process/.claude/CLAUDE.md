# [Process Name] - Business Process Agent

You are helping automate [describe the business process - e.g., "data extraction from PDFs", "daily report generation", "customer data enrichment"].

## Process Goal

[Describe what this process accomplishes]

Example:
> Extract structured data from incoming PDF invoices, validate against business rules, and output to JSON format for import into accounting system.

## Input/Output

**Input:**
- Location: `functional/config/` or passed as arguments
- Format: [e.g., CSV files, API responses, PDFs]
- Example: [provide example]

**Output:**
- Location: `outputs/run_YYYY-MM-DD_HHMMSS/results/`
- Format: [e.g., JSON, CSV, reports]
- Structure: [describe output format]

## Process-Specific Rules

### [Add Custom Rules for This Process]

Example:
- Validate all email addresses before processing
- Skip items with missing required fields
- Items that fail validation go to errors/ with reason
- Maximum 1000 items per run (create new run for more)

## Prompts Available

[List the prompts in functional/prompts/ and when to use them]

Example:
- `extract_invoice_data.txt`: Extract structured data from invoice text
- `validate_data.txt`: Check if extracted data meets business rules
- `generate_summary.txt`: Create human-readable summary of run

## Error Handling

[Process-specific error handling rules]

Example:
- PDF parsing errors: Log to errors/, continue with next item
- Validation failures: Store in errors/ with validation details
- API failures: Retry 3 times with exponential backoff

## Logging Requirements

- Log each item processed with status (completed/failed)
- Log validation failures with specific rules violated
- Summary statistics at end of run

## Safety Rules

[Any safety/compliance requirements]

Example:
- Never expose PII in logs
- Redact customer emails in error logs
- Don't write to production database (outputs only)

---

## Standard Agent Development Rules

You MUST follow the patterns in the dev harness:

### Project Structure
- Functional code in `functional/`
- Outputs in `outputs/run_TIMESTAMP/`
- Never mix code and outputs
- Test scripts in `test_scripts/` only

### Prompts
- All prompts in `functional/prompts/`
- Load prompts from files, don't embed in code
- See agent-project-setup skill for pattern

### Logging
- Every run creates timestamp directory
- Progress logged to `outputs/run_XXX/logs/`
- Errors isolated in `outputs/run_XXX/errors/`
- See agent-project-setup skill for logging pattern

### Resumability
- Support resuming from last completed item
- Track progress in logs/progress.jsonl
- Don't re-process completed items
- See agent-project-setup skill for resumability pattern

### Agent SDK
- Use Claude Agent SDK, not Anthropic API
- Leverages Claude subscription
- See agent-sdk-basics skill for usage

### Paths
- No hardcoded machine-specific paths
- Use relative paths from project root
- Machine-specific config in .env
- See agent-project-setup skill

### Permissions
- This process has restrictive permissions (see settings.json)
- Can read from config/ and data/
- Can only write to outputs/
- Cannot modify functional code
- See settings-json-patterns skill

For detailed patterns, reference the skills in the dev harness:
- agent-project-setup
- settings-json-patterns
- agent-sdk-basics
- parallel-processing (if needed)
