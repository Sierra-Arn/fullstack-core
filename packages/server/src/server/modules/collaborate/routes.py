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

# packages/server/src/server/modules/collaborate/routes.py
from fasthtml.common import FT
from starlette.requests import Request
from starlette.responses import Response
from postgres_lib import get_async_db_session, LeadRepository, Role
from .pages import create_collaborate_page
from .partials import create_collaborate_form_partial
from .schemas import CollaborateForm
from ...shared import html_response, role_for_display, parse_form


@role_for_display
async def collaborate_get(request: Request, role: Role) -> FT:
    """
    Render the public collaboration request page.

    The decorator automatically extracts the current user role from the
    session and injects it into this handler. The role is used purely
    for display purposes to conditionally render UI elements such as
    navigation links. The page remains accessible to all visitors
    regardless of authentication state, as collaboration requests are
    intended for both unauthenticated prospects and registered users.

    Parameters
    ----------
    request : Request
        The incoming HTTP request object.
    role : Role
        Current user access role, automatically extracted from the
        session by the role_for_display decorator.

    Returns
    -------
    FT
        FastHTML element representing the complete collaboration page.
    """
    return create_collaborate_page(role=role)


@parse_form(CollaborateForm)
async def collaborate_post(request: Request, form: CollaborateForm) -> Response:
    """
    Handle the collaboration form submission.

    Normalizes and validates the collaboration input. On success, persists
    the new lead to the database and returns the form partial with a success
    confirmation; on failure, returns the form partial with an inline error
    alert so the visitor can correct their input without a page reload.

    Parameters
    ----------
    request : Request
        The incoming HTTP request containing the form data.
    form : CollaborateForm
        Parsed form data injected by the parse_form decorator. Fields are
        normalized on construction and expose derived checks as properties.

    Returns
    -------
    Response
        HTML response containing the updated form partial with a success
        message after the lead is persisted, or with an error alert when
        the input is invalid.
    """
    if not form.has_name:
        return html_response(create_collaborate_form_partial(error="Name is required."))

    if not form.has_email:
        return html_response(create_collaborate_form_partial(error="Email is required."))

    if not form.email_is_valid:
        return html_response(
            create_collaborate_form_partial(error="Please enter a valid email address.")
        )

    if not form.has_message:
        return html_response(
            create_collaborate_form_partial(error="Message is required.")
        )

    lead_data = {
        "name": form.name,
        "email": form.email,
        "company": form.optional_company,
        "message": form.message,
    }

    async with get_async_db_session() as session:
        await LeadRepository.create(
            session,
            obj_data=lead_data,
        )
        await session.commit()

    return html_response(
        create_collaborate_form_partial(success=True)
    )