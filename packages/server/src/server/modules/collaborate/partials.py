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

# packages/server/src/server/modules/collaborate/partials.py
from fasthtml.common import Div, Form, Input, Textarea, Button, FT
from ...config import RoutePath
from ...shared import create_icon
from ...shared.ui import create_form_alert_slot, create_form_control


def _create_collaborate_form() -> Form:
    """
    Create the collaboration request submission form.

    Assembles all required input fields for a visitor to submit a
    collaboration request. Configured to submit asynchronously via
    HTMX and replace its own container in the DOM upon receiving
    a server response.

    Returns
    -------
    Form
        FastHTML form element configured for HTMX submission,
        containing fields for visitor information and project details.
    """
    return Form(
        create_form_control(
            "Name",
            "name",
            Input(
                id="name",
                name="name",
                type="text",
                placeholder="John Doe",
                required=True,
                cls="input input-bordered w-full",
            ),
        ),
        create_form_control(
            "Email",
            "email",
            Input(
                id="email",
                name="email",
                type="email",
                placeholder="you@example.com",
                required=True,
                cls="input input-bordered w-full",
            ),
        ),
        create_form_control(
            "Company",
            "company",
            Input(
                id="company",
                name="company",
                type="text",
                placeholder="Acme Inc.",
                cls="input input-bordered w-full",
            ),
            label_hint="optional",
        ),
        create_form_control(
            "Message",
            "message",
            Textarea(
                id="message",
                name="message",
                placeholder="Tell us about your use case...",
                required=True,
                rows="5",
                cls="textarea textarea-bordered w-full",
            ),
            margin_bottom="mb-6",
        ),
        Button(
            create_icon("paper-airplane", size=20, cls="mr-2"),
            "Send request",
            type="submit",
            cls="btn btn-primary w-full",
        ),
        hx_post=RoutePath.COLLABORATE,
        hx_target="#collaborate-form",
        hx_swap="outerHTML",
        id="collaborate-form",
    )


def create_collaborate_form_partial(
    success: bool = False,
    error: str | None = None,
) -> FT:
    """
    Create an HTMX partial response containing the collaboration form.

    Designed to be returned directly from HTMX route handlers to replace
    the existing form markup in the client DOM. Conditionally renders
    success or error alerts above the form based on the provided state
    flags. The form itself is configured to submit via HTMX and replace
    its own outer HTML upon receiving a response, allowing seamless
    inline validation and success feedback without full page reloads.

    Parameters
    ----------
    success : bool
        Whether to display a success confirmation alert above the form.
        Default is False.
    error : str or None
        Optional error message string. When provided, an error alert is
        displayed above the form to inform the user of validation failures
        or submission issues. Default is None.

    Returns
    -------
    FT
        FastHTML div container holding the conditional alert messages
        and the collaboration form, ready to be swapped into the client DOM.
    """
    return Div(
        create_form_alert_slot(
            success=(
                "Your request has been submitted. "
                "We will get back to you shortly."
                if success
                else None
            ),
            error=error,
        ),
        _create_collaborate_form(),
        id="collaborate-form",
    )