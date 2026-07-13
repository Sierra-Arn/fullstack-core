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

# packages/server/src/server/modules/inference_history/routes.py
from starlette.requests import Request
from starlette.responses import Response
from postgres_lib import get_async_db_session, InferenceHistoryRepository, Role
from session_lib import SessionPayload
from .partials import create_inference_history_partial
from .pages import create_inference_history_page
from ...shared import (
    role_for_authorization,
    calculate_pagination,
    parse_query,
    PageQuery,
)
from ...config import server_config


@role_for_authorization(Role.USER)
@parse_query(PageQuery)
async def inference_history_get(
    request: Request,
    user: SessionPayload,
    params: PageQuery,
) -> Response:
    """
    Render the inference history page or partial based on request type.

    For regular HTTP requests, renders the complete inference history
    page with navbar and footer. For HTMX requests (pagination), returns
    only the history records without layout to avoid duplicating navbar
    and footer in the DOM.

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
        HTML response containing either the full inference history page
        or just the records list, depending on whether this is an HTMX
        request.
    """

    async with get_async_db_session() as session:
        total = await InferenceHistoryRepository.count_by_user_id(
            session,
            user_id=user.user_id,
        )

        skip, total_pages, current_page = calculate_pagination(
            total=total,
            page_size=server_config.page_size,
            current_page=params.number,
        )

        records = await InferenceHistoryRepository.get_by_user_id(
            session,
            user_id=user.user_id,
            skip=skip,
            limit=server_config.page_size,
        )

    is_htmx = request.headers.get("HX-Request") == "true"

    if is_htmx:
        return create_inference_history_partial(
            records=records,
            current_page=current_page,
            total_pages=total_pages,
        )

    return create_inference_history_page(
        records=records,
        current_page=current_page,
        total_pages=total_pages,
        role=user.role,
    )