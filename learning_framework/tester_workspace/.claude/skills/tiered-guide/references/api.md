# API Integration Guide

## RESTful API Design
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

## Authentication
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

## Error Handling
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

## Rate Limiting
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
