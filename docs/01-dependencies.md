# I. Dependencies Overview

> *This document describes the dependencies required by Full-Stack Core: what each one is and the role it plays in the project.*

## System Dependencies

| Dependency | Repository | What it is | Role in the project |
|---|---|---|---|
| Pixi | [prefix-dev/pixi](https://github.com/prefix-dev/pixi) | Package and environment manager | 1. Resolves and installs mixed Conda and PyPI dependencies for the server, workers, and shared libraries. <br>2. Produces a deterministic lockfile (`pixi.lock`) for fully reproducible environments. |
| Docker | [moby/moby](https://github.com/moby/moby) | Containerization platform | Container runtime that isolates and runs PostgreSQL and Redis locally. |
| Docker Compose | [docker/compose](https://github.com/docker/compose) | Multi-container orchestration tool | Declares containers, their networking, and startup order in a single `docker-compose.yml` file. |
| NVIDIA GPU | — | GPU hardware | Hardware accelerator used by the inference worker for model execution. |
| CUDA driver | — | Host GPU driver | Low-level host driver (`libcuda`) required for GPU-accelerated computation. |

## Docker Images

| Dependency | Repository | What it is | Role in the project |
|---|---|---|---|
| PostgreSQL | [docker.io/library/postgres](https://hub.docker.com/_/postgres) | Official Docker image for PostgreSQL | Runs the relational database engine in a container, storing all persistent application data (users, leads, inference history). |
| Redis | [docker.io/library/redis](https://hub.docker.com/_/redis) | Official Docker image for Redis | Runs the in-memory data store in a container, serving as the Celery broker and result backend, and storing sessions and sliding window rate limit counters. |

## Pixi Dependencies

### Default Dependencies

| Dependency | Repository | What it is | Role in the project |
|---|---|---|---|
| CPython | [python/cpython](https://github.com/python/cpython) | Python virtual machine | Executes all Python source code across every package in the monorepo. |
| python-dotenv | [theskumar/python-dotenv](https://github.com/theskumar/python-dotenv) | Environment variable loader | Loads variables from `.env` files into `os.environ` for local execution and tooling. |
| just | [casey/just](https://github.com/casey/just) | Command runner | Provides short, readable recipes for bootstrapping, migrations, asset builds, and process launchers. |
| Bun | [oven-sh/bun](https://github.com/oven-sh/bun) | JavaScript runtime and package manager | 1. Resolves and installs JavaScript dependencies for the frontend asset toolchain.<br>2. Produces a deterministic lockfile (`bun.lock`) for reproducible JavaScript environments. |

### Shared Dependencies

| Dependency | Repository | What it is | Role in the project |
|---|---|---|---|
| Pydantic Settings | [pydantic/pydantic-settings](https://github.com/pydantic/pydantic-settings) | Settings management library | Loads and validates environment variables for all configuration classes across `shared`, `services`, `server`, and workers. |
| SQLAlchemy | [sqlalchemy/sqlalchemy](https://github.com/sqlalchemy/sqlalchemy) | ORM and database toolkit | Maps Python classes to PostgreSQL tables and manages sessions for all database interactions. |
| Alembic | [sqlalchemy/alembic](https://github.com/sqlalchemy/alembic) | Database migration tool | Manages versioned schema changes via sequential migration scripts in `migrations/`. |
| psycopg | [psycopg/psycopg](https://github.com/psycopg/psycopg) | Sync + async PostgreSQL driver | Handles all database connections via SQLAlchemy's `postgresql+psycopg` dialect. |
| redis-py | [redis/redis-py](https://github.com/redis/redis-py) | Official Redis client | Connects application code and Celery to Redis as a data store, broker, and result backend. |
| Celery | [celery/celery](https://github.com/celery/celery) | Distributed task queue | Dispatches work to worker processes that run concurrently with the web server and schedules periodic maintenance jobs. |

### Services Dependencies

| Dependency | Repository | What it is | Role in the project |
|---|---|---|---|
| bcrypt | [pyca/bcrypt](https://github.com/pyca/bcrypt) | Password hashing library | Hashes passwords at registration and verifies them at login using the bcrypt algorithm. |

### Server Dependencies

| Dependency | Repository | What it is | Role in the project |
|---|---|---|---|
| FastHTML | [AnswerDotAI/fasthtml](https://github.com/AnswerDotAI/fasthtml) | Server-side HTML framework | Defines typed HTML components, routing integration, and server-rendered pages with HTMX partial updates. |
| Uvicorn | [encode/uvicorn](https://github.com/encode/uvicorn) | ASGI server | Serves the application over HTTP. |
| python-json-logger | [nhairs/python-json-logger](https://github.com/nhairs/python-json-logger) | JSON log formatter | Formats log records as structured JSON for consistent machine-readable output across processes. |

### Worker-Inference Dependencies

| Dependency | Repository | What it is | Role in the project |
|---|---|---|---|
| CUDA Toolkit | [nvidia.com](https://developer.nvidia.com/cuda-toolkit) | CUDA runtime and math libraries | User-space runtime and optimized GPU libraries used by PyTorch for tensor computations on the GPU. |
| pytorch-gpu | [pytorch/pytorch](https://github.com/pytorch/pytorch) | Deep learning framework, CUDA built | Executes model inference on the GPU inside the dedicated inference worker. |
| Transformers | [huggingface/transformers](https://github.com/huggingface/transformers) | Model and inference library | Loads the Qwen model, tokenizer, and generation pipeline used by the inference worker. |
| Accelerate | [huggingface/accelerate](https://github.com/huggingface/accelerate) | Model runtime helper | Provides runtime helpers for efficient inference configuration and device placement. |

## Model Weights

| Model | Repository | Used by |
|---|---|---|
| Qwen3.5-2B | [Qwen/Qwen3.5-2B](https://huggingface.co/Qwen/Qwen3.5-2B) | The `generate` task in the inference worker for user prompt completion. |

## Bun Dependencies

| Dependency | Repository | What it is | Role in the project |
|---|---|---|---|
| Tailwind CSS | [tailwindlabs/tailwindcss](https://github.com/tailwindlabs/tailwindcss) | Utility-first CSS framework | Defines the utility class system and generation rules used by the server-rendered UI. |
| DaisyUI | [saadeghi/daisyui](https://github.com/saadeghi/daisyui) | Tailwind component library | Adds a component design system on top of Tailwind (e.g., buttons, cards, alerts), exposed as additional utility classes. |
| @tailwindcss/cli | [tailwindlabs/tailwindcss](https://github.com/tailwindlabs/tailwindcss) | Tailwind CLI | Runs the CSS build: scans templates for class usage and compiles Tailwind + DaisyUI into the final CSS bundle that the server serves to the browser. |
| Heroicons | [tailwindlabs/heroicons](https://github.com/tailwindlabs/heroicons) | SVG icon set | Provides the source icon set that is copied into the project and referenced by UI components. |
| HTMX | [bigskysoftware/htmx](https://github.com/bigskysoftware/htmx) | HTML-over-the-wire library | Enables partial page updates and form submissions by swapping server-rendered HTML fragments into the existing DOM. |
| Alpine.js | [alpinejs/alpine](https://github.com/alpinejs/alpine) | Lightweight client-side reactivity | Implements small interactive behaviors (e.g., confirmation modal state) without a full single-page application framework. |