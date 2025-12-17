# Validation Phase

Prove out risky assumptions before building the full workflow.

## Purpose

Validation answers: "Can we actually do this the way we think we can?"

Examples:
- "Does the Apollo API return company employee count?" (Test it)
- "Can we parse these PDFs reliably?" (Try a few)
- "Will the rate limits work for our volume?" (Calculate and test)

## The Validation Directory

All validation artifacts go in `projects/<name>/validation/`:

```
validation/
├── test_apollo_api.py      # Script that tested API
├── test_pdf_parsing.py     # Script that tested PDF extraction
├── sample_data/            # Test inputs used
│   └── example.pdf
└── results.md              # Summary of what we learned
```

## Writing Validation Scripts

Keep scripts simple and focused:

```python
# ABOUTME: Tests whether Apollo API returns employee count field
# ABOUTME: Run with: python test_apollo_api.py

import os
from dotenv import load_dotenv

load_dotenv()

def test_apollo_employee_count():
    """Test if Apollo API returns employee count for a company."""
    # Minimal code to test the specific assumption
    api_key = os.getenv("APOLLO_API_KEY")

    # Make one API call
    # Check if response has what we need
    # Print clear result

    print("SUCCESS: Apollo API returns employee_count field")
    # or
    print("FAILURE: employee_count not in response. Available fields: ...")

if __name__ == "__main__":
    test_apollo_employee_count()
```

## Recording Results

Update `validation/results.md`:

```markdown
# Validation Results

## Apollo API - Employee Count (2024-01-15)

**Question**: Does Apollo API return company employee count?

**Script**: `test_apollo_api.py`

**Result**: PARTIAL SUCCESS
- Returns `employee_count` for ~60% of companies
- Missing for smaller companies
- Alternative: `employee_range` field available for 90%

**Decision**: Use `employee_range` as primary, `employee_count` as fallback

---

## PDF Parsing - Invoice Data (2024-01-15)

**Question**: Can we extract line items from PDF invoices?

**Script**: `test_pdf_parsing.py`

**Result**: SUCCESS
- Tested 5 sample invoices
- PyMuPDF extracted tables correctly for all
- Processing time: ~0.3s per page

**Decision**: Proceed with PyMuPDF approach
```

## Update the Spec

Add validation results to `project_spec.md`:

```markdown
## Validation Results

| Assumption | Result | Impact |
|------------|--------|--------|
| Apollo has employee count | Partial - use employee_range | Adjusted filtering logic |
| PDF tables extractable | Success | Proceed as planned |
| Rate limit sufficient | Success - 100/min, need 50 | No changes needed |
```

## When to Stop Validating

Stop when:
- All critical assumptions are tested
- You have fallback plans for partial successes
- Remaining uncertainty is acceptable

Move to scaffolding when you're confident the approach will work.

## Handling Failures

When validation fails:

1. **Document what you learned** - This is valuable even if negative
2. **Return to brainstorming** - What's the alternative?
3. **Test the alternative** - Don't assume it works either
4. **Consider abandoning** - Sometimes the project isn't feasible

It's better to discover infeasibility now than after building half the workflow.
