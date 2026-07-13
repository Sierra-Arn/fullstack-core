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

# packages/server/src/server/shared/ui/error_page.py
from fasthtml.common import Div, H1, H2, P, A, FT
from postgres_lib import Role
from .layout import create_layout
from ...config import RoutePath


def _create_error_heading(status_code: int) -> H1:
    """
    Create the large status code heading for the error page.

    Parameters
    ----------
    status_code : int
        HTTP status code of the error.

    Returns
    -------
    H1
        FastHTML heading element displaying the status code as a
        large bold number styled with the primary color.
    """
    return H1(
        str(status_code),
        cls="text-8xl font-bold text-primary mb-4",
    )


def _create_error_title(title: str) -> H2:
    """
    Create the human-readable error title.

    Parameters
    ----------
    title : str
        Short error name such as "Not Found" or "Internal Server Error".

    Returns
    -------
    H2
        FastHTML heading element displaying the error title.
    """
    return H2(
        title,
        cls="text-2xl font-semibold text-base-content mb-4",
    )


def _create_error_detail(detail: str) -> P:
    """
    Create the detailed error description.

    Parameters
    ----------
    detail : str
        Longer explanation of what went wrong and what the user can do.

    Returns
    -------
    P
        FastHTML paragraph element displaying the error detail in
        subdued text with constrained width for readability.
    """
    return P(
        detail,
        cls="text-base-content/60 mb-8 max-w-md text-center",
    )


def _create_landing_link() -> A:
    """
    Create the call-to-action button linking back to the landing page.

    Returns
    -------
    A
        FastHTML anchor element styled as a primary button.
    """
    return A(
        "Go to Landing",
        href=RoutePath.LANDING,
        cls="btn btn-primary",
    )


def _create_error_content(
    status_code: int,
    title: str,
    detail: str,
) -> Div:
    """
    Create the centered error content block.

    Assembles the status code heading, error title, detail description,
    and landing page navigation link into a vertically stacked, centered layout.

    Parameters
    ----------
    status_code : int
        HTTP status code of the error.
    title : str
        Short human-readable error name.
    detail : str
        Longer explanation of the error.

    Returns
    -------
    Div
        FastHTML div container holding all error content elements,
        centered both horizontally and vertically.
    """
    return Div(
        Div(
            _create_error_heading(status_code),
            _create_error_title(title),
            _create_error_detail(detail),
            _create_landing_link(),
            cls="flex flex-col items-center text-center",
        ),
        cls="flex justify-center items-center min-h-[70vh]",
    )


def create_error_page(
    status_code: int,
    title: str,
    detail: str,
    role: Role = Role.UNAUTHENTICATED,
) -> FT:
    """
    Create a styled error page sharing the application layout.

    Used by middleware and centralized exception handlers to ensure the
    user always sees a styled page rather than a raw stack trace or plain
    text response. Accepts any HTTP error status code and renders it with
    a human-readable title and detail message.

    Parameters
    ----------
    status_code : int
        HTTP status code of the error, displayed as the large heading.
    title : str
        Short human-readable error name displayed below the status code.
        For example "Not Found" or "Too Many Requests".
    detail : str
        Longer explanation of what went wrong and what the user can do.
    role : Role
        Resolved access role of the current user. Passed to the global
        layout to determine which navigation links are displayed in the
        navbar. Default is UNAUTHENTICATED for anonymous visitors or
        when session resolution fails.

    Returns
    -------
    FT
        Complete HTML document rendered via create_layout, containing the
        styled error content with the application navbar and footer.
    """
    return create_layout(
        _create_error_content(status_code, title, detail),
        title=f"{status_code} {title}",
        role=role,
    )