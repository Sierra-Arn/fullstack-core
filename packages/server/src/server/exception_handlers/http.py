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

# packages/server/src/server/exception_handlers/http.py
import logging
from http import HTTPStatus
from starlette import status
from starlette.requests import Request
from starlette.exceptions import HTTPException
from starlette.responses import HTMLResponse
from fasthtml.common import to_xml
from postgres_lib import Role
from ..shared import get_session_user
from ..shared.ui import create_error_page, create_alert, Alert

logger = logging.getLogger(__name__)


async def http_exception_handler(
    request: Request,
    exc: HTTPException,
) -> HTMLResponse:
    """
    Handle HTTPException and return appropriate response.

    For HTMX requests, returns a partial alert with HTTP 200 status to
    allow HTMX to perform the swap and display the error to the user.
    For regular requests, returns a styled error page with the application
    layout and the original HTTP status code.

    Client errors in the 4xx range are logged at warning level to
    distinguish invalid requests from application faults. Server errors
    in the 5xx range are logged at error level to signal internal
    failures requiring investigation.

    Parameters
    ----------
    request : Request
        Incoming request object. Provides method and URL context for
        structured log records.
    exc : HTTPException
        Raised exception containing the HTTP status code and detail
        message.

    Returns
    -------
    HTMLResponse
        For HTMX requests, an alert partial with HTTP 200 status.
        For regular requests, a styled error page with the original
        HTTP status code.
    """
    phrase = HTTPStatus(exc.status_code).phrase

    log_extra = {
        "method": request.method,
        "url": str(request.url),
        "status_code": exc.status_code,
        "detail": exc.detail,
    }

    if exc.status_code >= 500:
        logger.error("HTTP error", extra=log_extra)
    else:
        logger.warning("HTTP error", extra=log_extra)

    is_htmx = request.headers.get("HX-Request") == "true"

    if is_htmx:
        # Return alert partial with 200 status for HTMX requests
        # HTMX requires 2xx status codes to perform swaps
        detail = exc.detail or phrase
        return HTMLResponse(
            status_code=status.HTTP_200_OK,
            # to_xml serializes FT objects to an HTML string;
            # the name reflects that HTML is a subset of XML
            # syntax, not any relation to XML as a data protocol
            content=to_xml(
                create_alert(detail, Alert.ERROR)
            ),
        )

    # Return full error page with original status for regular requests
    try:
        session_user = await get_session_user(request)
        role = session_user.role
    except Exception:
        role = Role.UNAUTHENTICATED

    return HTMLResponse(
        status_code=exc.status_code,
        content=to_xml(
            create_error_page(
                status_code=exc.status_code,
                title=phrase,
                detail=exc.detail,
                role=role,
            )
        ),
    )