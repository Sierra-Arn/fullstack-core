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

# packages/server/src/server/modules/login/pages.py
from fasthtml.common import Div, H2, P, A, FT
from postgres_lib import Role
from .partials import create_login_form_partial
from ...config import RoutePath
from ...shared import create_icon
from ...shared.ui import create_layout


def _create_form_header() -> Div:
    """
    Create the introductory header for the login form.

    Displays a centered title and a brief call-to-action directing
    unregistered visitors to the registration page.

    Returns
    -------
    Div
        FastHTML container holding the heading and registration link,
        styled for visual hierarchy and proper spacing above the form.
    """
    return Div(
        H2(
            "Sign in",
            cls="text-2xl font-bold text-center mb-2",
        ),
        P(
            "Don't have an account? ",
            A(
                create_icon("user-plus", size=14, cls="inline-block mr-1"),
                "Register",
                href=RoutePath.REGISTER,
                cls="link link-primary",
            ),
            cls=(
                "text-sm text-base-content/60 "
                "text-center mb-6"
            ),
        ),
    )


def create_login_page(
    role: Role = Role.UNAUTHENTICATED,
    error: str | None = None,
) -> FT:
    """
    Create the public login page.

    Assembles the complete page layout containing a centered card with
    an introductory header and the login submission form. The page is
    accessible to all visitors, as authentication is the entry point
    for unauthenticated users. An optional error message can be passed
    to display authentication failure feedback above the form.

    Parameters
    ----------
    role : Role
        Resolved access role of the current user. Passed to the global
        layout to determine which navigation links are displayed.
        Default is UNAUTHENTICATED for anonymous visitors.
    error : str or None
        Optional error message string. When provided, it is passed
        to the login form partial to display an authentication failure
        alert. Default is None.

    Returns
    -------
    FT
        Fully assembled FastHTML document containing the complete
        login page layout.
    """
    return create_layout(
        Div(
            Div(
                _create_form_header(),
                create_login_form_partial(error=error),
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
        title="Sign in",
        role=role,
    )