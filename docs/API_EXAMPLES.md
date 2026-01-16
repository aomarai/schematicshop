# API Examples

This document provides examples of how to use the SchematicShop API.

## Authentication

### Register a new user

```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "securepassword123",
    "password_confirm": "securepassword123",
    "first_name": "Test",
    "last_name": "User"
  }'
```

Response:
```json
{
  "id": 1,
  "username": "testuser",
  "email": "test@example.com",
  "first_name": "Test",
  "last_name": "User",
  "bio": "",
  "avatar": "",
  "storage_quota": 1073741824,
  "storage_used": 0,
  "storage_available": 1073741824,
  "storage_percentage": 0.0,
  "created_at": "2024-01-15T10:30:00Z"
}
```

### Login

```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "securepassword123"
  }'
```

Response:
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Get current user profile

```bash
curl -X GET http://localhost:8000/api/auth/me/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Schematics

### List schematics

```bash
# Public schematics (no auth required)
curl -X GET http://localhost:8000/api/schematics/

# With search
curl -X GET "http://localhost:8000/api/schematics/?search=castle"

# With filters
curl -X GET "http://localhost:8000/api/schematics/?category=medieval&scan_status=clean"
```

Response:
```json
{
  "count": 42,
  "next": "http://localhost:8000/api/schematics/?page=2",
  "previous": null,
  "results": [
    {
      "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "title": "Medieval Castle",
      "description": "A beautiful medieval castle with towers",
      "owner": {
        "id": 1,
        "username": "builder123",
        "avatar": ""
      },
      "file_size": 2048576,
      "minecraft_version": "1.20.1",
      "width": 128,
      "height": 64,
      "length": 128,
      "tags": [
        {"id": 1, "name": "medieval", "slug": "medieval"},
        {"id": 2, "name": "castle", "slug": "castle"}
      ],
      "category": "medieval",
      "is_public": true,
      "scan_status": "clean",
      "download_count": 150,
      "view_count": 523,
      "thumbnail_url": "",
      "likes_count": 42,
      "is_liked": false,
      "created_at": "2024-01-10T14:23:00Z",
      "updated_at": "2024-01-10T14:23:00Z"
    }
  ]
}
```

### Upload a schematic

```bash
curl -X POST http://localhost:8000/api/schematics/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "file=@path/to/schematic.schem" \
  -F "title=My Awesome Build" \
  -F "description=A cool building I made" \
  -F "tag_names=modern,house,creative" \
  -F "category=modern" \
  -F "is_public=true" \
  -F "minecraft_version=1.20.1"
```

Response:
```json
{
  "id": "new-uuid-here",
  "title": "My Awesome Build",
  "description": "A cool building I made",
  "owner": {...},
  "file_size": 1234567,
  "scan_status": "pending",
  ...
}
```

### Get schematic details

```bash
curl -X GET http://localhost:8000/api/schematics/{id}/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Download a schematic

```bash
curl -X POST http://localhost:8000/api/schematics/{id}/download/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

Response:
```json
{
  "download_url": "http://localhost:9000/schematics/2024/01/15/file.schem",
  "file_name": "file.schem",
  "file_size": 2048576
}
```

### Like a schematic

```bash
# Like
curl -X POST http://localhost:8000/api/schematics/{id}/like/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Unlike
curl -X DELETE http://localhost:8000/api/schematics/{id}/like/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Add a comment

```bash
curl -X POST http://localhost:8000/api/schematics/{id}/comments/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "This is an amazing build!",
    "parent": null
  }'
```

### Get trending schematics

```bash
curl -X GET http://localhost:8000/api/schematics/trending/
```

## Tags

### List all tags

```bash
curl -X GET http://localhost:8000/api/schematics/tags/
```

### Get popular tags

```bash
curl -X GET http://localhost:8000/api/schematics/tags/popular/
```

## User Stats

### Get user statistics

```bash
curl -X GET http://localhost:8000/api/auth/me/stats/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

Response:
```json
{
  "total_schematics": 15,
  "public_schematics": 12,
  "storage_used": 52428800,
  "storage_quota": 1073741824,
  "storage_available": 1021313024,
  "storage_percentage": 4.88
}
```

## Python Example

```python
import requests

# Base URL
BASE_URL = "http://localhost:8000/api"

# Login
response = requests.post(f"{BASE_URL}/auth/login/", json={
    "username": "testuser",
    "password": "securepassword123"
})
tokens = response.json()
access_token = tokens["access"]

# Headers with authentication
headers = {
    "Authorization": f"Bearer {access_token}"
}

# Upload a schematic
with open("my_build.schem", "rb") as f:
    files = {"file": f}
    data = {
        "title": "My Build",
        "description": "An awesome build",
        "tag_names": "modern,house",
        "is_public": True
    }
    response = requests.post(
        f"{BASE_URL}/schematics/",
        headers=headers,
        files=files,
        data=data
    )
    schematic = response.json()
    print(f"Uploaded: {schematic['id']}")

# List user's schematics
response = requests.get(
    f"{BASE_URL}/schematics/",
    headers=headers,
    params={"owner": "testuser"}
)
schematics = response.json()
print(f"Total: {schematics['count']}")
```

## JavaScript Example

```javascript
const BASE_URL = 'http://localhost:8000/api';

// Login
async function login(username, password) {
  const response = await fetch(`${BASE_URL}/auth/login/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password })
  });
  const { access } = await response.json();
  localStorage.setItem('access_token', access);
  return access;
}

// Upload schematic
async function uploadSchematic(file, metadata) {
  const formData = new FormData();
  formData.append('file', file);
  Object.keys(metadata).forEach(key => {
    formData.append(key, metadata[key]);
  });
  
  const token = localStorage.getItem('access_token');
  const response = await fetch(`${BASE_URL}/schematics/`, {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${token}` },
    body: formData
  });
  
  return await response.json();
}

// Usage
const token = await login('testuser', 'securepassword123');
const schematic = await uploadSchematic(fileInput.files[0], {
  title: 'My Build',
  description: 'An awesome build',
  tag_names: 'modern,house',
  is_public: true
});
console.log('Uploaded:', schematic.id);
```

## Rate Limits

The API implements rate limiting:
- Anonymous users: 100 requests/hour
- Authenticated users: 1000 requests/hour
- Upload endpoint: 10 requests/hour

When rate limited, you'll receive a `429 Too Many Requests` response.

## Pagination

All list endpoints support pagination:
- `?page=2` - Get page 2
- `?page_size=50` - Change page size (max 100)

Response includes:
```json
{
  "count": 150,
  "next": "http://localhost:8000/api/schematics/?page=3",
  "previous": "http://localhost:8000/api/schematics/?page=1",
  "results": [...]
}
```

## Error Handling

Error responses follow a consistent format:

```json
{
  "error": "Error message",
  "detail": "Detailed error information"
}
```

Common HTTP status codes:
- `200 OK` - Success
- `201 Created` - Resource created
- `400 Bad Request` - Invalid input
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Permission denied
- `404 Not Found` - Resource not found
- `429 Too Many Requests` - Rate limit exceeded
- `500 Internal Server Error` - Server error
