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

# packages/server/src/server/modules/users/partials.py
from fasthtml.common import Div, FT
from postgres_lib.models import User
from .components import create_user_card
from ...config import RoutePath
from ...shared.ui import create_pagination, create_empty_state


def _create_users_list(
    users: list[User],
    current_page: int,
    total_pages: int,
) -> Div:
    """
    Create the paginated list of user cards.

    Displays each user as a card with role toggle and delete action
    buttons, and appends the pagination controls configured for
    HTMX-driven page transitions. The container carries an identifier
    so HTMX can target it for partial swaps during pagination.

    Parameters
    ----------
    users : list[User]
        List of User ORM instances for the current page.
    current_page : int
        One-based index of the currently active page.
    total_pages : int
        Total number of pages available.

    Returns
    -------
    Div
        FastHTML div container holding the user cards and
        pagination controls, identified for HTMX targeting.
    """
    return Div(
        *[
            create_user_card(
                user_id=user.id,
                email=user.email,
                role=user.role,
                inference_runs_count=user.inference_runs_count,
                created_at=user.created_at,
            )
            for user in users
        ],
        create_pagination(
            current_page=current_page,
            total_pages=total_pages,
            endpoint=RoutePath.USERS,
            target="#users-list",
        ),
        id="users-list",
    )


def create_users_partial(
    users: list[User],
    current_page: int,
    total_pages: int,
) -> FT:
    """
    Create the users partial containing all registered accounts.

    Each user is rendered as a card with role toggle and delete action
    buttons. Pagination is rendered below the list when there is more
    than one page.

    Parameters
    ----------
    users : list[User]
        List of User ORM instances for the current page.
    current_page : int
        One-based index of the currently active page.
    total_pages : int
        Total number of pages available.

    Returns
    -------
    FT
        Div containing the users list and pagination control, or an
        empty state message if no users exist.
    """
    if not users:
        return create_empty_state(
            "No registered users found.",
            icon_name="users",
        )

    return _create_users_list(users, current_page, total_pages)