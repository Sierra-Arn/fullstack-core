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

# packages/server/src/server/middleware/rate_limit.py
import logging
from starlette import status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, HTMLResponse
from fasthtml.common import to_xml
from rate_limit_lib import RateLimitService
from postgres_lib import Role
from ..shared import get_session_user
from ..shared.ui import create_error_page

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware that enforces IP-based rate limiting on every incoming request.

    On each request the client IP address is extracted and checked against
    the sliding window counter stored in Redis. If the limit is exceeded the
    request is rejected immediately with a 429 Too Many Requests HTML error
    page before it reaches any route handler.

    Rate limit parameters, including maximum requests and window duration, are read
    from rate_limit_config at startup and require an application restart to
    take effect.

    Notes
    -----
    BaseHTTPMiddleware wraps every request in a try/except block internally,
    so unhandled exceptions raised inside dispatch (such as RedisError) are
    still caught by the global exception handlers registered on the application.
    """

    async def dispatch(
        self,
        request: Request,
        call_next: callable,
    ) -> Response:
        """
        Check the rate limit for the incoming request and either forward it
        or reject it with a 429 response.

        Parameters
        ----------
        request : Request
            Incoming HTTP request.
        call_next : callable
            Next handler in the middleware chain. Called only if the rate
            limit has not been exceeded.

        Returns
        -------
        Response
            Response from the next handler if the request is allowed, or a
            429 Too Many Requests HTML response if the limit is exceeded.
        """
        ip = request.client.host

        if not await RateLimitService.is_allowed(identifier=ip):
            logger.warning(
                "Rate limit exceeded",
                extra={
                    "ip": ip,
                    "method": request.method,
                    "url": str(request.url),
                },
            )

            try:
                session_user = await get_session_user(request)
                role = session_user.role
            except Exception:
                role = Role.UNAUTHENTICATED

            return HTMLResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content=to_xml(
                    create_error_page(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        title="Too Many Requests",
                        detail="You have exceeded the allowed request rate. Please try again later.",
                        role=role,
                    )
                ),
            )

        return await call_next(request)