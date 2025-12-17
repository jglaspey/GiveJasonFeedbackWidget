---
name: Prompt Isolation
description: When building agents with prompts that need frequent refinement, or when you want to version and A/B test prompts separately from code
when_to_use: |
  - Building agent with prompts
  - Need to refine prompts frequently
  - Want to version prompts separately from code
  - Symptoms: "prompts in Python strings", "can't A/B test prompts", "messy diffs"
  - Keywords: prompts, templates, isolation, refinement
version: 1.0.0
languages: all
---

# Prompt Isolation

## Overview

Prompts are the core of AI agents and change frequently during development. Embedding them in code makes iteration painful. This skill shows how to isolate prompts in separate files.

**Core principle:** Prompts in files, code references files.

## The Problem

### ❌ Prompts Embedded in Code

```python
def process_item(item):
    prompt = f"""
    You are a data analyst. Analyze the following item:

    Item ID: {item['id']}
    Data: {item['data']}

    Extract:
    - Key insights
    - Quality score (1-10)
    - Any anomalies

    Output JSON format:
    {{
        "insights": "...",
        "quality_score": X,
        "anomalies": ["..."]
    }}
    """

    response = call_claude(prompt)
    return response
```

**Problems:**
- Can't refine prompt without touching Python code
- Syntax highlighting doesn't work well for prompts
- Hard to A/B test different prompts
- Git diffs show Python + prompt mixed together
- Can't easily swap prompts

## The Solution

### ✅ Prompts in Separate Files

**File: functional/prompts/analyze_item.txt**
```
You are a data analyst. Analyze the following item:

Item ID: {item_id}
Data: {data}

Extract:
- Key insights
- Quality score (1-10)
- Any anomalies

Output JSON format:
{{
    "insights": "...",
    "quality_score": X,
    "anomalies": ["..."]
}}
```

**File: functional/scripts/process.py**
```python
from pathlib import Path

def load_prompt(name: str) -> str:
    """Load prompt from functional/prompts/ directory"""
    project_root = Path(__file__).parent.parent
    prompt_path = project_root / "prompts" / f"{name}.txt"
    return prompt_path.read_text()

def process_item(item):
    # Load prompt template
    prompt_template = load_prompt("analyze_item")

    # Format with data
    prompt = prompt_template.format(
        item_id=item['id'],
        data=item['data']
    )

    response = call_claude(prompt)
    return response
```

## Benefits

✅ **Easy refinement** - Edit prompt file, no code changes
✅ **Proper editing** - Use text editor for prompts
✅ **Clean diffs** - Git shows prompt changes separately
✅ **A/B testing** - Easy to swap prompts
✅ **Version control** - Track prompt evolution
✅ **Collaboration** - Prompt engineers can work independently

## Standard Pattern

### Directory Structure

```
functional/
├── prompts/
│   ├── analyze_item.txt
│   ├── validate_data.txt
│   └── generate_summary.txt
└── scripts/
    └── process.py
```

### Loading Helper

```python
from pathlib import Path
from typing import Optional

def load_prompt(name: str, prompts_dir: Optional[Path] = None) -> str:
    """
    Load prompt template from prompts directory

    Args:
        name: Prompt filename without .txt extension
        prompts_dir: Optional custom prompts directory

    Returns:
        Prompt template as string

    Raises:
        FileNotFoundError: If prompt doesn't exist
    """
    if prompts_dir is None:
        project_root = Path(__file__).parent.parent
        prompts_dir = project_root / "prompts"

    prompt_path = prompts_dir / f"{name}.txt"

    if not prompt_path.exists():
        raise FileNotFoundError(
            f"Prompt not found: {prompt_path}\n"
            f"Available prompts: {list(prompts_dir.glob('*.txt'))}"
        )

    return prompt_path.read_text()
```

### Usage Patterns

**Simple formatting:**
```python
prompt_template = load_prompt("analyze_item")
prompt = prompt_template.format(item_id="123", data="test")
```

**With dictionary:**
```python
prompt_template = load_prompt("analyze_item")
prompt = prompt_template.format(**item)  # Unpack item dict
```

**Multiple prompts:**
```python
analyze_prompt = load_prompt("analyze_item")
validate_prompt = load_prompt("validate_data")
summary_prompt = load_prompt("generate_summary")
```

## Advanced Patterns

### Prompt with Conditional Sections

