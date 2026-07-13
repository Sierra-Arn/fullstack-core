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

# packages/server/src/server/modules/inference/routes.py
from datetime import datetime, timezone
from starlette import status
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import Response
from celery.result import AsyncResult
from celery_lib import celery_app, celery_config
from postgres_lib import get_async_db_session, UserRepository, Role
from session_lib import SessionPayload
from .pages import create_inference_page
from .partials import (
    create_inference_error_partial,
    create_inference_pending_partial,
    create_inference_result_partial,
)
from .schemas import InferenceForm
from ...shared import role_for_authorization, parse_form
from ...config import server_config


@role_for_authorization(Role.USER)
async def inference_get(request: Request, user: SessionPayload) -> Response:
    """
    Render the inference page for authenticated users.

    Parameters
    ----------
    request : Request
        The incoming HTTP request object containing the session cookie.
    user : SessionPayload
        Authenticated user payload injected by the role_for_authorization
        decorator. Contains the user identifier and access role.

    Returns
    -------
    Response
        HTML response containing the rendered inference page.
    """
    return create_inference_page(role=user.role)


@role_for_authorization(Role.USER)
@parse_form(InferenceForm)
async def inference_post(request: Request, user: SessionPayload, form: InferenceForm) -> Response:
    """
    Enqueue a model inference task and return a polling partial.

    Normalizes and validates the prompt, then checks the user inference
    quota against the configured maximum before enqueuing. An empty prompt
    or an exhausted quota returns an error alert partial inserted into the
    result container without dispatching any task, leaving the prompt form
    intact so the user does not need to reload the page. On success enqueues
    the Celery task and returns the pending partial which initiates HTMX
    polling.

    Parameters
    ----------
    request : Request
        The incoming HTTP request containing the session cookie and
        form data with the prompt text.
    user : SessionPayload
        Authenticated user payload injected by the role_for_authorization
        decorator. Contains the user identifier and access role.
    form : InferenceForm
        Parsed form data injected by the parse_form decorator. The prompt
        field is normalized on construction and exposes a non-empty check
        as a property.

    Returns
    -------
    Response
        Pending partial with HTMX polling attributes on success, or an error
        alert partial if the prompt is empty or the quota is exceeded.

    Raises
    ------
    HTTPException
        403 Forbidden if the user record no longer exists in the database.
    """
    if not form.has_input:
        return create_inference_error_partial(
            error="Prompt is required.",
        )

    async with get_async_db_session() as session:
        db_user = await UserRepository.get_by_id(session, user.user_id)

        if db_user is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access forbidden.",
            )

        if db_user.inference_runs_count >= server_config.inference_quota:
            return create_inference_error_partial(
                error="You have exceeded your inference quota.",
            )

    task = celery_app.send_task(
        celery_config.task_name_inference,
        args=[form.input_text, user.user_id],
        queue=celery_config.queue_name_inference,
    )

    return create_inference_pending_partial(task_id=task.id)


@role_for_authorization(Role.USER)
async def inference_status_get(request: Request, user: SessionPayload) -> Response:
    """
    Poll the status of a Celery inference task.

    Reads the task identifier from the URL path and checks the Celery
    result backend. Returns the pending partial if the task is still
    running so HTMX continues polling, or the result partial if the
    task has completed, which stops the polling loop.

    Parameters
    ----------
    request : Request
        The incoming HTTP request object containing the session cookie
        and path parameters with the task identifier.
    user : SessionPayload
        Authenticated user payload injected by the role_for_authorization
        decorator. Contains the user identifier and access role.

    Returns
    -------
    Response
        Pending partial if the task is still running, or result partial
        if the task has completed.
    """
    task_id = request.path_params["task_id"]
    result = AsyncResult(task_id, app=celery_app)

    if not result.ready():
        return create_inference_pending_partial(task_id=task_id)

    payload = result.get()

    return create_inference_result_partial(
        input_text=payload["input_text"],
        output_text=payload["output_text"],
        created_at=datetime.now(timezone.utc),
    )