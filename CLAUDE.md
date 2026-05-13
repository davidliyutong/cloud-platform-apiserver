# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Run the server
```shell
python -m src serve
python -m src init   # initialize configuration
```

### Tests
```shell
pytest                        # run all tests
pytest src/tests/test_foo.py  # run a single test file
pytest -k "test_name"         # run tests matching a name
```

Tests live in `src/tests/`. `pyproject.toml` sets `pythonpath = ["."]` so no export needed.

### Docker
```shell
make build.docker.native    # build image tagged with git version
make push.docker.buildx     # build and push multi-platform (amd64, arm64)
make test.docker             # run latest image locally
make task.generate_client   # generate Python client from live OpenAPI spec
```

## Architecture

This is a Sanic-based async REST API server that manages containerized WebIDE pods (code-server/noVNC) on Kubernetes, with MongoDB for persistence.

### Layer structure

```
src/
  __main__.py               # CLI entry point (Click: init | serve)
  apiserver/
    server/server.py        # App wiring: blueprints, JWT, DB/K8s init, background tasks
    controller/             # HTTP handlers (one file per role×resource)
    service/                # Business logic
      service.py            # RootService factory — aggregates all services
    repo/                   # MongoDB access (Motor async driver)
  components/
    config.py               # APIServerConfig (Vyper-based, env vars CLPL_*)
    datamodels.py           # Pydantic v2 models: UserModel, PodModel, TemplateModel, QuotaModel
    authn.py / authz.py     # JWT + OIDC auth, RBAC
    tasks.py                # Background tasks: crash recovery, pod scanning
    events.py               # Event definitions dispatched through handler.py
```

### Key services (`src/apiserver/service/`)

| Service | Responsibility |
|---|---|
| `UserService` | User CRUD, quota management |
| `PodService` | Pod lifecycle: create/delete/update, quota enforcement |
| `TemplateService` | Template management (admin-controlled, shared across users) |
| `AuthService` | JWT issuance/validation, OIDC flow |
| `K8SOperatorService` | Kubernetes API interactions (pod creation, deletion, status) |
| `HeartbeatService` | Pod keep-alive / timeout enforcement |

### API routes

- `POST /v1/auth/basic/`, `POST /v1/auth/token/login` — authentication
- `/v1/admin/users|pods|templates/` — admin-only CRUD
- `/v1/users|pods|templates/` — user self-service
- `GET /docs/openapi.json` — live OpenAPI spec

### Authentication

Two modes configured via `CLPL_*` env vars:
1. **JWT** (default) — `sanic-jwt` with bcrypt passwords
2. **OIDC** — Authentik integration; `jsonpath-ng` maps OIDC claims to local user fields

### Database

MongoDB via Motor (async). Collections: `clpl_users`, `clpl_pods`, `clpl_templates`, `clpl_global`. Connection singleton in `src/apiserver/repo/db.py`. Configuration via `CLPL_DB_*` env vars (default: `mongodb://clpl:clpl@127.0.0.1:27017`).

### Configuration

All config is via environment variables prefixed `CLPL_` (Vyper reads them). Key groups:
- `CLPL_API_*` — host, port, workers
- `CLPL_DB_*` — MongoDB connection
- `CLPL_K8S_*` — Kubernetes API endpoint and credentials
- `CLPL_OIDC_*` — OIDC provider settings
- `CLPL_BOOTSTRAP_*` — initial admin credentials and JWT secret

### Background tasks (started at server launch)

- **Crash recovery** — reconciles pod state after restart
- **Pod scanner** — periodic sweep for timed-out or orphaned pods
- **Admin bootstrap** — creates default admin user if none exists
