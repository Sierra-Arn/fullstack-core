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

# packages/server/src/server/modules/health/utils.py
import logging
from sqlalchemy import text
from postgres_lib import async_engine
from redis_lib import session_redis_client, rate_limit_redis_client
from celery_lib import celery_app
from .types import ServiceStatus

logger = logging.getLogger(__name__)


async def check_postgres() -> ServiceStatus:
    """
    Verify PostgreSQL availability by executing a lightweight query.

    Opens an asynchronous connection and runs a constant selection
    to confirm the database engine is responsive and accepting
    transactions.

    Returns
    -------
    ServiceStatus
        ServiceStatus.OK if the query executes successfully.
        ServiceStatus.UNAVAILABLE if the connection fails, times
        out, or encounters a database error.
    """
    try:
        async with async_engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return ServiceStatus.OK
    except Exception as e:
        logger.error("PostgreSQL healthcheck failed", exc_info=e)
        return ServiceStatus.UNAVAILABLE


async def check_session_redis() -> ServiceStatus:
    """
    Verify availability of the session Redis database by issuing
    a ping command.

    Returns
    -------
    ServiceStatus
        ServiceStatus.OK if the ping returns a successful response.
        ServiceStatus.UNAVAILABLE if the connection is refused, times
        out, or encounters an authentication error.
    """
    try:
        await session_redis_client.ping()
        return ServiceStatus.OK
    except Exception as e:
        logger.error("Session Redis healthcheck failed", exc_info=e)
        return ServiceStatus.UNAVAILABLE


async def check_rate_limit_redis() -> ServiceStatus:
    """
    Verify availability of the rate limiting Redis database by issuing
    a ping command.

    Returns
    -------
    ServiceStatus
        ServiceStatus.OK if the ping returns a successful response.
        ServiceStatus.UNAVAILABLE if the connection is refused, times
        out, or encounters an authentication error.
    """
    try:
        await rate_limit_redis_client.ping()
        return ServiceStatus.OK
    except Exception as e:
        logger.error("Rate limit Redis healthcheck failed", exc_info=e)
        return ServiceStatus.UNAVAILABLE


def check_celery() -> ServiceStatus:
    """
    Verify Celery worker availability by broadcasting a ping request.

    Uses the Celery control interface to query active workers and
    waits for a response within a two second timeout to confirm at
    least one worker is online and consuming tasks from the broker.

    Returns
    -------
    ServiceStatus
        ServiceStatus.OK if one or more workers acknowledge the ping;
        ServiceStatus.UNAVAILABLE if no workers respond or the control
        request fails.
    """
    try:
        response = celery_app.control.inspect(timeout=2).ping()
        if not response:
            return ServiceStatus.UNAVAILABLE
        return ServiceStatus.OK
    except Exception as e:
        logger.error("Celery healthcheck failed", exc_info=e)
        return ServiceStatus.UNAVAILABLE