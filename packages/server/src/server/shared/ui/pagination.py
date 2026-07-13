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

# packages/server/src/server/shared/ui/pagination.py
from fasthtml.common import Div, Button, Span, FT
from ..utils import create_icon


def _create_page_button(
    page: int,
    *,
    current_page: int,
    endpoint: str,
    target: str,
    icon_name: str | None = None,
    label: str | None = None,
) -> FT:
    """
    Create a pagination page button.

    Generates a button element that either acts as a disabled indicator
    for the current page or an interactive HTMX trigger for navigating
    to a different page.

    Parameters
    ----------
    page : int
        The page number this button represents.
    current_page : int
        The currently active page number.
    endpoint : str
        The HTMX request endpoint to fetch the new page content.
    target : str
        The CSS selector of the element to swap the new content into.
    icon_name : str or None
        Optional Heroicon name to display inside the button. When
        provided, the icon is rendered instead of or alongside text.
        Default is None.
    label : str or None
        Custom text to display inside the button. Default is the
        string representation of the page number if not provided.

    Returns
    -------
    FT
        FastHTML button element configured with appropriate styles
        and HTMX attributes.
    """
    is_current = page == current_page

    attrs = {}

    if not is_current:
        attrs.update(
            {
                "hx_get": f"{endpoint}?page={page}",
                "hx_target": target,
                "hx_swap": "innerHTML",
            }
        )

    children = []

    if icon_name:
        children.append(create_icon(icon_name, size=16))

    if label is not None:
        children.append(label)
    elif not icon_name:
        children.append(str(page))

    return Button(
        *children,
        disabled=is_current,
        cls=(
            "btn btn-sm btn-active"
            if is_current
            else "btn btn-sm btn-ghost"
        ),
        **attrs,
    )


def _create_ellipsis() -> Span:
    """
    Create a pagination ellipsis separator.

    Returns
    -------
    Span
        FastHTML span element displaying an ellipsis icon, styled as a
        disabled button to visually separate page groups.
    """
    return Span(
        create_icon("ellipsis-horizontal", size=16, cls="opacity-40"),
        cls="btn btn-sm btn-disabled px-2",
    )


def _visible_pages(
    current_page: int,
    total_pages: int,
    window: int = 2,
) -> list[int | None]:
    """
    Calculate the sequence of visible page numbers for the pagination control.

    Determines which page numbers should be rendered as buttons and where
    ellipsis separators should be placed to keep the control compact.
    The sequence always includes the first page, the last page, and a
    sliding window of pages around the current page.

    Parameters
    ----------
    current_page : int
        The currently active page number.
    total_pages : int
        The total number of pages available.
    window : int
        The number of pages to show on each side of the current page.
        Default is 2.

    Returns
    -------
    list[int | None]
        Ordered list of page numbers to display. None values represent
        positions where an ellipsis separator should be rendered.
    """
    pages: set[int] = {
        1,
        total_pages,
    }

    for page in range(
        current_page - window,
        current_page + window + 1,
    ):
        if 1 <= page <= total_pages:
            pages.add(page)

    result: list[int | None] = []

    previous = None

    for page in sorted(pages):
        if previous is not None and page - previous > 1:
            result.append(None)

        result.append(page)
        previous = page

    return result


def create_pagination(
    current_page: int,
    total_pages: int,
    endpoint: str,
    target: str,
) -> FT:
    """
    Create responsive HTMX pagination controls.

    Constructs a complete pagination bar with previous and next navigation
    buttons with icons, numbered page buttons, and ellipsis separators for
    large page ranges. Uses HTMX for seamless asynchronous page transitions.

    Example output:

        [←] 1 ... 8 9 [10] 11 12 ... 50 [→]

    Parameters
    ----------
    current_page : int
        The currently active one-based page number.
    total_pages : int
        The total number of pages available.
    endpoint : str
        The HTMX request endpoint to fetch the new page content.
    target : str
        The CSS selector of the element to swap the new content into.

    Returns
    -------
    FT
        FastHTML container element holding all pagination buttons,
        or an empty container if there is only one page or fewer.
    """
    if total_pages <= 1:
        return Div()

    buttons: list[FT] = []

    # Previous
    if current_page > 1:
        buttons.append(
            _create_page_button(
                current_page - 1,
                current_page=current_page,
                endpoint=endpoint,
                target=target,
                icon_name="chevron-left",
            )
        )

    else:
        buttons.append(
            Button(
                create_icon("chevron-left", size=16, cls="opacity-40"),
                disabled=True,
                cls="btn btn-sm btn-disabled",
            )
        )

    # Pages
    for page in _visible_pages(
        current_page,
        total_pages,
    ):
        if page is None:
            buttons.append(_create_ellipsis())
        else:
            buttons.append(
                _create_page_button(
                    page,
                    current_page=current_page,
                    endpoint=endpoint,
                    target=target,
                )
            )

    # Next
    if current_page < total_pages:
        buttons.append(
            _create_page_button(
                current_page + 1,
                current_page=current_page,
                endpoint=endpoint,
                target=target,
                icon_name="chevron-right",
            )
        )

    else:
        buttons.append(
            Button(
                create_icon("chevron-right", size=16, cls="opacity-40"),
                disabled=True,
                cls="btn btn-sm btn-disabled",
            )
        )

    return Div(
        *buttons,
        cls="join flex justify-center mt-4",
    )