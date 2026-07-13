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

# packages/server/src/server/modules/leads/routes.py
from starlette import status
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import Response
from postgres_lib import get_async_db_session, LeadRepository, Role, LeadStatus
from session_lib import SessionPayload
from .components import create_lead_card
from .partials import create_leads_partial
from .pages import create_leads_page
from .schemas import LeadStatusForm
from ...shared import (
    role_for_authorization,
    calculate_pagination,
    parse_query,
    parse_form,
    PageQuery,
)
from ...config import server_config


@role_for_authorization(Role.MODERATOR)
@parse_query(PageQuery)
async def leads_get(
    request: Request,
    user: SessionPayload,
    params: PageQuery,
) -> Response:
    """
    Render the leads page or partial based on request type.

    For regular HTTP requests, renders the complete leads page with
    navbar and footer. For HTMX requests (pagination), returns only
    the leads partial without layout to avoid duplicating navbar and
    footer in the DOM.

    Parameters
    ----------
    request : Request
        The incoming HTTP request object containing the session cookie
        and optional page query parameter.
    user : SessionPayload
        Authenticated user payload injected by the role_for_authorization
        decorator. Contains the user identifier and access role.
    params : PageQuery
        Parsed query parameters injected by the parse_query decorator.
        The number property exposes a sanitized one-based page number.

    Returns
    -------
    Response
        HTML response containing either the full leads page or just
        the leads partial, depending on whether this is an HTMX request.
    """

    async with get_async_db_session() as session:
        total = await LeadRepository.count(session)

        skip, total_pages, current_page = calculate_pagination(
            total=total,
            page_size=server_config.page_size,
            current_page=params.number,
        )

        leads = await LeadRepository.get_all(
            session,
            skip=skip,
            limit=server_config.page_size,
        )

    is_htmx = request.headers.get("HX-Request") == "true"

    if is_htmx:
        return create_leads_partial(
            leads=leads,
            current_page=current_page,
            total_pages=total_pages,
        )

    return create_leads_page(
        leads=leads,
        current_page=current_page,
        total_pages=total_pages,
        role=user.role,
    )


@role_for_authorization(Role.MODERATOR)
@parse_form(LeadStatusForm)
async def lead_status_post(
    request: Request,
    user: SessionPayload,
    form: LeadStatusForm,
) -> Response:
    """
    Update the status of a collaboration request.

    Reads the lead id from the URL path and the target status from the
    validated form data. Validates that the status transition is legal
    for the current lead status, updates the lead record in the database,
    and returns the updated lead card partial so HTMX can replace the
    existing card in the DOM without a full page reload.

    Parameters
    ----------
    request : Request
        Incoming request object containing the session cookie and path
        parameters.
    user : SessionPayload
        Authenticated user payload injected by the role_for_authorization
        decorator. Contains the user identifier and access role.
    form : LeadStatusForm
        Parsed form data injected by the parse_form decorator. The status
        field is normalized on construction and exposes a parsed LeadStatus
        enum as the target_status property.

    Returns
    -------
    Response
        Updated lead card partial with the new status reflected in the
        badge and available transition buttons.

    Raises
    ------
    HTTPException
        400 Bad Request if the status value is invalid or the transition is
        not allowed for the current lead status.
        404 Not Found if no lead exists with the given id.
    """
    lead_id = int(request.path_params["id"])
    target_status = form.target_status

    if target_status is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid status.",
        )

    valid_transitions: dict[LeadStatus, list[LeadStatus]] = {
        LeadStatus.NEW: [LeadStatus.IN_PROGRESS, LeadStatus.ANSWERED, LeadStatus.REJECTED],
        LeadStatus.IN_PROGRESS: [LeadStatus.ANSWERED, LeadStatus.REJECTED],
        LeadStatus.ANSWERED: [],
        LeadStatus.REJECTED: [],
    }

    async with get_async_db_session() as session:
        lead = await LeadRepository.get_by_id(session, lead_id)

        if lead is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lead not found.",
            )

        current_status = LeadStatus(lead.status)

        if target_status not in valid_transitions[current_status]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status transition from {current_status.value} to {target_status.value}.",
            )

        updated = await LeadRepository.update_by_id(
            session,
            lead_id,
            obj_data={"status": target_status},
        )
        await session.commit()

    return create_lead_card(
        lead_id=updated.id,
        name=updated.name,
        email=updated.email,
        company=updated.company,
        message=updated.message,
        status=LeadStatus(updated.status),
    )