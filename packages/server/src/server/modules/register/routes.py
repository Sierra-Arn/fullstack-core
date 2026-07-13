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

# packages/server/src/server/modules/register/routes.py
from starlette import status
from starlette.requests import Request
from starlette.responses import Response
from postgres_lib import get_async_db_session, UserRepository, Role
from session_lib import SessionService, SessionPayload, session_config
from password_lib import PasswordService
from .pages import create_register_page
from .partials import create_register_form_partial
from .schemas import RegisterForm
from ...shared import html_response, role_for_display, parse_form
from ...config import RoutePath


@role_for_display
async def register_get(request: Request, role: Role) -> Response:
    """
    Render the public registration page.

    Extracts the current user role from the session to determine
    whether the registration page should be displayed. If the user is
    already authenticated, they are immediately redirected to the
    inference page, as the registration form has no purpose for signed-in
    users. Otherwise, the registration page is rendered with the
    appropriate navigation state.

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
        On success, an HTML response containing the rendered registration page.
        If the user is already authenticated, an HTTP 200 response with
        an HX-Redirect header pointing to the inference page.
    """
    if role.level >= Role.USER.level:
        return Response(
            status_code=status.HTTP_200_OK,
            headers={"HX-Redirect": RoutePath.INFERENCE},
        )

    return create_register_page(role=role)


@parse_form(RegisterForm)
async def register_post(request: Request, form: RegisterForm) -> Response:
    """
    Handle the registration form submission.

    Normalizes and validates the registration input, checks that the email
    is not already taken, hashes the password, creates the user record,
    establishes a session, and redirects to the inference page. Returns the
    registration form partial with an error alert on any failure without
    raising an HTTP exception, so the user stays on the form and sees inline
    feedback via HTMX.

    Parameters
    ----------
    request : Request
        The incoming HTTP request containing the form data.
    form : RegisterForm
        Parsed form data injected by the parse_form decorator. Fields are
        normalized on construction and expose derived checks as properties.

    Returns
    -------
    Response
        Redirect response to the inference page on success, or the registration
        form partial with an error alert on failure.
    """
    if not form.has_email:
        return html_response(create_register_form_partial(error="Email is required."))

    if not form.email_is_valid:
        return html_response(
            create_register_form_partial(error="Please enter a valid email address.")
        )

    if not form.has_password:
        return html_response(create_register_form_partial(error="Password is required."))

    if not form.passwords_match:
        return html_response(
            create_register_form_partial(error="Passwords do not match.")
        )

    async with get_async_db_session() as session:
        existing = await UserRepository.get_by_email(session, email=form.email)
        if existing is not None:
            return html_response(
                create_register_form_partial(
                    error=f"An account with email '{form.email}' already exists.",
                ),
            )

        hashed = PasswordService.hash(form.password)
        user = await UserRepository.create(
            session,
            obj_data={
                "email": form.email,
                "hashed_password": hashed,
            },
        )
        await session.commit()

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