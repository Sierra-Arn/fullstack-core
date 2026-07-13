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

# packages/server/src/server/middleware/access_log.py
import logging
import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger(__name__)


class AccessLogMiddleware(BaseHTTPMiddleware):
    """
    Middleware that logs every incoming HTTP request and its outcome.

    Captures the request method, URL, client IP, HTTP status code, and
    response time for every request that passes through the application.
    All records are emitted at INFO level with a type field set to access,
    allowing them to be filtered separately from internal application logs
    in structured JSON output.

    Notes
    -----
    Response time is measured from the moment dispatch is entered to the
    moment the response object is returned by the next handler. It does not
    include the time spent streaming the response body to the client.
    """

    async def dispatch(self, request: Request, call_next: callable) -> Response:
        """
        Delegate to the next handler and log the outcome.

        Parameters
        ----------
        request : Request
            Incoming HTTP request.
        call_next : callable
            Next handler in the middleware chain.

        Returns
        -------
        Response
            Response returned by the next handler, passed through unchanged.
        """
        start = time.perf_counter()
        response: Response = await call_next(request)
        response_time_ms = round((time.perf_counter() - start) * 1000, 2)

        logger.info(
            "Request handled",
            extra={
                "type": "access",
                "ip": request.client.host,
                "method": request.method,
                "url": str(request.url),
                "status_code": response.status_code,
                "response_time_ms": response_time_ms,
            },
        )

        return response