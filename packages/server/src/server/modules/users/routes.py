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

# packages/server/src/server/modules/users/routes.py
from starlette import status
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import Response
from postgres_lib import get_async_db_session, UserRepository, Role
from session_lib import SessionPayload
from .components import create_user_card
from .partials import create_users_partial
from .pages import create_users_page
from .schemas import UserRoleForm
from ...shared import (
    role_for_authorization,
    calculate_pagination,
    parse_query,
    parse_form,
    PageQuery,
)
from ...config import server_config


@role_for_authorization(Role.ADMIN)
@parse_query(PageQuery)
async def users_get(
    request: Request,
    user: SessionPayload,
    params: PageQuery,
) -> Response:
    """
    Render the users page or partial based on request type.

    For regular HTTP requests, renders the complete users page with
    navbar and footer. For HTMX requests (pagination), returns only
    the users partial without layout to avoid duplicating navbar and
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
        HTML response containing either the full users page or just
        the users partial, depending on whether this is an HTMX request.
    """
    async with get_async_db_session() as session:
        total = await UserRepository.count(session)

        skip, total_pages, current_page = calculate_pagination(
            total=total,
            page_size=server_config.page_size,
            current_page=params.number,
        )

        users = await UserRepository.get_all(
            session,
            skip=skip,
            limit=server_config.page_size,
        )

    is_htmx = request.headers.get("HX-Request") == "true"

    if is_htmx:
        return create_users_partial(
            users=users,
            current_page=current_page,
            total_pages=total_pages,
        )

    return create_users_page(
        users=users,
        current_page=current_page,
        total_pages=total_pages,
        role=user.role,
    )


@role_for_authorization(Role.ADMIN)
@parse_form(UserRoleForm)
async def user_role_post(
    request: Request,
    user: SessionPayload,
    form: UserRoleForm,
) -> Response:
    """
    Change the role of a user account.

    Reads the user id from the URL path and the target role from the
    validated form data. Validates that the target role differs from
    the current role, then updates the record in the database. Returns
    the updated user card partial so HTMX can replace the existing card
    in the DOM without a full page reload.

    Parameters
    ----------
    request : Request
        Incoming request object containing the session cookie and path
        parameters.
    user : SessionPayload
        Authenticated user payload injected by the role_for_authorization
        decorator. Contains the user identifier and access role.
    form : UserRoleForm
        Parsed form data injected by the parse_form decorator. The role
        field is normalized on construction and exposes a parsed Role enum
        as the target_role property.

    Returns
    -------
    Response
        Updated user card partial with the new role reflected in the
        badge and the pre-selected dropdown option.

    Raises
    ------
    HTTPException
        400 Bad Request if the role value is not a valid role or is
        unchanged.
        404 Not Found if no user exists with the given id.
    """
    user_id = int(request.path_params["id"])
    target_role = form.target_role

    if target_role is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role.",
        )

    async with get_async_db_session() as session:
        target_user = await UserRepository.get_by_id(session, user_id)

        if target_user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found.",
            )

        if target_user.role == target_role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already has this role.",
            )

        updated = await UserRepository.update_by_id(
            session,
            user_id,
            obj_data={"role": target_role},
        )
        await session.commit()

    return create_user_card(
        user_id=updated.id,
        email=updated.email,
        role=updated.role,
        inference_runs_count=updated.inference_runs_count,
        created_at=updated.created_at,
    )


@role_for_authorization(Role.ADMIN)
async def user_delete_post(request: Request, user: SessionPayload) -> Response:
    """
    Permanently delete a user account and all associated records.

    Reads the user id from the URL path and deletes the record from
    the database. Associated inference history records are deleted
    automatically via the CASCADE constraint defined on the foreign key.
    Returns an empty response so HTMX removes the card from the DOM.

    Parameters
    ----------
    request : Request
        Incoming request object containing the session cookie and
        path parameters.
    user : SessionPayload
        Authenticated user payload injected by the role_for_authorization
        decorator. Contains the user identifier and access role.

    Returns
    -------
    Response
        Empty HTTP 200 response causing HTMX to replace the card with
        nothing, effectively removing it from the DOM.

    Raises
    ------
    HTTPException
        404 Not Found if no user exists with the given id.
    """
    user_id = int(request.path_params["id"])

    async with get_async_db_session() as session:
        target_user = await UserRepository.get_by_id(session, user_id)

        if target_user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found.",
            )

        await UserRepository.delete_by_id(session, user_id)
        await session.commit()

    return Response(status_code=status.HTTP_200_OK)