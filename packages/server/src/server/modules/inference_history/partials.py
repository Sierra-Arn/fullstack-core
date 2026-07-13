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

# packages/server/src/server/modules/inference_history/partials.py
from fasthtml.common import Div, FT
from postgres_lib.models import InferenceHistory
from ..inference.components import create_inference_card
from ...shared.ui import create_pagination, create_empty_state
from ...config import RoutePath


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


def create_inference_history_partial(
    records: list[InferenceHistory],
    current_page: int,
    total_pages: int,
) -> FT:
    """
    Create the inference history partial containing paginated records.

    Each record is rendered as an inference card showing the submitted
    prompt, the model response, and the timestamp. Pagination is rendered
    below the list when there is more than one page.

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
    FT
        Div containing the records list and pagination control, or an
        empty state message if no records exist.
    """
    if not records:
        return create_empty_state(
            "You have not made any inference requests yet.",
            icon_name="sparkles",
        )

    return _create_records_list(records, current_page, total_pages)