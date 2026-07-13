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

# packages/server/src/server/modules/login/partials.py
from fasthtml.common import Div, Form, Input, Button, FT
from ...config import RoutePath
from ...shared import create_icon
from ...shared.ui import create_form_alert_slot, create_form_control


def _create_login_form() -> Form:
    """
    Create the login submission form.

    Assembles all required input fields for a user to authenticate.
    Configured to submit asynchronously via HTMX and replace its own
    container in the DOM upon receiving a server response.

    Returns
    -------
    Form
        FastHTML form element configured for HTMX submission,
        containing fields for email and password.
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
                placeholder="*******",
                required=True,
                cls="input input-bordered w-full",
            ),
            margin_bottom="mb-6",
        ),
        Button(
            create_icon("arrow-right-on-rectangle", size=20, cls="mr-2"),
            "Sign in",
            type="submit",
            cls="btn btn-primary w-full",
        ),
        novalidate=True,
        hx_post=RoutePath.LOGIN,
        hx_target="#login-form",
        hx_swap="outerHTML",
        id="login-form",
    )


def create_login_form_partial(
    error: str | None = None,
) -> FT:
    """
    Create an HTMX partial response containing the login form.

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
        is displayed above the form to inform the user of authentication
        failures or validation issues. Default is None.

    Returns
    -------
    FT
        FastHTML div container holding the conditional error alert
        and the login form, ready to be swapped into the client DOM.
    """
    return Div(
        create_form_alert_slot(error=error),
        _create_login_form(),
        id="login-form",
    )