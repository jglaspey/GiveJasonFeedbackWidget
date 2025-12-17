---
name: mixed-processor
description: Processes CSV files by reading them, validating schema against expected columns, transforming date formats to ISO 8601, normalizing currency to USD, and outputting clean JSON
---

# CSV Data Processor

This skill processes CSV files for data pipeline integration.

## Steps

1. Read the CSV file
2. Validate the schema matches expected columns
3. Transform dates to ISO 8601 format
4. Normalize currency values to USD
5. Output as clean JSON

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
