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

# packages/server/src/server/shared/utils.py
from math import ceil
from starlette import status
from starlette.responses import HTMLResponse
from fasthtml.common import to_xml, Img, FT


def html_response(content: FT, status_code: int = status.HTTP_200_OK) -> HTMLResponse:
    """
    Convert a FastHTML FT element to an HTMLResponse.

    Parameters
    ----------
    content : FT
        FastHTML element to serialize.
    status_code : int
        HTTP status code. Default is 200.

    Returns
    -------
    HTMLResponse
        Response with serialized HTML content.
    """
    return HTMLResponse(content=to_xml(content), status_code=status_code)


def create_icon(
    name: str,
    size: int = 24,
    *,
    cls: str = "",
) -> FT:
    """
    Render a Heroicon image element for use throughout the application.

    Icons are loaded from the static assets directory where Heroicons
    SVG files are stored after the build step. Outline variants are
    used by default for a consistent visual weight across the UI.

    Parameters
    ----------
    name : str
        Icon filename without extension, matching the Heroicons naming
        convention such as arrow-right-on-rectangle or user-plus.
    size : int
        Width and height in pixels for the icon. Default is 24, which
        matches the native Heroicons outline size. Use smaller values
        like 20 for compact UI elements such as navbar links.
    cls : str
        Additional CSS classes to apply to the img element. Useful for
        adjusting opacity, colors, or spacing. Default is empty string.

    Returns
    -------
    FT
        FastHTML img element pointing to the static icon file.
    """
    return Img(
        src=f"/static/icons/outline/{name}.svg",
        alt="",
        width=str(size),
        height=str(size),
        cls=cls,
    )


def calculate_pagination(
    total: int,
    page_size: int,
    current_page: int = 1,
) -> tuple[int, int, int]:
    """
    Calculate pagination parameters for database queries.

    Computes the total number of pages and the database offset for
    the current page. Ensures at least one page exists even when
    there are no records.

    Parameters
    ----------
    total : int
        Total number of records in the dataset.
    page_size : int
        Number of records per page.
    current_page : int
        The currently active one-based page number. Default is 1.

    Returns
    -------
    skip : int
        Database offset for the current page (zero-based).
    total_pages : int
        Total number of pages available (minimum 1).
    current_page : int
        The validated current page number.
    """
    total_pages = max(1, ceil(total / page_size))
    current_page = max(1, min(current_page, total_pages))
    skip = (current_page - 1) * page_size

    return skip, total_pages, current_page
