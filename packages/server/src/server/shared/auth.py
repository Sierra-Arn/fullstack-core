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

# packages/server/src/server/shared/auth.py
from functools import wraps
from starlette import status
from starlette.requests import Request
from starlette.responses import Response
from starlette.exceptions import HTTPException
from postgres_lib import Role
from session_lib import SessionService, SessionPayload, session_config
from .utils import html_response


async def get_session_user(request: Request) -> SessionPayload:
    """
    Extract and validate the session cookie, returning the decoded
    session payload or a default unauthenticated state.

    If the session cookie is missing, returns a default payload
    representing an unauthenticated visitor. If the cookie is present
    but the corresponding session cannot be found in Redis, raises
    an authentication error.

    Parameters
    ----------
    request : Request
        The incoming HTTP request object containing the session cookie.

    Returns
    -------
    SessionPayload
        Parsed session data containing the authenticated user identifier
        and their access role. If no session cookie is present, returns
        a payload with a null user identifier and the unauthenticated role.

    Raises
    ------
    HTTPException
        401 Unauthorized if the session cookie is present but the
        corresponding session is invalid or has expired.

    Notes
    -----
    This function implements a hybrid validation strategy. The absence
    of a session cookie is treated as a normal state for unauthenticated
    visitors, allowing public routes to seamlessly access the current
    user state without handling exceptions. However, if a session cookie
    is present but invalid, this indicates a potential issue such as an
    expired session, a revoked session, or a tampered cookie, and is
    treated as an authentication failure.
    """
    session_id = request.cookies.get(session_config.cookie_name)

    if not session_id:
        return SessionPayload(user_id=None, role=Role.UNAUTHENTICATED)

    payload = await SessionService.get(session_id)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session is invalid or has expired.",
        )

    return payload


async def require_role(request: Request, role: Role) -> SessionPayload:
    """
    Validate the session and ensure the current user holds at least
    the required role.

    Intended to be called directly at the beginning of a protected
    route handler to enforce hierarchical role-based access control.
    Fetches the session payload, verifies the user is authenticated
    and has sufficient privileges, and returns the payload for
    further use.

    Parameters
    ----------
    request : Request
        The incoming HTTP request object containing the session cookie.
    role : Role
        The minimum access role required to access the route. Users
        with higher privilege levels will also be granted access due
        to the hierarchical nature of the role system.

    Returns
    -------
    SessionPayload
        Parsed session data containing the authenticated user identifier
        and their access role.

    Raises
    ------
    HTTPException
        401 Unauthorized if the user is not authenticated.
        403 Forbidden if the current user privilege level is lower
        than the required role level.

    Notes
    -----
    The role hierarchy is defined by the numeric level associated with
    each role. A user with a higher level automatically satisfies the
    requirements of roles with lower levels. For example, an administrator
    can access routes restricted to moderators or regular users.
    """
    user = await get_session_user(request)

    if user.role == Role.UNAUTHENTICATED:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
        )

    if user.role.level < role.level:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied.",
        )

    return user


def role_for_display(handler):
    """
    Decorator for route handlers that need the user role for display purposes.

    Extracts the current user role from the session and injects it into
    the wrapped handler. The role is used purely for conditional rendering
    of UI elements such as navigation links, call-to-action buttons, or
    user-specific content. The page remains accessible to all visitors
    regardless of authentication state.

    The decorator supports handlers that return either FT elements or
    Response objects. If the handler returns a Response (e.g., for redirects),
    it is passed through unchanged. If the handler returns an FT element,
    it is automatically wrapped in an HTML response.

    This decorator contrasts with authorization decorators like
    role_for_authorization that enforce access control and reject requests
    from users without sufficient privileges. Here, the role drives
    presentation logic rather than permission checks.

    Parameters
    ----------
    handler : callable
        Asynchronous function accepting (request, role) parameters and
        returning either a FastHTML element or a Response object.

    Returns
    -------
    callable
        Wrapped route handler that accepts only the request parameter,
        automatically extracts the role, and returns an HTML response
        or passes through Response objects unchanged.
    """
    @wraps(handler)
    async def wrapper(request: Request, *args, **kwargs) -> Response:
        session_user = await get_session_user(request)
        kwargs['role'] = session_user.role
        result = await handler(request, *args, **kwargs)
        if isinstance(result, Response):
            return result
        return html_response(result)
    return wrapper


def role_for_authorization(required_role: Role):
    """
    Decorator factory for route handlers that require authorization.

    Creates a decorator that enforces role-based access control before
    executing the wrapped handler. The decorator validates that the user
    is authenticated and holds at least the required role, injecting the
    authenticated user payload into the handler for further use.

    The decorator supports handlers that return either FT elements or
    Response objects. If the handler returns a Response (e.g., for redirects),
    it is passed through unchanged. If the handler returns an FT element,
    it is automatically wrapped in an HTML response.

    This decorator contrasts with display decorators like role_for_display
    that extract the role for conditional UI rendering without enforcing
    access restrictions. Here, the role is used for permission checks and
    unauthorized requests are rejected with appropriate HTTP status codes.

    Parameters
    ----------
    required_role : Role
        The minimum access role required to access the route. Users with
        higher privilege levels will also be granted access due to the
        hierarchical nature of the role system.

    Returns
    -------
    callable
        Decorator that wraps a route handler, enforcing authorization
        before execution.
    """
    def decorator(handler):
        @wraps(handler)
        async def wrapper(request: Request, *args, **kwargs) -> Response:
            user = await require_role(request, required_role)
            kwargs['user'] = user
            result = await handler(request, *args, **kwargs)
            if isinstance(result, Response):
                return result
            return html_response(result)
        return wrapper
    return decorator