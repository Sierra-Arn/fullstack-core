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

# packages/server/src/server/shared/ui/navbar.py
from fasthtml.common import Nav, Div, A, FT, Form, Button
from postgres_lib import Role
from ..utils import create_icon
from ...config import server_config, RoutePath


def _create_brand_link() -> A:
    """
    Create the application brand link for the navigation bar.

    Returns
    -------
    A
        FastHTML anchor element displaying the application name
        and linking to the landing page.
    """
    return A(
        server_config.app_name,
        href=RoutePath.LANDING,
        cls="btn btn-ghost text-xl font-bold",
    )


def _create_nav_link(label: str, href: str, icon: str | None = None) -> A:
    """
    Create a styled navigation link with an optional leading icon.

    Parameters
    ----------
    label : str
        Visible text displayed inside the link.
    href : str
        Target URL the link points to.
    icon : str or None
        Optional Heroicon name to display before the label. When None,
        the link contains only text. Default is None.

    Returns
    -------
    A
        FastHTML anchor element styled as a ghost button with optional icon.
    """
    children = []
    if icon:
        children.append(create_icon(icon))
    children.append(label)

    return A(
        *children,
        href=href,
        cls="btn btn-ghost gap-2",
    )


def _create_logout_button() -> Form:
    """
    Create a logout form containing a submit button with icon.

    Returns
    -------
    Form
        FastHTML form element configured to send a POST request to the
        logout endpoint, styled as a ghost button with a leading icon.
    """
    return Form(
        Button(
            create_icon("arrow-right-on-rectangle"),
            "Logout",
            type="submit",
            cls="btn btn-ghost gap-2",
        ),
        method="post",
        action=RoutePath.LOGOUT,
    )


def create_navbar(role: Role = Role.UNAUTHENTICATED) -> FT:
    """
    Render the application navigation bar based on the user access role.

    Constructs a responsive navigation component with the application
    brand on the left and role-specific links on the right. The visible
    links are determined by the hierarchical role level: unauthenticated
    visitors see login and registration options, authenticated users see
    inference and collaboration links, moderators additionally see leads
    management, and administrators additionally see user management.
    The component strictly handles presentation logic, assuming that
    authentication and authorization resolution have already occurred
    in the route handler before this function is invoked.

    Parameters
    ----------
    role : Role
        Resolved access role of the current user. Default is
        UNAUTHENTICATED for anonymous visitors.

    Returns
    -------
    FT
        Fully assembled FastHTML navigation element ready for rendering.
    """
    links: list[FT] = []

    if role.level < Role.USER.level:
        links.extend(
            [
                _create_nav_link("Login", RoutePath.LOGIN, icon="arrow-right-on-rectangle"),
                _create_nav_link("Register", RoutePath.REGISTER, icon="user-plus"),
                _create_nav_link("Collaborate", RoutePath.COLLABORATE, icon="briefcase"),
            ]
        )
    else:
        links.extend(
            [
                _create_nav_link("Inference", RoutePath.INFERENCE, icon="sparkles"),
                _create_nav_link("History", RoutePath.INFERENCE_HISTORY, icon="clock"),
                _create_nav_link("Collaborate", RoutePath.COLLABORATE, icon="briefcase"),
            ]
        )

        if role.level >= Role.MODERATOR.level:
            links.append(
                _create_nav_link("Leads", RoutePath.LEADS, icon="inbox")
            )

        if role.level >= Role.ADMIN.level:
            links.append(
                _create_nav_link("Users", RoutePath.USERS, icon="users")
            )

        links.append(_create_logout_button())

    return Nav(
        Div(
            _create_brand_link(),
            cls="navbar-start",
        ),
        Div(
            *links,
            cls="navbar-end",
        ),
        cls="navbar bg-base-100 shadow-sm",
    )