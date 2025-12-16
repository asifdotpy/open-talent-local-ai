# User Service API Endpoints

**Service:** User Service  
**Port:** 8001  
**Base URL:** `http://localhost:8001`

## Health & Status

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Root endpoint - service status |
| GET | `/health` | Health check endpoint |

## User CRUD Operations

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/users` | List users with pagination and filters |
| GET | `/api/v1/users/count` | Count users with optional filters |
| GET | `/api/v1/users/{user_id}` | Get specific user by ID |
| POST | `/api/v1/users` | Create new user |
| PATCH | `/api/v1/users/{user_id}` | Update existing user |
| DELETE | `/api/v1/users/{user_id}` | Delete user (soft delete) |

### Query Parameters for List Users

- `skip` (int, default: 0): Pagination offset
- `limit` (int, default: 100, max: 1000): Results per page
- `email` (string): Filter by email (partial match)
- `role` (enum): Filter by role (admin/recruiter/candidate)
- `status` (enum): Filter by status (active/inactive/suspended)
- `search` (string): Search by name, email, or location
- `tenant_id` (string): Filter by tenant

## User Profile Operations

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/users/{user_id}/profile` | Get user profile |
| POST | `/api/v1/users/{user_id}/profile` | Create user profile |
| PATCH | `/api/v1/users/{user_id}/profile` | Update user profile |

## User Preferences Operations

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/users/{user_id}/preferences` | Get user preferences |
| POST | `/api/v1/users/{user_id}/preferences` | Create user preferences |
| PATCH | `/api/v1/users/{user_id}/preferences` | Update user preferences |

## User Activity Tracking

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/users/{user_id}/activity` | Get user activity log |
| POST | `/api/v1/users/{user_id}/activity` | Log user activity |

### Query Parameters for Activity

- `skip` (int, default: 0): Pagination offset
- `limit` (int, default: 100, max: 1000): Results per page
- `action` (string): Filter by action type

## User Session Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/users/{user_id}/sessions` | Get user sessions |
| DELETE | `/api/v1/users/{user_id}/sessions/{session_id}` | Revoke user session |

### Query Parameters for Sessions

- `active_only` (bool, default: false): Show only active sessions

## Bulk Operations

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/users/bulk/import` | Bulk import users from CSV |
| GET | `/api/v1/users/bulk/export` | Bulk export users to CSV |

### CSV Import Format

```csv
email,first_name,last_name,role,status,phone,location,tenant_id
john@example.com,John,Doe,candidate,active,555-1234,New York,tenant1
jane@example.com,Jane,Smith,recruiter,active,555-5678,Boston,tenant1
```

### CSV Export Query Parameters

- `role` (enum): Filter by role
- `status` (enum): Filter by status
- `tenant_id` (string): Filter by tenant

## Authentication

All endpoints (except `/` and `/health`) require Bearer token authentication:

```
Authorization: Bearer <token>
```

## Example API Calls

### Create User

```bash
curl -X POST http://localhost:8001/api/v1/users \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "candidate",
    "status": "active"
  }'
```

### List Users with Filters

```bash
curl "http://localhost:8001/api/v1/users?role=candidate&status=active&limit=50" \
  -H "Authorization: Bearer <token>"
```

### Search Users

```bash
curl "http://localhost:8001/api/v1/users?search=john&limit=20" \
  -H "Authorization: Bearer <token>"
```

### Get User Profile

```bash
curl http://localhost:8001/api/v1/users/{user_id}/profile \
  -H "Authorization: Bearer <token>"
```

### Update User Preferences

```bash
curl -X PATCH http://localhost:8001/api/v1/users/{user_id}/preferences \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "notification_email": true,
    "theme": "dark",
    "language": "en"
  }'
```

### Log User Activity

```bash
curl -X POST "http://localhost:8001/api/v1/users/{user_id}/activity?action=login&resource=web_app" \
  -H "Authorization: Bearer <token>"
```

### Export Users to CSV

```bash
curl "http://localhost:8001/api/v1/users/bulk/export?status=active" \
  -H "Authorization: Bearer <token>" \
  -o users_export.csv
```

### Import Users from CSV

```bash
curl -X POST http://localhost:8001/api/v1/users/bulk/import \
  -H "Authorization: Bearer <token>" \
  -F "file=@users.csv"
```

## Swagger Documentation

Interactive API documentation available at:
- Swagger UI: http://localhost:8001/docs
- ReDoc: http://localhost:8001/redoc
- OpenAPI JSON: http://localhost:8001/openapi.json

## Response Formats

### Success Response (User)

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "role": "candidate",
  "status": "active",
  "phone": null,
  "bio": null,
  "location": "New York",
  "avatar_url": null,
  "tenant_id": "tenant1",
  "created_at": "2025-12-14T10:00:00Z",
  "updated_at": "2025-12-14T10:00:00Z"
}
```

### Error Response

```json
{
  "detail": "User not found"
}
```

## Status Codes

- `200 OK`: Successful GET/PATCH request
- `201 Created`: Successful POST request
- `204 No Content`: Successful DELETE request
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Missing or invalid authentication
- `404 Not Found`: Resource not found
- `409 Conflict`: Resource already exists (duplicate email)
- `422 Unprocessable Entity`: Validation error

## Features Summary

✅ **Full CRUD operations** for users  
✅ **Advanced filtering** (role, status, email, search)  
✅ **Pagination** support (skip/limit)  
✅ **User profiles** management  
✅ **User preferences** management  
✅ **Activity tracking** with filtering  
✅ **Session management** with revocation  
✅ **Bulk import** from CSV  
✅ **Bulk export** to CSV with filters  
✅ **Count endpoint** for analytics  
✅ **Soft delete** (status-based)  
✅ **Multi-tenant** support (tenant_id filtering)

## Database Models

- **User**: Core user entity with auth/profile data
- **UserProfile**: Extended profile (bio, company, job title, avatar)
- **UserPreferences**: Notification and UI settings
- **UserActivity**: Audit log of user actions
- **UserSession**: Active/revoked session tracking
