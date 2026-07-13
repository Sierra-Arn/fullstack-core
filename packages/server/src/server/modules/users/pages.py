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

# packages/server/src/server/modules/users/pages.py
from fasthtml.common import Div, H2, FT
from postgres_lib import User, Role
from .partials import create_users_partial
from ...shared import create_icon
from ...shared.ui import create_layout


def _create_page_header() -> Div:
    """
    Create the introductory header for the users page.

    Displays a title with a users icon for the users section.

    Returns
    -------
    Div
        FastHTML container holding the heading, styled for visual
        hierarchy and proper spacing above the content.
    """
    return Div(
        H2(
            create_icon("users", size=28, cls="inline-block mr-2 align-middle"),
            "Registered Users",
            cls="text-2xl font-bold mb-6",
        ),
    )


def create_users_page(
    users: list[User],
    current_page: int,
    total_pages: int,
    role: Role = Role.ADMIN,
) -> FT:
    """
    Create the users page for administrators.

    Displays a paginated list of registered users with role management
    and deletion controls. Each user is rendered as a card showing
    account details and available actions. When no users exist, a
    neutral empty state message is shown instead of an empty list.

    Parameters
    ----------
    users : list[User]
        List of User ORM instances for the current page.
    current_page : int
        One-based index of the currently active page.
    total_pages : int
        Total number of pages available.
    role : Role
        Resolved access role of the current user. Passed to the global
        layout to determine which navigation links are displayed.
        Default is ADMIN since this page requires administrator role.

    Returns
    -------
    FT
        Fully assembled FastHTML document containing the complete
        users page layout.
    """
    return create_layout(
        Div(
            _create_page_header(),
            create_users_partial(users, current_page, total_pages),
            cls="max-w-4xl mx-auto py-8",
        ),
        title="Users",
        role=role,
    )