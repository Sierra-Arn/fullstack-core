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

# Originally from Backend Core
# https://github.com/Sierra-Arn/backend-core
# Modified for Full-Stack Core

# packages/server/src/server/modules/health/routes.py
import asyncio
from starlette import status
from starlette.requests import Request
from starlette.responses import JSONResponse
from .utils import (
    check_postgres,
    check_session_redis,
    check_rate_limit_redis,
    check_celery,
)
from .types import ServiceStatus
from ...config import server_config


async def health_shallow_get(request: Request) -> JSONResponse:
    """
    Provide a lightweight process liveness probe.

    Returns an immediate success response without inspecting external
    dependencies or internal state. Designed for fast liveness checks
    used by orchestrators and load balancers to verify that the web
    server process is running and accepting HTTP requests.

    Parameters
    ----------
    request : Request
        Incoming request object. Not used directly 
        but required by the Starlette handler signature.

    Returns
    -------
    JSONResponse
        JSON response with status "ok" and HTTP 200, indicating the
        process is alive and accepting requests.
    """
    return JSONResponse({"status": ServiceStatus.OK})


async def health_deep_get(request: Request) -> JSONResponse:
    """
    Execute concurrent health probes for all external dependencies.

    Runs PostgreSQL, session Redis, rate limit Redis, and Celery broker
    checks in parallel via asyncio.gather. If all probes succeed the
    overall status is OK; if any probe fails the overall status is
    DEGRADED so that orchestrators can route traffic away from the
    instance or trigger an alert without marking it fully unavailable.

    Parameters
    ----------
    request : Request
        Incoming request object. Not used directly but required by the
        Starlette handler signature.

    Returns
    -------
    JSONResponse
        Aggregated health status for the instance and each dependency.
        Returns 200 with status "ok" or "degraded" when probes complete,
        or 503 with status "unavailable" on timeout.

    Notes
    -----
    All probes must complete within server_config.deep_health_timeout
    seconds. On timeout every dependency is marked UNAVAILABLE and the
    overall status is set to UNAVAILABLE to signal orchestrators that
    the instance cannot serve traffic safely.
    """
    try:
        postgres, session_redis, rate_limit_redis, celery = (
            await asyncio.wait_for(
                asyncio.gather(
                    check_postgres(),
                    check_session_redis(),
                    check_rate_limit_redis(),
                    check_celery(),
                ),
                timeout=server_config.deep_health_timeout,
            )
        )
    except asyncio.TimeoutError:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": ServiceStatus.UNAVAILABLE,
                "postgres": ServiceStatus.UNAVAILABLE,
                "session_redis": ServiceStatus.UNAVAILABLE,
                "rate_limit_redis": ServiceStatus.UNAVAILABLE,
                "celery": ServiceStatus.UNAVAILABLE,
            },
        )

    overall = (
        ServiceStatus.OK
        if all(
            s == ServiceStatus.OK
            for s in (postgres, session_redis, rate_limit_redis, celery)
        )
        else ServiceStatus.DEGRADED
    )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "status": overall,
            "postgres": postgres,
            "session_redis": session_redis,
            "rate_limit_redis": rate_limit_redis,
            "celery": celery,
        },
    )