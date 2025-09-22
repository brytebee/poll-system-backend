# API Usage Examples

## Authentication

### Register User

<!-- TODO: Update links in prod -->

```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpass123",
    "password_confirm": "testpass123",
    "first_name": "Test",
    "last_name": "User"
  }'
```

### Login User

```bash
curl -X POST http://localhost:8000/api/auth/login/ \
 -H "Content-Type: application/json" \
 -d '{
"username": "testuser",
"password": "testpass123"
}'
```

## Polls

### Create Poll

```bash
curl -X POST http://localhost:8000/api/polls/ \
 -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
 -H "Content-Type: application/json" \
 -d '{
"title": "Best Programming Language?",
"description": "Vote for your favorite programming language",
"options": [
  {"text": "Python", "order_index": 1},
  {"text": "JavaScript", "order_index": 2},
  {"text": "Java", "order_index": 3}
]
}'
```

### Vote on Poll

```bash
curl -X POST http://localhost:8000/api/polls/{POLL_ID}/vote/ \
 -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
 -H "Content-Type: application/json" \
 -d '{
"option_id": "OPTION_UUID"
}'
```

### Get Poll Results

```bash
curl -X GET http://localhost:8000/api/polls/{POLL_ID}/results/
```
