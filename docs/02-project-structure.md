# II. Project Structure

> *This document describes the logical organization of the project codebase as a Python monorepo. Each package follows the standard `src/` layout for clean imports, independent packaging, and reproducible builds via Pixi.*

## Repository Layout

```
fullstack-core/
├── packages/               # Monorepo root containing all independently deployable
│   │                       # Python modules and shared libraries. Each package
│   │                       # follows the standard `src/` layout (e.g.
│   │                       # `packages/server/src/server/`) for clean imports and
│   │                       # packaging.
│   │
│   ├── server/             # FastHTML app: HTTP routing, server-rendered
│   │                       # pages, HTMX partial updates, database
│   │                       # interactions, and task delegation to the
│   │                       # workers.
│   │
│   ├── shared/             # Cross-process shared infrastructure. Contains base
│   │                       # configurations and unified client abstractions for
│   │                       # external services.
│   │
│   ├── services/           # Cross-process business logic built on top of shared
│   │                       # infrastructure. Contains self-contained service
│   │                       # modules that implement domain-specific behaviour.
│   │
│   ├── worker-inference/   # Dedicated GPU worker for model inference tasks
│   │                       # (Transformers + PyTorch CUDA build).
│   │
│   ├── worker-maintenance/ # Maintenance process package: general-purpose
│   │                       # CPU worker and Celery beat scheduler entry
│   │                       # point, running periodic maintenance tasks.
│   │
│   └── scripts/            # Standalone automation scripts for environment
│                           # bootstrapping, infrastructure initialization, and
│                           # auxiliary utility tasks.
│
├── migrations/             # Alembic migration environment and database schema
│                           # change scripts.
│
├── postgres/               # PostgreSQL initialization scripts generated from
│                           # environment variables at bootstrap time.
│
├── redis/                  # Redis ACL initialization scripts generated from
│                           # environment variables at bootstrap time.
│
├── docker-compose.yml      # Docker Compose stack for running infrastructure
│                           # services (PostgreSQL, Redis) locally.
│
├── .env.example            # Environment variable template. Copied to .env during
│                           # bootstrapping with auto-generated credentials for
│                           # credential fields.
│
├── pixi.toml               # Pixi configuration defining feature-based dependency
│                           # groups for server, workers, and shared libraries.
│
├── pixi.lock               # Fully resolved and reproducible dependency lockfile.
│
├── package.json            # Bun manifest declaring frontend asset dependencies.
│
├── bun.lock                # Fully resolved and reproducible JavaScript dependency
│                           # lockfile.
│
└── justfile                # Task runner: bootstrap commands, database
                            # migration targets, runtime process launchers,
                            # and Docker Compose shortcuts. Automatically
                            # manages the pixi environment per recipe.
```

Every file contains comprehensive inline comments to explain the code. 

