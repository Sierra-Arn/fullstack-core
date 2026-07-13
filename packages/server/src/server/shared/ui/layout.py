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

# packages/server/src/server/shared/ui/layout.py
from fasthtml.common import (
    Html, Head, Body, Title,
    Link, Script, Main, FT,
    Div, H2, P
)
from postgres_lib import Role
from .navbar import create_navbar
from .footer import create_footer
from ...config import server_config


def create_layout(
    *content: FT,
    title: str | None = None,
    role: Role = Role.UNAUTHENTICATED,
    contained: bool = True,
) -> FT:
    """
    Create the complete application HTML shell.

    Assembles the shared document structure used by all pages, including
    document metadata, global stylesheet references, the role-aware
    navigation bar, the main content area, the global footer, and
    client-side script references. The function strictly handles
    presentation composition, assuming that authentication and
    authorization resolution have already occurred in the route handler.

    Parameters
    ----------
    *content : FT
        One or more FastHTML elements to be rendered inside the main
        content area of the page.
    title : str or None
        Optional page-specific title. When provided, it is prepended
        to the application name with a separator to form the full
        document title. When None, only the application name is used.
    role : Role
        Resolved access role of the current user. Passed directly to
        the navbar component to determine which navigation links to
        display. Default is UNAUTHENTICATED for anonymous visitors.
    contained : bool
        Whether the main content area should be wrapped in a centered
        container with horizontal padding. When False, the content
        spans the full viewport width. Default is True.

    Returns
    -------
    FT
        Fully assembled FastHTML Html element representing the complete
        document, ready to be returned from a route handler.
    """
    page_title = (
        f"{title} — {server_config.app_name}"
        if title
        else server_config.app_name
    )

    main_classes = (
        "container mx-auto px-4 py-8"
        if contained
        else ""
    )

    return Html(
        Head(
            Title(page_title),
            Link(
                rel="stylesheet",
                href="/static/css/styles.css",
            ),
        ),
        Body(
            create_navbar(role),
            Main(
                *content,
                cls=main_classes,
            ),
            create_footer(),
            Script(
                src="/static/js/index.js",
            ),
            cls="min-h-screen flex flex-col bg-base-200",
        ),
        lang="en",
        data_theme=server_config.ui_theme,
    )


def create_page_header(
    title: str,
    description: str | None = None,
) -> Div:
    """
    Create a standard page header with title and optional description.

    Provides consistent styling for page headers across the application.
    Used at the top of main content areas to establish visual hierarchy.

    Parameters
    ----------
    title : str
        Main heading text displayed prominently.
    description : str or None
        Optional descriptive text displayed below the title in subdued
        styling. When None, only the title is rendered. Default is None.

    Returns
    -------
    Div
        FastHTML div container holding the header elements.
    """
    children = [
        H2(title, cls="text-2xl font-bold mb-2"),
    ]

    if description:
        children.append(
            P(description, cls="text-base-content/60 mb-8")
        )

    return Div(*children)