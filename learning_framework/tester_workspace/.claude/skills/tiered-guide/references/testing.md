# Testing Approaches Guide

## Unit Testing
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

## Integration Testing
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

## End-to-End Testing
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

## Test Coverage
Aim for meaningful coverage:
- 80%+ line coverage is a good target
- Focus on critical paths
- Don't write tests just to increase coverage
- Use coverage reports to find untested code:
  ```bash
  pytest --cov=myapp --cov-report=html
  ```

## Mocking
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

## Test Organization
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
