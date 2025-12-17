# Database Setup Guide

## Choosing a Database
When selecting a database for your project, consider these factors:

1. **Data Structure**: Is your data relational or document-based?
   - Relational data → PostgreSQL, MySQL
   - Document data → MongoDB, CouchDB
   - Key-value → Redis, DynamoDB

2. **Scale Requirements**: How much data will you handle?
   - Small (<1GB) → SQLite is fine
   - Medium (1-100GB) → PostgreSQL recommended
   - Large (>100GB) → Consider sharding or managed solutions

3. **Query Patterns**: What types of queries will you run?
   - Complex joins → Relational databases
   - Simple lookups → Key-value stores
   - Full-text search → Elasticsearch or PostgreSQL with extensions

## Database Configuration

For PostgreSQL setup:
```bash
# Install PostgreSQL
brew install postgresql

# Start the service
brew services start postgresql

# Create database
createdb myproject

# Connect
psql myproject
```

For SQLite setup:
```python
import sqlite3

conn = sqlite3.connect('myproject.db')
cursor = conn.cursor()

# Create tables
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT UNIQUE
    )
''')
conn.commit()
```

## Schema Design Best Practices
- Always use primary keys
- Index frequently queried columns
- Use foreign keys for relationships
- Normalize to 3NF unless performance requires denormalization
- Use appropriate data types (don't store numbers as strings)
