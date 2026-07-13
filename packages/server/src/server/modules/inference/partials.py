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

# packages/server/src/server/modules/inference/partials.py
from datetime import datetime
from fasthtml.common import Div, Form, Textarea, Button, FT
from .components import create_inference_card
from ...config import RoutePath
from ...shared import create_icon
from ...shared.ui import (
    create_alert,
    create_form_alert_slot,
    Alert,
    create_spinner,
    create_form_control
)


def _create_inference_form() -> Form:
    """
    Create the inference submission form.

    Assembles the textarea input for the model prompt and the submit
    button. Configured to submit asynchronously via HTMX and replace
    the result container in the DOM upon receiving a server response.

    The submit button is disabled while a task is running via Alpine.js
    to prevent duplicate submissions.

    Returns
    -------
    Form
        FastHTML form element configured for HTMX submission,
        containing the prompt textarea and submit button.
    """
    return Form(
        create_form_control(
            "Prompt",
            "input_text",
            Textarea(
                id="input_text",
                name="input_text",
                placeholder="Enter your prompt here...",
                required=True,
                rows="6",
                cls="textarea textarea-bordered w-full",
            ),
        ),
        Button(
            create_icon("sparkles", size=20, cls="mr-2"),
            "Submit",
            type="submit",
            **{":disabled": "running"},
            cls="btn btn-primary w-full",
        ),
        hx_post=RoutePath.INFERENCE,
        hx_target="#inference-result",
        hx_swap="innerHTML",
        **{"@submit": "running = true"},
    )


def create_inference_form_partial(
    error: str | None = None,
) -> FT:
    """
    Create the inference form and result container as a standalone partial.

    Designed to be rendered on initial page load and returned by POST
    handlers when validation fails, allowing the same markup to be reused
    in both contexts without duplication. The result container is initially
    empty and becomes visible only after the first submission.

    The form posts to /inference which enqueues a Celery task and returns
    a spinner partial with a polling trigger. The spinner is rendered
    inside the result container and replaced by the final output once
    the task completes.

    The submit button is disabled while a task is running via Alpine.js
    to prevent duplicate submissions. The result container listens for
    HTMX settle events to reset the running flag once the polling loop
    completes and the final result has been rendered.

    Parameters
    ----------
    error : str or None
        Optional error message string. When provided, an error alert
        is displayed above the form to inform the user of validation
        failures or quota exhaustion. Default is None.

    Returns
    -------
    FT
        FastHTML div container holding the conditional error alert,
        the inference form, and the result container, ready for
        rendering or HTMX swap.
    """
    return Div(
        create_form_alert_slot(error=error),
        Div(
            _create_inference_form(),
            cls="card bg-base-100 shadow-sm p-6 mb-6",
        ),
        Div(
            id="inference-result",
            **{
                "@htmx:after-settle": "if (!$el.querySelector('[hx-trigger]')) running = false"
            },
        ),
        id="inference-form",
    )


def create_inference_error_partial(error: str) -> FT:
    """
    Create an inline error alert for the inference result container.

    Returned by the POST handler when the inference quota is exceeded
    and swapped into #inference-result via HTMX. Does not include a
    form, navbar, or footer; only the alert message.

    Parameters
    ----------
    error : str
        Error message to display inside the alert.

    Returns
    -------
    FT
        Alert partial ready for HTMX innerHTML swap into
        the inference-result container.
    """
    return Div(
        create_alert(
            error,
            Alert.ERROR,
        )
    )


def create_inference_pending_partial(task_id: str) -> FT:
    """
    Create a polling partial inserted into the inference result container
    immediately after a task is enqueued.

    The partial renders a spinner and configures HTMX to poll the task
    status endpoint every second. On each poll the server inspects the
    Celery result backend and returns either this same partial again
    (task still running) or the result partial (task complete), at which
    point HTMX replaces the container content and polling stops because
    the returned partial carries no hx-trigger attribute.

    Parameters
    ----------
    task_id : str
        Celery task identifier returned by the broker on enqueue, used
        to construct the polling URL.

    Returns
    -------
    FT
        Div containing the spinner and HTMX polling attributes, ready
        for insertion into the inference result container.
    """
    return Div(
        create_spinner(),
        hx_get=RoutePath.INFERENCE_STATUS.format(task_id=task_id),
        hx_trigger="every 1s",
        hx_target="#inference-result",
        hx_swap="innerHTML",
    )


def create_inference_result_partial(
    input_text: str,
    output_text: str,
    created_at: datetime,
) -> FT:
    """
    Create the completed inference result partial inserted into the
    inference result container once the Celery task finishes.

    Returned by the status polling endpoint when AsyncResult indicates
    the task is complete. Carries no HTMX polling attributes so the
    one-second polling loop initiated by create_inference_pending_partial
    stops naturally when this partial replaces the container content.

    Parameters
    ----------
    input_text : str
        Raw text submitted by the user as the model prompt. Passed
        through from the Celery task result for display purposes.
    output_text : str
        Text generated by the model in response to the prompt.
    created_at : datetime
        UTC timestamp of the completed inference run. For authenticated
        users this is the timestamp recorded in the database by the
        Celery worker.

    Returns
    -------
    FT
        Div containing the inference card, ready for insertion into
        the inference result container.
    """
    return Div(
        create_inference_card(
            input_text=input_text,
            output_text=output_text,
            created_at=created_at,
        )
    )