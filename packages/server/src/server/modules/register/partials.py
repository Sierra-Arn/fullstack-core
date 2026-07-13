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

# packages/server/src/server/modules/register/partials.py
from fasthtml.common import Div, Form, Input, Button, Label, Span, FT
from ...config import RoutePath
from ...shared import create_icon
from ...shared.ui import create_form_alert_slot, create_form_control


def _create_password_match_error() -> Span:
    """
    Create the client-side password mismatch error message.

    Displayed below the confirm password field when the two password
    inputs do not match. Visibility is controlled by Alpine.js based
    on the reactive form state.

    Returns
    -------
    Span
        FastHTML span element with Alpine.js x-show directive for
        conditional visibility.
    """
    return Span(
        create_icon("exclamation-circle", size=14, cls="inline-block mr-1"),
        "Passwords do not match",
        **{
            "x-show": "confirm_password.length > 0 && password !== confirm_password",
        },
        cls="text-error text-xs mt-1",
    )


def _create_register_form() -> Form:
    """
    Create the registration submission form.

    Assembles all required input fields for a new user to register,
    including email, password, and password confirmation. Configured
    to submit asynchronously via HTMX and replace its own container
    in the DOM upon receiving a server response.

    Client-side validation via Alpine.js checks that the password and
    confirm password fields match before the form is submitted. The
    submit button is disabled until both fields are non-empty and
    identical. Browser-native validation is disabled via novalidate
    so all validation feedback is handled consistently through the
    server response and Alpine.js rather than browser-specific popups.

    Returns
    -------
    Form
        FastHTML form element configured for HTMX submission,
        containing fields for email, password, and confirmation.
    """
    return Form(
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
            "Password",
            "password",
            Input(
                id="password",
                name="password",
                type="password",
                placeholder="••••••••",
                required=True,
                **{"x-model": "password"},
                cls="input input-bordered w-full",
            ),
        ),
        Div(
            Label(
                "Confirm password",
                fr="confirm_password",
                cls="label label-text",
            ),
            Input(
                id="confirm_password",
                name="confirm_password",
                type="password",
                placeholder="••••••••",
                required=True,
                **{"x-model": "confirm_password"},
                cls="input input-bordered w-full",
            ),
            _create_password_match_error(),
            cls="form-control mb-6",
        ),
        Button(
            create_icon("user-plus", size=20, cls="mr-2"),
            "Create account",
            type="submit",
            **{
                ":disabled": "confirm_password.length === 0 || password !== confirm_password",
            },
            cls="btn btn-primary w-full",
        ),
        novalidate=True,
        hx_post=RoutePath.REGISTER,
        hx_target="#register-form",
        hx_swap="outerHTML",
        id="register-form",
    )


def create_register_form_partial(
    error: str | None = None,
) -> FT:
    """
    Create an HTMX partial response containing the registration form.

    Designed to be returned directly from HTMX route handlers to replace
    the existing form markup in the client DOM. Conditionally renders
    an error alert above the form based on the provided error message.
    The form itself is configured to submit via HTMX and replace its
    own outer HTML upon receiving a response, allowing seamless inline
    validation feedback without full page reloads.

    Parameters
    ----------
    error : str or None
        Optional error message string. When provided, an error alert
        is displayed above the form to inform the user of registration
        failures such as duplicate email addresses. Default is None.

    Returns
    -------
    FT
        FastHTML div container holding the conditional error alert
        and the registration form, ready to be swapped into the client DOM.
    """
    return Div(
        create_form_alert_slot(error=error),
        _create_register_form(),
        id="register-form",
        **{"x-data": "{ password: '', confirm_password: '' }"},
    )