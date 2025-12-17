---
name: separated-processor
description: When you need to convert CSV data to JSON, validate tabular file formats, or normalize date and currency fields in spreadsheet exports
---

# CSV Data Processor

This skill processes CSV files for data pipeline integration.

## What This Skill Does

1. Reads CSV files from the specified path
2. Validates schema matches expected columns
3. Transforms dates to ISO 8601 format
4. Normalizes currency values to USD
5. Outputs as clean JSON

## Expected Columns

- `date` - Any date format, will be converted
- `amount` - Currency value with optional symbol
- `description` - Text field
- `category` - Category code

## Output Format

```json
{
  "records": [
    {
      "date": "2024-01-15",
      "amount_usd": 150.00,
      "description": "Sample",
      "category": "A1"
    }
  ],
  "metadata": {
    "total_records": 1,
    "processing_date": "2024-01-15T10:30:00Z"
  }
}
```
