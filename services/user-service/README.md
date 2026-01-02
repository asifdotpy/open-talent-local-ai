# User Service (Scaffold)

## Overview

- FastAPI service with async SQLAlchemy
- Self-hosted Supabase core (Postgres + PostgREST) via docker-compose
- Alembic migrations scaffolded
- JWT verification placeholder (to integrate with Security Service)

## Quick Start

```bash
cd services/user-service
cp .env.example .env
# Start Postgres + PostgREST
docker compose -f docker-compose.supabase.yml up -d

# Run migrations
alembic upgrade head

# Start API
python -m uvicorn app.main:app --reload --port 8001
```

## Key Files

- docker-compose.supabase.yml — Postgres + PostgREST (Supabase core)
- app/config.py — settings (DATABASE_URL, logging)
- app/database.py — async engine/session + init_db
- app/models.py — SQLAlchemy models (User)
- app/schemas.py — Pydantic schemas
- app/routers.py — API routes (root, health, list/create users)
- app/utils.py — auth placeholder (validate Authorization header)
- alembic.ini — migration config
- migrations/ — Alembic environment + versions folder

## Next Steps (Day 1-2)

1) Flesh out models: profiles, preferences, activity, sessions
2) Expand routers: full CRUD, profile, preferences, search/filter, activity
3) Integrate Security Service JWT verification (signature + claims)
4) Add RLS policies mapped from JWT (role, tenant_id)
5) Add tests (unit + integration with Postgres container)

## Notes

- PostgREST included for optional direct table access; FastAPI remains source of business logic.
- Keep everything offline/local; no cloud dependencies.
