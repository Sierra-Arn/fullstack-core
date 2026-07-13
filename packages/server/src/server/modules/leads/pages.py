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

# packages/server/src/server/modules/leads/pages.py
from fasthtml.common import Div, H2, FT
from postgres_lib.models import Lead
from postgres_lib import Role
from .partials import create_leads_partial
from ...shared import create_icon
from ...shared.ui import create_layout


def _create_page_header() -> Div:
    """
    Create the introductory header for the leads page.

    Displays a title with an inbox icon for the leads section.

    Returns
    -------
    Div
        FastHTML container holding the heading, styled for visual
        hierarchy and proper spacing above the content.
    """
    return Div(
        H2(
            create_icon("inbox", size=28, cls="inline-block mr-2 align-middle"),
            "Collaboration Requests",
            cls="text-2xl font-bold mb-6",
        ),
    )


def create_leads_page(
    leads: list[Lead],
    current_page: int,
    total_pages: int,
    role: Role = Role.MODERATOR,
) -> FT:
    """
    Create the leads page for moderators and administrators.

    Displays a paginated list of collaboration requests with status
    transition controls. Each request is rendered as a card showing
    the submitted information and available actions based on the
    current status. When no requests exist, a neutral empty state
    message is shown instead of an empty list.

    Parameters
    ----------
    leads : list[Lead]
        List of Lead ORM instances for the current page.
    current_page : int
        One-based index of the currently active page.
    total_pages : int
        Total number of pages available.
    role : Role
        Resolved access role of the current user. Passed to the global
        layout to determine which navigation links are displayed.
        Default is MODERATOR since this page requires at least that role.

    Returns
    -------
    FT
        Fully assembled FastHTML document containing the complete
        leads page layout.
    """
    return create_layout(
        Div(
            _create_page_header(),
            create_leads_partial(leads, current_page, total_pages),
            cls="max-w-4xl mx-auto py-8",
        ),
        title="Leads",
        role=role,
    )