**File: prompts/analyze_item_detailed.txt**
```
You are a data analyst.

Item ID: {item_id}
Data: {data}

{additional_context}

Extract:
- Key insights
- Quality score (1-10)
{extra_requirements}
```

**Usage:**
```python
prompt_template = load_prompt("analyze_item_detailed")

# Build conditional content
additional_context = ""
if item.get("priority") == "high":
    additional_context = "PRIORITY: This is a high-priority item."

extra_requirements = ""
if detailed:
    extra_requirements = "- Detailed breakdown\n- Confidence scores"

prompt = prompt_template.format(
    item_id=item['id'],
    data=item['data'],
    additional_context=additional_context,
    extra_requirements=extra_requirements
)
```

### Prompt Versioning

**Directory structure:**
```
functional/prompts/
├── analyze_item_v1.txt
├── analyze_item_v2.txt
└── analyze_item.txt  -> analyze_item_v2.txt (symlink or copy)
```

**A/B testing:**
```python
# Easy to swap versions
prompt = load_prompt("analyze_item_v1")  # Old version
prompt = load_prompt("analyze_item_v2")  # New version
prompt = load_prompt("analyze_item")     # Current default
```

### Prompt with Examples

**File: prompts/extract_entities.txt**
```
Extract named entities from the text.

Examples:
Input: "Apple Inc. announced new products in Cupertino."
Output: {{"company": "Apple Inc.", "location": "Cupertino"}}

Input: "Microsoft hired John Smith as CEO."
Output: {{"company": "Microsoft", "person": "John Smith", "role": "CEO"}}

Now extract from:
{text}
```

## Prompt File Organization

### Flat Structure (Simple)
```
prompts/
├── analyze.txt
├── validate.txt
└── summarize.txt
```

### Grouped Structure (Complex)
```
prompts/
├── analysis/
│   ├── quick_analysis.txt
│   └── deep_analysis.txt
├── validation/
│   ├── schema_check.txt
│   └── business_rules.txt
└── reporting/
    ├── summary.txt
    └── detailed.txt
```

**Loading from subdirectories:**
```python
def load_prompt(name: str, category: Optional[str] = None) -> str:
    """Load prompt, optionally from category subdirectory"""
    project_root = Path(__file__).parent.parent
    prompts_dir = project_root / "prompts"

    if category:
        prompt_path = prompts_dir / category / f"{name}.txt"
    else:
        prompt_path = prompts_dir / f"{name}.txt"

    return prompt_path.read_text()

# Usage
prompt = load_prompt("quick_analysis", category="analysis")
```

## Common Mistakes

### Mistake 1: Partial Isolation
**Problem:** Some prompts in files, others in code

**Fix:** All prompts in files, no exceptions

### Mistake 2: Code in Prompt Files
**Problem:** Python logic in .txt files

**Fix:** Prompts are pure text/templates, logic stays in Python

### Mistake 3: Absolute Paths
**Problem:** `load("/Users/justin/prompts/...")`

**Fix:** Relative to project root

### Mistake 4: No Version Control
**Problem:** Prompts not committed to git

**Fix:** functional/prompts/ is version controlled

## Workflow

### Development Cycle

1. **Write initial prompt** in functional/prompts/
2. **Run process** with prompt
3. **Check results** in outputs/
4. **Refine prompt** (edit .txt file only)
5. **Run again** (no code changes needed)
6. **Repeat** until satisfied
7. **Commit** prompt to git

### Team Workflow

- **Developer:** Writes code to load/use prompts
- **Prompt Engineer:** Refines prompts in .txt files
- **Both:** Can work independently, clean git history

## Quick Reference

| Task | Pattern |
|------|---------|
| Create prompt | Add .txt file to functional/prompts/ |
| Load prompt | `load_prompt("name")` |
| Format with data | `template.format(**data)` |
| Refine prompt | Edit .txt file, run again |
| Version prompts | name_v1.txt, name_v2.txt |
| Organize prompts | Subdirectories by category |

## Related Skills

- **directory-structure**: Where prompts/ directory lives
- **sequential-processing**: Outputs separate from prompts
- **path-management**: How to load from functional/prompts/

## Real-World Impact

**Before:**
- 30 min to refine prompt (edit Python, restart, test)
- Prompt changes mixed with code in git
- Hard to A/B test
- Prompt engineers need to touch code

**After:**
- 30 sec to refine prompt (edit .txt, run)
- Clean git history for prompts
- Easy A/B testing
- Prompt engineers work independently

## Version History

- 1.0.0: Extracted from agent-project-setup skill for clarity
