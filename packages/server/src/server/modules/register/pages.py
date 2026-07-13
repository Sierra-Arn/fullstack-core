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

# packages/server/src/server/modules/register/pages.py
from fasthtml.common import Div, H2, P, A, FT
from postgres_lib import Role
from .partials import create_register_form_partial
from ...config import RoutePath
from ...shared import create_icon
from ...shared.ui import create_layout


def _create_form_header() -> Div:
    """
    Create the introductory header for the registration form.

    Displays a centered title and a brief call-to-action directing
    already registered users to the login page.

    Returns
    -------
    Div
        FastHTML container holding the heading and login link,
        styled for visual hierarchy and proper spacing above the form.
    """
    return Div(
        H2(
            "Create an account",
            cls="text-2xl font-bold text-center mb-2",
        ),
        P(
            "Already have an account? ",
            A(
                create_icon("arrow-right-on-rectangle", size=14, cls="inline-block mr-1"),
                "Sign in",
                href=RoutePath.LOGIN,
                cls="link link-primary",
            ),
            cls=(
                "text-sm text-base-content/60 "
                "text-center mb-6"
            ),
        ),
    )


def create_register_page(
    role: Role = Role.UNAUTHENTICATED,
    error: str | None = None,
) -> FT:
    """
    Create the public registration page.

    Assembles the complete page layout containing a centered card with
    an introductory header and the registration submission form. The
    page is accessible to all visitors, as registration is the entry
    point for new users. An optional error message can be passed to
    display registration failure feedback above the form.

    The form itself is rendered via create_register_form_partial so that
    the same markup is reused both on initial page load and in HTMX
    partial responses, avoiding duplication.

    Client-side validation via Alpine.js checks that the password and
    confirm password fields match before the form is submitted. Server-side
    validation catches duplicate email addresses and returns the form
    partial with an error alert.

    After successful registration the user is automatically authenticated
    and redirected to the inference page without an intermediate login step
    via an HX-Redirect response header.

    Parameters
    ----------
    role : Role
        Resolved access role of the current user. Passed to the global
        layout to determine which navigation links are displayed.
        Default is UNAUTHENTICATED for anonymous visitors.
    error : str or None
        Optional error message string. When provided, it is passed
        to the registration form partial to display a registration
        failure alert. Default is None.

    Returns
    -------
    FT
        Fully assembled FastHTML document containing the complete
        registration page layout.
    """
    return create_layout(
        Div(
            Div(
                _create_form_header(),
                create_register_form_partial(error=error),
                cls=(
                    "card bg-base-100 shadow-sm "
                    "p-8 w-full max-w-md"
                ),
            ),
            cls=(
                "flex justify-center "
                "items-center min-h-[70vh]"
            ),
        ),
        title="Register",
        role=role,
    )