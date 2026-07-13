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

# packages/server/src/server/modules/inference/components.py
from datetime import datetime
from fasthtml.common import Div, P, Span, FT
from ...shared import create_icon


def _create_section_label(text: str, icon_name: str | None = None) -> Span:
    """
    Create a styled section label for the inference card.

    Encapsulates the repetitive styling applied to section headers
    such as "Prompt", "Response", and user identifiers. Optionally
    includes a leading icon for visual distinction.

    Parameters
    ----------
    text : str
        Label text to display.
    icon_name : str or None
        Optional Heroicon name to display before the label text.
        When None, only the text is rendered. Default is None.

    Returns
    -------
    Span
        FastHTML span element styled as a small uppercase label
        with optional leading icon.
    """
    children = []

    if icon_name:
        children.append(
            create_icon(icon_name, size=14, cls="inline-block mr-1 align-middle")
        )

    children.append(text)

    return Span(
        *children,
        cls="text-xs font-semibold text-base-content/50 uppercase tracking-wide",
    )


def _create_content_block(
    label: str,
    content: str,
    icon_name: str | None = None,
) -> Div:
    """
    Create a labeled content block for the inference card.

    Combines a section label with the actual content text, providing
    consistent spacing and visual hierarchy across all card sections.

    Parameters
    ----------
    label : str
        Section header text (e.g., "Prompt", "Response").
    content : str
        The actual content to display below the label.
    icon_name : str or None
        Optional Heroicon name to display in the label for visual
        distinction. When None, only the text label is shown.
        Default is None.

    Returns
    -------
    Div
        FastHTML div container holding the label and content,
        styled with proper spacing.
    """
    return Div(
        _create_section_label(label, icon_name=icon_name),
        P(
            content,
            cls="text-base-content mt-1",
        ),
        cls="mb-4",
    )


def _create_user_header(user_id: int) -> Div:
    """
    Create the user identifier header for administrative context.

    Displayed only when the inference card is rendered in an
    administrative view where multiple users' records are shown
    together. On the user's own history page this header is omitted.

    Parameters
    ----------
    user_id : int
        Primary key of the user who submitted the inference request.

    Returns
    -------
    Div
        FastHTML div container holding the user identifier label,
        styled for visual separation from the card content.
    """
    return Div(
        _create_section_label(f"User #{user_id}", icon_name="user"),
        cls="flex justify-between items-center mb-4",
    )


def _create_timestamp_footer(created_at: datetime) -> Div:
    """
    Create the timestamp footer for the inference card.

    Displays the UTC timestamp of when the inference was completed,
    formatted in a human-readable ISO-like format with a clock icon.

    Parameters
    ----------
    created_at : datetime
        UTC timestamp recorded by the database at insert time.

    Returns
    -------
    Div
        FastHTML div container holding the formatted timestamp,
        right-aligned and styled as subtle metadata.
    """
    return Div(
        Span(
            create_icon("clock", size=12, cls="inline-block mr-1 align-middle opacity-60"),
            created_at.strftime("%Y-%m-%d %H:%M UTC"),
            cls="text-xs text-base-content/40",
        ),
        cls="flex justify-end",
    )


def create_inference_card(
    input_text: str,
    output_text: str,
    created_at: datetime,
    user_id: int | None = None,
) -> FT:
    """
    Create a single inference history record as a card.

    Displays the submitted prompt, the model response, and the UTC
    timestamp of the completed run. When user_id is provided it is
    rendered in the card header, which is the case on the admin
    statistics panel. On the user history page user_id is omitted
    since the page already belongs to a single authenticated user.

    Each section includes a leading icon for visual distinction:
    prompt uses a chat bubble, response uses sparkles, user header
    uses a user icon, and timestamp uses a clock icon.

    Parameters
    ----------
    input_text : str
        Raw text submitted by the user as the model prompt.
    output_text : str
        Text generated by the model in response to the prompt.
    created_at : datetime
        UTC timestamp recorded by the database at insert time.
    user_id : int or None
        Primary key of the user who submitted the request. When
        provided it is displayed in the card header for administrative
        context. Default is None.

    Returns
    -------
    FT
        Div containing the formatted inference record card.
    """
    children: list[FT] = []

    if user_id is not None:
        children.append(_create_user_header(user_id))

    children.extend(
        [
            _create_content_block("Prompt", input_text, icon_name="chat-bubble-left"),
            _create_content_block("Response", output_text, icon_name="sparkles"),
            _create_timestamp_footer(created_at),
        ]
    )

    return Div(
        *children,
        cls="card bg-base-100 shadow-sm p-6 mb-4",
    )