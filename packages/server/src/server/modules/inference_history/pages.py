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

# packages/server/src/server/modules/inference_history/pages.py
from fasthtml.common import Div, H2, FT
from postgres_lib.models import InferenceHistory
from postgres_lib import Role
from ..inference.components import create_inference_card
from ...config import RoutePath
from ...shared import create_icon
from ...shared.ui import create_layout, create_pagination, create_empty_state


def _create_page_header() -> Div:
    """
    Create the introductory header for the inference history page.

    Displays a title with a clock icon for the history section.

    Returns
    -------
    Div
        FastHTML container holding the heading, styled for visual
        hierarchy and proper spacing above the content.
    """
    return Div(
        H2(
            create_icon("clock", size=28, cls="inline-block mr-2 align-middle"),
            "Inference History",
            cls="text-2xl font-bold mb-6",
        ),
    )


def _create_records_list(
    records: list[InferenceHistory],
    current_page: int,
    total_pages: int,
) -> Div:
    """
    Create the paginated list of inference history records.

    Displays each record as an inference card and appends the
    pagination controls configured for HTMX-driven page transitions.
    The container carries an identifier so HTMX can target it for
    partial swaps during pagination.

    Parameters
    ----------
    records : list[InferenceHistory]
        List of InferenceHistory ORM instances for the current page,
        ordered by created_at descending.
    current_page : int
        One-based index of the currently active page.
    total_pages : int
        Total number of pages available.

    Returns
    -------
    Div
        FastHTML div container holding the inference cards and
        pagination controls, identified for HTMX targeting.
    """
    return Div(
        *[
            create_inference_card(
                input_text=record.input_text,
                output_text=record.output_text,
                created_at=record.created_at,
            )
            for record in records
        ],
        create_pagination(
            current_page=current_page,
            total_pages=total_pages,
            endpoint=RoutePath.INFERENCE_HISTORY,
            target="#history-list",
        ),
        id="history-list",
    )


def create_inference_history_page(
    records: list[InferenceHistory],
    current_page: int,
    total_pages: int,
    role: Role = Role.USER,
) -> FT:
    """
    Create the inference history page for the authenticated user.

    Displays a paginated list of completed inference runs ordered by
    most recent first. Each record is rendered as a card showing the
    submitted prompt, the model response, and the timestamp. When no
    records exist a neutral empty state message is shown instead of
    an empty list.

    Parameters
    ----------
    records : list[InferenceHistory]
        List of InferenceHistory ORM instances for the current page,
        ordered by created_at descending.
    current_page : int
        One-based index of the currently active page.
    total_pages : int
        Total number of pages available.
    role : Role
        Resolved access role of the current user. Passed to the global
        layout to determine which navigation links are displayed.
        Default is USER since this page requires authentication.

    Returns
    -------
    FT
        Fully assembled FastHTML document containing the complete
        inference history page layout.
    """
    content = (
        create_empty_state(
            "You have not made any inference requests yet.",
            icon_name="sparkles",
        )
        if not records
        else _create_records_list(records, current_page, total_pages)
    )

    return create_layout(
        Div(
            _create_page_header(),
            content,
        ),
        title="History",
        role=role,
    )