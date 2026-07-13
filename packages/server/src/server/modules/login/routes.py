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

# packages/server/src/server/modules/login/routes.py
from starlette import status
from starlette.requests import Request
from starlette.responses import Response
from postgres_lib import get_async_db_session, UserRepository, Role
from session_lib import SessionService, SessionPayload, session_config
from password_lib import PasswordService
from .pages import create_login_page
from .partials import create_login_form_partial
from .schemas import LoginForm
from ...shared import html_response, role_for_display, parse_form
from ...config import RoutePath


@role_for_display
async def login_get(request: Request, role: Role) -> Response:
    """
    Render the public login page.

    Extracts the current user role from the session to determine
    whether the login page should be displayed. If the user is
    already authenticated, they are immediately redirected to the
    inference page, as the login form has no purpose for signed-in
    users. Otherwise, the login page is rendered with the appropriate
    navigation state.

    Parameters
    ----------
    request : Request
        The incoming HTTP request object containing the session cookie.
    role : Role
        Current user access role, automatically extracted from the
        session by the role_for_display decorator.

    Returns
    -------
    Response
        On success, an HTML response containing the rendered login page.
        If the user is already authenticated, an HTTP 200 response with
        an HX-Redirect header pointing to the inference page.
    """
    if role.level >= Role.USER.level:
        return Response(
            status_code=status.HTTP_200_OK,
            headers={"HX-Redirect": RoutePath.INFERENCE},
        )

    return create_login_page(role=role)


@parse_form(LoginForm)
async def login_post(request: Request, form: LoginForm) -> Response:
    """
    Authenticate the user and create a new session.

    Normalizes the submitted credentials, verifies them against the
    database, and creates a server-side session stored in Redis. On
    success, sets the session cookie and instructs the client to redirect
    to the inference page via HTMX. Any failure, whether from missing,
    malformed, or incorrect credentials, returns the login form partial with a single
    generic message so as not to reveal whether the email is well-formed
    or maps to an existing account.

    Parameters
    ----------
    request : Request
        The incoming HTTP request containing the form data.
    form : LoginForm
        Parsed form data injected by the parse_form decorator. Fields are
        normalized on construction.

    Returns
    -------
    Response
        On success, an HTTP 200 response with an HX-Redirect header
        pointing to the inference page and a session cookie attached.
        On failure, an HTML response containing the login form partial
        with an error message displayed above the form.
    """
    async with get_async_db_session() as session:
        user = await UserRepository.get_by_email(
            session,
            email=form.email,
        )

    if user is None or not PasswordService.verify(form.password, user.hashed_password):
        return html_response(
            create_login_form_partial(error="Invalid email or password.")
        )

    session_payload = SessionPayload(user_id=user.id, role=user.role)
    session_id = await SessionService.create(session_payload)

    response = Response(
        status_code=status.HTTP_200_OK,
        headers={"HX-Redirect": RoutePath.INFERENCE},
    )

    response.set_cookie(
        key=session_config.cookie_name,
        value=session_id,
        path=session_config.cookie_path,
        httponly=session_config.cookie_httponly,
        samesite=session_config.cookie_samesite,
        secure=session_config.cookie_secure,
    )

    return response