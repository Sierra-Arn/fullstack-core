# Copyright (c) 2026 Ilya Snegov (aka Sierra Arn)

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Originally from Human Pose Estimation Service
# https://github.com/Sierra-Arn/pose-estimation-service
# Modified for Full-Stack Core

# =============================================================================
# Justfile Settings
# =============================================================================
set dotenv-load := true
set export := true

# =============================================================================
# Environment Mappings: justfile variable -> pixi environment
# =============================================================================

ENV_DEFAULT      := "pixi run -e default"
ENV_SERVER       := "pixi run -e server"
ENV_WORKER_INF   := "pixi run -e worker-inference"
ENV_WORKER_MAIN  := "pixi run -e worker-maintenance"

# =============================================================================
# Scripts
# =============================================================================

# Generate .env from template with secure random passwords
gen-env:
    {{ENV_DEFAULT}} python -m scripts.utils.init_env

# Generate Redis ACL rules for Docker init
gen-acl:
    {{ENV_DEFAULT}} python -m scripts.utils.generate_redis_acl

# Generate PostgreSQL user creation script for Docker init
gen-sql:
    {{ENV_DEFAULT}} python -m scripts.utils.generate_postgres_sql

# Compile Tailwind CSS from the source input file into the static output file.
build-css:
    {{ENV_DEFAULT}} bun run tailwindcss -i packages/server/assets/styles.css -o packages/server/static/css/styles.css

# Bundle frontend JS (htmx + alpine) from the source entry file into the static output file.
build-js:
    {{ENV_DEFAULT}} bun build packages/server/assets/index.js --outfile=packages/server/static/js/index.js

# Copy Heroicons SVG files from node_modules into the static icons directory.
build-icons:
    cp node_modules/heroicons/24/outline/*.svg packages/server/static/icons/outline/

# =============================================================================
# Infrastructure
# =============================================================================

# Generate new revision
db-revision message='New migration':
    {{ENV_SERVER}} alembic -c ./migrations/alembic.ini revision -m "{{message}}"

# Generate new revision with auto-detected changes
db-revision-auto message='Auto migration':
    {{ENV_SERVER}} alembic -c ./migrations/alembic.ini revision --autogenerate -m "{{message}}"

# Apply pending migrations to sync database schema
db-migrate:
    {{ENV_SERVER}} alembic -c ./migrations/alembic.ini upgrade head

# Revert the latest migration step
db-rollback:
    {{ENV_SERVER}} alembic -c ./migrations/alembic.ini downgrade -1

# =============================================================================
# Runtime
# =============================================================================

# Start Celery worker for ML inference
worker-inference:
    {{ENV_WORKER_INF}} python -m worker_inference.main

# Start Celery worker for maintenance tasks
worker-maintenance:
    {{ENV_WORKER_MAIN}} python -m worker_maintenance.main --mode worker

# Start Celery beat scheduler
worker-beat:
    {{ENV_WORKER_MAIN}} python -m worker_maintenance.main --mode beat

# Launch FastHTML server
server:
    {{ENV_SERVER}} python -m server.main

# =============================================================================
# Docker Local
# =============================================================================

# Start infrastructure stack to be consumed by locally running services
docker-up:
    {{ENV_DEFAULT}} docker compose -f docker-compose.yml up -d

# Stop local containers and remove anonymous volumes
docker-down:
    {{ENV_DEFAULT}} docker compose -f docker-compose.yml down --remove-orphans --volumes

# Stream combined logs from all local services
docker-logs:
    {{ENV_DEFAULT}} docker compose -f docker-compose.yml logs -f

# =============================================================================
# Quick Start
# =============================================================================

# Start full local development environment and open Swagger in browser
quick-start:
    {{ENV_DEFAULT}} python -m scripts.quick_start