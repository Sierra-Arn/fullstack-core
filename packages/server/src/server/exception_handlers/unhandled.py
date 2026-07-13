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

# packages/server/src/server/exception_handlers/unhandled.py
import logging
from starlette import status
from starlette.requests import Request
from starlette.responses import HTMLResponse
from fasthtml.common import to_xml
from postgres_lib import Role
from ..shared import get_session_user
from ..shared.ui import create_error_page, create_alert, Alert

logger = logging.getLogger(__name__)


async def unhandled_exception_handler(
    request: Request,
    exc: Exception,
) -> HTMLResponse:
    """
    Catch-all handler for uncaught exceptions falling through specific
    error routes.

    For HTMX requests, returns a partial alert with HTTP 200 status to
    allow HTMX to perform the swap and display the error to the user.
    For regular requests, returns a styled error page with the application
    layout and HTTP 500 status.

    Records the complete traceback at error level with request context
    for post-mortem diagnostics. Returns a generic error message to
    prevent leaking internal implementation details or raw stack traces
    to the client.

    The user role is resolved from the request cookie so the navbar
    renders the correct links for the current user even on error pages.
    If the session is absent, invalid, or Redis is unavailable, the error
    page falls back to the unauthenticated role silently.

    Parameters
    ----------
    request : Request
        Incoming request object. Provides method and URL context for
        structured log records.
    exc : Exception
        Uncaught exception that triggered the handler.

    Returns
    -------
    HTMLResponse
        For HTMX requests, an alert partial with HTTP 200 status.
        For regular requests, a styled error page with HTTP 500 status.
    """
    logger.error(
        "Unhandled exception",
        exc_info=exc,
        extra={
            "method": request.method,
            "url": str(request.url),
        },
    )

    is_htmx = request.headers.get("HX-Request") == "true"

    if is_htmx:
        # Return alert partial with 200 status for HTMX requests
        # HTMX requires 2xx status codes to perform swaps
        return HTMLResponse(
            status_code=status.HTTP_200_OK,
            # to_xml serializes FT objects to an HTML string;
            # the name reflects that HTML is a subset of XML
            # syntax, not any relation to XML as a data protocol
            content=to_xml(
                create_alert(
                    "Something went wrong on our end. Please try again later.",
                    Alert.ERROR,
                )
            ),
        )

    # Return full error page with 500 status for regular requests
    try:
        session_user = await get_session_user(request)
        role = session_user.role
    except Exception:
        role = Role.UNAUTHENTICATED

    return HTMLResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=to_xml(
            create_error_page(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                title="Internal Server Error",
                detail="Something went wrong on our end. Please try again later.",
                role=role,
            )
        ),
    )