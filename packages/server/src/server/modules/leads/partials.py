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

# packages/server/src/server/modules/leads/partials.py
from fasthtml.common import Div, FT
from postgres_lib import Lead, LeadStatus
from .components import create_lead_card
from ...config import RoutePath
from ...shared.ui import create_pagination, create_empty_state


def _create_leads_list(
    leads: list[Lead],
    current_page: int,
    total_pages: int,
) -> Div:
    """
    Create the paginated list of collaboration request cards.

    Displays each lead as a card with status transition buttons and
    appends the pagination controls configured for HTMX-driven page
    transitions. The container carries an identifier so HTMX can
    target it for partial swaps during pagination.

    Parameters
    ----------
    leads : list[Lead]
        List of Lead ORM instances for the current page.
    current_page : int
        One-based index of the currently active page.
    total_pages : int
        Total number of pages available.

    Returns
    -------
    Div
        FastHTML div container holding the lead cards and
        pagination controls, identified for HTMX targeting.
    """
    return Div(
        *[
            create_lead_card(
                lead_id=lead.id,
                name=lead.name,
                email=lead.email,
                company=lead.company,
                message=lead.message,
                status=LeadStatus(lead.status),
            )
            for lead in leads
        ],
        create_pagination(
            current_page=current_page,
            total_pages=total_pages,
            endpoint=RoutePath.LEADS,
            target="#leads-list",
        ),
        id="leads-list",
    )


def create_leads_partial(
    leads: list[Lead],
    current_page: int,
    total_pages: int,
) -> FT:
    """
    Create the leads partial containing all collaboration requests.

    Each lead is rendered as a card with status transition buttons.
    Pagination is rendered below the list when there is more than one page.

    Parameters
    ----------
    leads : list[Lead]
        List of Lead ORM instances for the current page.
    current_page : int
        One-based index of the currently active page.
    total_pages : int
        Total number of pages available.

    Returns
    -------
    FT
        Div containing the leads list and pagination control, or an
        empty state message if no leads exist.
    """
    if not leads:
        return create_empty_state(
            "No collaboration requests found.",
            icon_name="inbox",
        )

    return _create_leads_list(leads, current_page, total_pages)