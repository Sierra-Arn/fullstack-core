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

# packages/server/src/server/modules/collaborate/pages.py
from fasthtml.common import Div, H2, P, FT
from postgres_lib import Role
from .partials import create_collaborate_form_partial
from ...shared import create_icon
from ...shared.ui import create_layout


def _create_form_header() -> Div:
    """
    Create the introductory header for the collaboration form.

    Displays a centered title and a brief description explaining the
    purpose of the form to the visitor.

    Returns
    -------
    Div
        FastHTML container holding the heading and descriptive paragraph,
        styled for visual hierarchy and proper spacing above the form.
    """
    return Div(
        H2(
            create_icon("briefcase", size=28, cls="inline-block mr-2 align-middle"),
            "Work with us",
            cls="text-2xl font-bold text-center mb-2",
        ),
        P(
            "Tell us about your use case and we will get back to you.",
            cls=(
                "text-sm text-base-content/60 "
                "text-center mb-6"
            ),
        ),
    )


def create_collaborate_page(
    role: Role = Role.UNAUTHENTICATED,
) -> FT:
    """
    Create the public collaboration request page.

    Assembles the complete page layout containing a centered card with
    an introductory header and the collaboration request submission form.
    The page is accessible to all visitors regardless of their
    authentication state, as collaboration requests are intended for
    both unauthenticated prospects and registered users.

    Parameters
    ----------
    role : Role
        Resolved access role of the current user. Passed to the global
        layout to determine which navigation links are displayed.
        Default is UNAUTHENTICATED for anonymous visitors.

    Returns
    -------
    FT
        Fully assembled FastHTML document containing the complete
        collaboration page layout.
    """
    return create_layout(
        Div(
            Div(
                _create_form_header(),
                create_collaborate_form_partial(),
                cls=(
                    "card bg-base-100 shadow-sm "
                    "p-8 w-full max-w-lg"
                ),
            ),
            cls=(
                "flex justify-center "
                "items-center min-h-[70vh]"
            ),
        ),
        title="Collaborate",
        role=role,
    )