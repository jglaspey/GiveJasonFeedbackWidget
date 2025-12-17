---
name: flat-guide
description: When you need help with database setup, API integration, or testing approaches for projects
---

# Project Development Guide

This guide covers database setup, API integration, and testing approaches.

## Database Setup

### Choosing a Database
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

### Database Configuration

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

### Schema Design Best Practices
- Always use primary keys
- Index frequently queried columns
- Use foreign keys for relationships
- Normalize to 3NF unless performance requires denormalization
- Use appropriate data types (don't store numbers as strings)

## API Integration

### RESTful API Design
When building or integrating with REST APIs:

1. **HTTP Methods**
   - GET: Retrieve resources
   - POST: Create new resources
   - PUT: Update entire resources
   - PATCH: Partial updates
   - DELETE: Remove resources

2. **Status Codes**
   - 200: Success
   - 201: Created
   - 400: Bad request
   - 401: Unauthorized
   - 404: Not found
   - 500: Server error

3. **URL Structure**
   ```
   GET    /api/users          # List users
   POST   /api/users          # Create user
   GET    /api/users/:id      # Get specific user
   PUT    /api/users/:id      # Update user
   DELETE /api/users/:id      # Delete user
   ```

### Authentication
Common authentication methods:

1. **API Keys**
   ```python
   headers = {
       'Authorization': 'Bearer YOUR_API_KEY'
   }
   response = requests.get(url, headers=headers)
   ```

2. **OAuth 2.0**
   - Authorization Code flow for web apps
   - Client Credentials for server-to-server
   - PKCE for mobile/SPA applications

3. **JWT Tokens**
   ```python
   import jwt

   token = jwt.encode(
       {'user_id': 123, 'exp': datetime.utcnow() + timedelta(hours=1)},
       SECRET_KEY,
       algorithm='HS256'
   )
   ```

### Error Handling
Always handle API errors gracefully:
```python
try:
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
except requests.exceptions.HTTPError as e:
    logger.error(f"HTTP error: {e}")
except requests.exceptions.ConnectionError:
    logger.error("Connection failed")
except requests.exceptions.Timeout:
    logger.error("Request timed out")
```

### Rate Limiting
Respect API rate limits:
```python
import time

def make_request_with_retry(url, max_retries=3):
    for attempt in range(max_retries):
        response = requests.get(url)
        if response.status_code == 429:
            retry_after = int(response.headers.get('Retry-After', 60))
            time.sleep(retry_after)
            continue
        return response
    raise Exception("Max retries exceeded")
```

## Testing Approaches

### Unit Testing
Test individual functions in isolation:

```python
import pytest

def add(a, b):
    return a + b

def test_add_positive_numbers():
    assert add(2, 3) == 5

def test_add_negative_numbers():
    assert add(-1, -1) == -2

def test_add_mixed():
    assert add(-1, 1) == 0
```

### Integration Testing
Test how components work together:

```python
import pytest
from myapp import create_app, db

@pytest.fixture
def client():
    app = create_app('testing')
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client

def test_create_user(client):
    response = client.post('/api/users', json={
        'name': 'Test User',
        'email': 'test@example.com'
    })
    assert response.status_code == 201
    assert response.json['name'] == 'Test User'
```

### End-to-End Testing
Test complete user workflows:

```python
from selenium import webdriver
from selenium.webdriver.common.by import By

def test_user_login_flow():
    driver = webdriver.Chrome()
    driver.get('http://localhost:3000/login')

    driver.find_element(By.ID, 'email').send_keys('user@example.com')
    driver.find_element(By.ID, 'password').send_keys('password123')
    driver.find_element(By.ID, 'submit').click()

    assert 'Dashboard' in driver.title
    driver.quit()
```

### Test Coverage
Aim for meaningful coverage:
- 80%+ line coverage is a good target
- Focus on critical paths
- Don't write tests just to increase coverage
- Use coverage reports to find untested code:
  ```bash
  pytest --cov=myapp --cov-report=html
  ```

### Mocking
Use mocks for external dependencies:
```python
from unittest.mock import patch, MagicMock

@patch('myapp.external_api.fetch_data')
def test_process_data(mock_fetch):
    mock_fetch.return_value = {'status': 'success', 'data': [1, 2, 3]}

    result = process_data()

    assert result == [1, 2, 3]
    mock_fetch.assert_called_once()
```

### Test Organization
Structure your tests logically:
```
tests/
├── unit/
│   ├── test_models.py
│   └── test_utils.py
├── integration/
│   ├── test_api.py
│   └── test_database.py
├── e2e/
│   └── test_workflows.py
└── conftest.py
```
