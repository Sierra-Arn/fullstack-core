# Full-Stack Core

*An educational project demonstrating how to build a server-side rendered web application with Python, covering authentication, authorization, rate limiting, access logging, global error handling, partial page updates, and client-side interactivity.*

## Project Structure

```
fullstack-core/
├── packages/               # Monorepo root containing all independently deployable
│   │                       # Python modules and shared libraries. Each package
│   │                       # strictly follows the standard `src/` layout (e.g.
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
│   ├── worker-inference/   # Dedicated GPU worker running text generation
│   │                       # inference via the Qwen model and Hugging Face
│   │                       # Transformers.
│   │
│   ├── worker-maintenance/ # Maintenance process package: general-purpose
│   │                       # CPU worker and Celery beat scheduler entry
│   │                       # point, running scheduled tasks (currently:
│   │                       # resetting per-user inference run quotas).
│   │
│   └── scripts/            # Standalone automation scripts for environment
│                           # bootstrapping, infrastructure initialization, and
│                           # auxiliary utility tasks.
│
├── migrations/             # Alembic migration environment and database schema
│                           # change scripts.
│
├── docker-compose.yml      # Docker Compose stack for running infrastructure
│                           # services (PostgreSQL, Redis) locally.
│
├── .env.example            # Environment variable template. Copied to .env during
│                           # bootstrapping with auto-generated credentials for
│                           # credential fields.
│
├── pixi.toml               # Pixi configuration defining feature-based
│                           # dependency groups for server, workers, and
│                           # ML inference.
│
├── pixi.lock               # Fully resolved and reproducible dependency
│                           # lockfile.
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

## Quick Start

### I. Prerequisites

- [Pixi](https://pixi.sh/latest/) package manager.
- [Docker and Docker Compose](https://docs.docker.com/engine/install/).
- GNU/Linux-based system on `x86_64` architecture.
- NVIDIA GPU with a driver that supports CUDA `>= 12.8`.

> **Note: on these prerequisites**  
> These are not strict requirements but describe the environment used for development. The package can be set up in alternative environments with different package managers, operating systems, or GPU configurations if needed.

> **Note: on CUDA versions**  
> The `>= 12.8` figure is a *driver* requirement, enforced through pixi's `system-requirements`. It was chosen because 12.8 was the default CUDA build shipped by PyTorch at the time development started (a plain `pip install torch` pulled the 12.8 build back then).

### II. Setup

1. **Clone the repository**

    ```bash
    git clone git@github.com:Sierra-Arn/fullstack-core.git
    cd fullstack-core
    ```

2. **Install dependencies**

    ```bash
    pixi run setup
    ```

3. **Activate environment**

    ```bash
    pixi shell
    ```

### III. Launch

Once the environment is activated, the service can be launched with a single command:

```bash
just quick-start
```

The launch script will automatically execute all necessary setup steps, start the server, and open the landing page in your default web browser once the application is ready.

> **Want to see what happens under the hood?**  
> The launch script is fully documented with step-by-step comments explaining each action. You can find it here:
> - [Quick start script](./packages/scripts/src/scripts/quick_start.py)

### IV. Cleanup

When you are done, stop the server, workers, and scheduler by terminating their terminal processes, then bring down the infrastructure containers:

```bash
just docker-down
```

## License

This project is licensed under the [Apache License, Version 2.0](LICENSE).