> **Note:**  
Since the primary focus here is on demonstrating backend server patterns rather than database configuration, `docker-compose.yml` uses a minimal setup for both databases — for more detailed PostgreSQL and Redis configurations, see [postgresql-core](https://github.com/Sierra-Arn/postgresql-core) and [redis-core](https://github.com/Sierra-Arn/redis-core).

## Package Overview

### 1. `packages/server/`
The FastHTML application serving as the HTTP boundary of the system. Handles server-rendered page composition, HTMX partial responses, session-based authentication, role-based authorization, rate limiting, access logging, and global error handling.

```
server/
├── assets/             # Frontend source inputs consumed by the asset build recipes.
│   │
│   ├── index.js        # JavaScript entry point bundled into static/js/index.js.
│   └── styles.css      # Tailwind input compiled into static/css/styles.css.
│
├── static/             # Built assets mounted and served to the browser.
│   │
│   ├── css/styles.css  # Compiled Tailwind + DaisyUI stylesheet.
│   ├── js/index.js     # Bundled HTMX and Alpine.js runtime.
│   └── icons/outline/  # Heroicons SVGs copied from node_modules at build time.
│
├── pyproject.toml      # Packaging and dependency manifest for the server package.
└── src/server/         # Python application package.
    │
    ├── app.py                  # FastHTML application factory, middleware registration,
    │                           # static file mounting, and exception handler wiring.
    ├── config.py               # Environment-based settings and centralized RoutePath constants.
    ├── logger.py               # Structured JSON logging configuration.
    ├── main.py                 # Uvicorn entry point for the ASGI server.      
    │
    ├── exception_handlers/
    │   ├── http.py             # Handles HTTPException raised by route handlers,
    │   │                       # translating status codes into HTML error pages
    │   │                       # or HTMX-compatible alert partials.
    │   └── unhandled.py        # Catches all unhandled exceptions, logs the full
    │                           # traceback, and returns a generic 500 response.
    ├── middleware/
    │   ├── access_log.py       # Logs every request with method, URL, status, and response time.
    │   └── rate_limit.py       # IP-based sliding window rate limiting via Redis.
    │
    ├── shared/
    │   ├── auth.py             # Session helpers and role-based route decorators.
    │   ├── parsing.py          # Form and query parsing into dataclass request shapes.
    │   ├── schemas.py          # Shared dataclass field mixins and pagination helpers.
    │   ├── utils.py            # HTML response helpers and shared UI utilities.
    │   │
    │   └── ui/                 # Reusable server-rendered UI components.
    │       │
    │       ├── alert.py                # Inline alert rendering helpers for HTMX forms.
    │       ├── confirmation_modal.py   # Reusable confirmation modal component.
    │       ├── empty_state.py          # Empty-state component for list pages.
    │       ├── error_page.py           # Full-page error rendering.
    │       ├── footer.py               # Application footer.
    │       ├── forms.py                # Shared form control helpers.
    │       ├── layout.py               # Page layout wrapper and title assembly.
    │       ├── navbar.py               # Navigation bar for authenticated and public pages.
    │       ├── pagination.py           # Pagination UI primitives.
    │       └── spinner.py              # Loading spinner component.
    │
    └── modules/                # Route handlers grouped by domain resource.
        │
        ├── landing/            # GET /.
        │
        ├── health/             # Liveness and readiness health check endpoints.
        │   │
        │   ├── shallow/        # GET /health/shallow (process only).
        │   └── deep/           # GET /health/deep (PostgreSQL and Redis connectivity).
        │
        ├── login/              # GET/POST /login.
        ├── register/           # GET/POST /register.
        ├── logout/             # POST /logout.
        │
        ├── collaborate/        # GET/POST /collaborate.
        │
        ├── inference/          # Model inference interface for authenticated users.
        │   │
        │   ├── page/           # GET/POST /inference.
        │   └── status/         # GET /inference/status/{task_id}.
        │
        ├── inference_history/  # GET /inference/history.
        │
        ├── leads/              # Collaboration request management (MODERATOR+).
        │   │
        │   ├── list/           # GET /leads.
        │   └── status/         # POST /leads/{id}/status.
        │
        └── users/              # User account management (ADMIN).
            │
            ├── list/           # GET /users.
            ├── role/           # POST /users/{id}/role.
            └── delete/         # POST /users/{id}/delete.
```

Route handlers are organized by domain resource under `modules/`, with each module encapsulating the pages, partials, routes, and request shapes for a single user-facing area. This makes the application surface navigable by feature and workflow rather than by technical artifact type.

The `exception_handlers/` directory translates internal exceptions into uniform HTML error responses suitable for both full-page renders and HTMX swaps. The `middleware/` directory implements cross-cutting concerns applied to every request before it reaches a route handler. The `shared/` directory contains server-specific utilities reused across multiple modules, including form and query parsing, dataclass request shapes, authentication helpers, and shared UI components under `shared/ui/`.

### 2. `packages/shared/`

Centralizes all infrastructure client code and shared utilities consumed across the system. Implements the concrete clients for PostgreSQL and Redis, the shared Celery application, and base configuration primitives.

```
shared/
├── pyproject.toml
└── src/
    ├── base_lib/                   # Foundational utilities shared across all packages.
    │   ├── base_config.py          # Base Pydantic settings class with environment
    │   │                           # variable loading.
    │   └── logger.py               # Structured JSON logging setup shared across all processes.
    │
    ├── celery_lib/                 # Shared Celery application instance and configuration.
    │   ├── config.py               # Broker, result backend, and beat schedule settings.
    │   └── instance.py             # Celery app instance, queues, and task routing.
    │
    ├── postgres_lib/               # Relational database layer.
    │   ├── config.py               # PostgreSQL connection settings.
    │   ├── session.py              # SQLAlchemy async session factory.
    │   ├── models/                 # ORM models for domain entities.
    │   │   │
    │   │   ├── base.py                 # Declarative base and shared mixins (id, created_at).
    │   │   ├── types.py                # Custom SQLAlchemy column types and domain enums.
    │   │   ├── user.py                 # User model.
    │   │   ├── lead.py                 # Collaboration request (lead) model.
    │   │   └── inference_history.py    # Inference run history model.
    │   │
    │   └── repositories/           # Stateless data access layer following the Repository pattern.
    │       │
    │       ├── base.py                 # Generic BaseRepository with common CRUD classmethods.
    │       ├── user.py                 # User-specific queries and persistence operations.
    │       ├── lead.py                 # Lead-specific queries and persistence operations.
    │       └── inference_history.py    # Inference history queries and persistence operations.
    │
    └── redis_lib/                  # In-memory store client.
        │
        ├── config.py               # Redis connection settings with per-database URL properties.
        └── client.py               # Async Redis client instances keyed by logical database.
```

### 3. `packages/services/`

Centralizes cross-process business logic built on top of shared infrastructure. Each library implements a self-contained domain concern and is consumed by the server.

```
services/
├── pyproject.toml
└── src/
    ├── password_lib/               # Password hashing and verification.
    │   ├── config.py               # Bcrypt cost factor and algorithm settings.
    │   └── service.py              # Hash and verify operations via bcrypt.
    │
    ├── rate_limit_lib/             # IP and account based sliding window rate limiting.
    │   ├── config.py               # Maximum requests and window duration settings.
    │   └── service.py              # Sliding window counter operations against Redis.
    │
    └── session_lib/                # Server-side session management.
        ├── config.py               # Session cookie name, TTL, and Redis key settings.
        ├── types.py                # SessionPayload schema for serialized session data.
        └── service.py              # Session creation, lookup, and revocation in Redis.
```

### 4. `packages/worker-inference/`

The GPU-bound worker process that executes **text generation** tasks — the system's isolated inference context. It consumes tasks from the message broker, runs the Qwen model through Hugging Face Transformers on the GPU, and persists the resulting inference history to PostgreSQL.

```
worker-inference/
├── pyproject.toml
└── src/worker_inference/
    ├── config.py                      # Worker-specific configuration (model path,
    │                                  # device, pool settings).
    ├── main.py                        # Celery worker entry point with eager GPU
    │                                  # model and tokenizer initialization.
    ├── _state.py                      # Process-local model and tokenizer
    │                                  # references (loaded once at startup).
    └── tasks/
        └── generate.py                # Text generation task: runs inference,
                                       # persists history, and increments the
                                       # user run counter.
```

This worker is isolated from maintenance tasks to prevent VRAM from being occupied by non-ML operations. The `_state.py` module ensures that the heavy model weights are loaded exactly once when the worker process starts, not on every task invocation.

### 5. `packages/worker-maintenance/`

The CPU-bound process package that executes **scheduled maintenance** tasks — the system's isolated maintenance context, free of any ML or GPU dependencies. It can run either as a Celery worker consuming from the maintenance queue or as a beat scheduler dispatching periodic tasks into that queue.

```
worker-maintenance/
├── pyproject.toml
└── src/worker_maintenance/
    ├── config.py                # Worker and beat scheduler configuration
    │                            # (paths, pool settings).
    ├── main.py                  # Entry point for worker or beat scheduler mode.
    └── tasks/
        └── reset.py             # Daily bulk reset of per-user inference run
                                 # counters in PostgreSQL.
```

The maintenance worker uses a `solo` pool, which is appropriate for lightweight database operations that require no parallelism within a single process. Its complete isolation from the inference worker keeps GPU memory dedicated to model execution, never pinned by a process that performs no ML work. The beat scheduler runs as a separate process and dispatches the daily quota reset into the maintenance queue according to the schedule configured in `celery_lib`.

### 6. `packages/scripts/`

Standalone automation scripts for environment bootstrapping and developer utilities. Not part of the runtime application but essential for development workflow.

```
scripts/
├── pyproject.toml
└── src/scripts/
    ├── quick_start.py                  # Automated startup script. Bootstraps infrastructure,
    │                                   # builds frontend assets, applies migrations, launches the
    │                                   # server and workers, and opens the landing page.
    └── utils/
        ├── init_env.py                 # Generates .env file from .env.example with secure
        │                               # credentials.
        ├── generate_postgres_sql.py    # Generates PostgreSQL user creation SQL from env vars.
        └── generate_redis_acl.py       # Generates Redis ACL rules from env vars.
```

The `quick_start.py` script orchestrates infrastructure provisioning, frontend asset builds, database migration, and process launch in the correct dependency order, eliminating manual setup steps. The `utils/` scripts generate environment and infrastructure initialization artifacts from environment variables, enforcing the principle of least privilege for database users and Redis ACLs.

## Infrastructure Directories

### 7. `migrations/`

Alembic migration environment managing the evolution of the database schema. Contains the configuration file (`alembic.ini`), migration script template, and all versioned migration files including the initial schema and seed data.

```
migrations/
├── versions/
│   ├── b5dabad9f8b0_auto_migration.py          # Initial schema: users, leads,
│   │                                           # inference_history.
│   ├── 0667fb39660d_seed_admin_user.py         # Seeds the initial administrator account
│   │                                           # from environment variables.
│   └── fc8041e25d16_seed_test_data.py          # Seeds local development test data for users,
│                                               # leads, and inference history.
├── alembic.ini                                 # Alembic configuration file.
├── env.py                                      # Migration execution environment.
└── script.py.mako                              # Migration script template.
```

### 8. `postgres/` and `redis/`

Infrastructure initialization artifacts generated by the scripts in `packages/scripts/utils/` from environment variables at bootstrap time.

`postgres/` contains the SQL script that creates the application database user with restricted privileges — SELECT, INSERT, UPDATE, and DELETE on tables only, preventing the application user from dropping tables, schemas, or the database itself.

`redis/` contains the ACL configuration that defines two Redis users: an admin user with unrestricted access for operational tasks, and an application user restricted to only the commands the service actually issues, with the default user disabled entirely.