# fastapi-auth-service

Servicio de autenticación que armé para tener listo un módulo de JWT auth reutilizable cada vez que arranco un proyecto en FastAPI: login, refresh tokens, guards por rol, rate limiting y headers de seguridad ya resueltos, para no reescribir esto de cero en cada backend nuevo. Es la base que uso mientras profundizo en Python después de años trabajando principalmente en JS/TS.

## Setup

```bash
cp .env.example .env
docker compose up
```

- API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- Health check: http://localhost:8000/health

## Auth endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/v1/auth/register` | Public | Register new user |
| POST | `/api/v1/auth/login` | Public | Login, returns JWT tokens |
| POST | `/api/v1/auth/refresh` | Public | Refresh access token |
| GET | `/api/v1/auth/me` | Bearer | Get current user |

## Features

- **Uniform response contract** — All responses wrapped in `{statusCode, data, meta}`
- **JWT auth** — Access + refresh tokens, role-based guards, `@public` decorator
- **Rate limiting** — Configurable via env vars (slowapi)
- **Security headers** — Equivalent to Helmet (CSP, HSTS, X-Frame, etc.)
- **CORS** — Configurable origins via env var
- **Correlation ID** — `X-Request-ID` header per request, propagated to logs
- **Structured logging** — JSON logs with request ID
- **Env validation** — Fail-fast on missing required vars
- **Health check** — With DB connectivity verification
- **Granular validation errors** — `details: [{field, message}]`
- **Domain exceptions** — Typed hierarchy with error codes
- **Seed script** — `python seed.py` for dev data

## Development

```bash
# Lint
docker compose exec api ruff check .

# Format
docker compose exec api ruff format .

# Type check
docker compose exec api mypy app/

# Tests
docker compose exec api pytest

# Migrations
docker compose exec api alembic upgrade head

# Seed
docker compose exec api python seed.py
```

## Stack

- **FastAPI** + **Uvicorn** — ASGI server
- **SQLAlchemy 2.x** (async) — ORM
- **PostgreSQL 16** — Database
- **Pydantic v2** — Schemas + Settings
- **Alembic** — Migrations
- **PyJWT** + **passlib/bcrypt** — Auth
- **slowapi** — Rate limiting
- **Ruff** — Linter + Formatter
- **mypy** — Type checking
- **pytest** — Testing
- **Docker** — Multi-stage build
