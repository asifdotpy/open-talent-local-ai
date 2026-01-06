# Service Audit Results: user-service

**Location**: `services/user-service`
**Type**: FastAPI

## Recent Changes

```
commit b43abe82811bb9e7871b3a2f44764ad4a65a4fb5
Author: Asif - TalentAI <asif@talentai.com>
Date:   Mon Jan 5 18:20:29 2026 +0600

    feat: Enhance type safety in create_access_token and resolve pre-commit issues

    Refactored create_access_token function for type safety.
    Resolved bandit, black, isort, and ruff pre-commit hook failures.
    Temporarily disabled mypy and markdownlint hooks to unblock commit.
    Follow-up tasks are needed to properly configure mypy and markdownlint.
```

## Endpoints

| Method | Path | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Service root |
| `GET` | `/health` | Health check |
| `GET` | `/api/v1/users` | List users |
| `GET` | `/api/v1/users/count` | Count users |
| `GET` | `/api/v1/users/{user_id}` | Get user by ID |
| `POST` | `/api/v1/users` | Create user |
| `PATCH` | `/api/v1/users/{user_id}` | Update user |
| `PUT` | `/api/v1/users/{user_id}` | Update user |
| `DELETE` | `/api/v1/users/{user_id}` | Delete user |
| `GET` | `/api/v1/users/{user_id}/profile` | Get user profile |
| `POST` | `/api/v1/users/{user_id}/profile` | Create user profile |
| `PATCH` | `/api/v1/users/{user_id}/profile` | Update user profile |
| `PUT` | `/api/v1/users/{user_id}/profile` | Update user profile |
| `GET` | `/api/v1/users/me/profile` | Get current user's profile |
| `PATCH` | `/api/v1/users/me/profile` | Update current user's profile |
| `GET` | `/api/v1/users/{user_id}/preferences` | Get user preferences |
| `POST` | `/api/v1/users/{user_id}/preferences` | Create user preferences |
| `PATCH` | `/api/v1/users/{user_id}/preferences` | Update user preferences |
| `PUT` | `/api/v1/users/{user_id}/preferences` | Update user preferences |
| `GET` | `/api/v1/users/me/preferences` | Get current user's preferences |
| `PATCH` | `/api/v1/users/me/preferences` | Update current user's preferences |
| `PUT` | `/api/v1/users/me/preferences` | Update current user's preferences |
| `GET` | `/api/v1/users/{user_id}/activity` | Get user activity |
| `POST` | `/api/v1/users/{user_id}/activity` | Log user activity |
| `GET` | `/api/v1/users/{user_id}/sessions` | Get user sessions |
| `DELETE` | `/api/v1/users/{user_id}/sessions/{session_id}`| Revoke user session |
| `POST` | `/api/v1/users/bulk/import` | Bulk import users |
| `GET` | `/api/v1/users/bulk/export` | Bulk export users |

## Mock Data / Simulation Findings

1.  **Database Integration**: The service is fully integrated with a PostgreSQL database using SQLAlchemy for data persistence. All CRUD operations interact with the database.
2.  **No Mock Data**: No in-memory data structures, hardcoded responses, or mock data patterns were found within the main application logic in `app/routers.py`.
3.  **Test Data**: Mock data and `example.com` domains are used appropriately within the test suite (`tests/`) to isolate tests and are not present in the production code.
