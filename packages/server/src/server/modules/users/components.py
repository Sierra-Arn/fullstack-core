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

# packages/server/src/server/modules/users/components.py
from datetime import datetime
from fasthtml.common import Div, Span, Button, H3, P, Select, Option, FT
from postgres_lib import Role
from ...shared import create_icon
from ...config import RoutePath


_ALL_ROLES = [Role.USER, Role.MODERATOR, Role.ADMIN]

_ROLE_LABELS: dict[Role, str] = {
    Role.USER: "User",
    Role.MODERATOR: "Moderator",
    Role.ADMIN: "Admin",
}

_ROLE_BADGE_STYLES: dict[Role, str] = {
    Role.USER: "badge badge-ghost",
    Role.MODERATOR: "badge badge-info",
    Role.ADMIN: "badge badge-primary",
}


def _create_role_badge(role: Role) -> Span:
    """
    Create a colored badge displaying the user role.

    Parameters
    ----------
    role : Role
        Current access role of the user.

    Returns
    -------
    Span
        FastHTML span element styled as a role badge.
    """
    return Span(
        _ROLE_LABELS[role],
        cls=_ROLE_BADGE_STYLES[role],
    )


def _create_user_header(email: str, role: Role) -> Div:
    """
    Create the user card header with email and role badge.

    Parameters
    ----------
    email : str
        Email address of the user account.
    role : Role
        Current access role of the user.

    Returns
    -------
    Div
        FastHTML div containing the email and role badge,
        arranged horizontally with space between.
    """
    return Div(
        Div(
            create_icon("envelope", size=16, cls="opacity-60"),
            Span(
                email,
                cls="font-semibold text-base-content",
            ),
            cls="flex items-center gap-2",
        ),
        _create_role_badge(role),
        cls="flex items-center justify-between",
    )


def _create_user_metadata(
    user_id: int,
    inference_runs_count: int,
    created_at: datetime,
) -> Div:
    """
    Create the user metadata section with ID, runs count, and join date.

    Parameters
    ----------
    user_id : int
        Primary key of the user record.
    inference_runs_count : int
        Total number of completed model inference runs.
    created_at : datetime
        UTC timestamp when the account was registered.

    Returns
    -------
    Div
        FastHTML div containing the metadata spans arranged horizontally.
    """
    return Div(
        Div(
            create_icon("identification", size=14, cls="opacity-60"),
            Span(f"ID: {user_id}", cls="text-xs text-base-content/50"),
            cls="flex items-center gap-1",
        ),
        Div(
            create_icon("sparkles", size=14, cls="opacity-60"),
            Span(f"Runs: {inference_runs_count}", cls="text-xs text-base-content/50"),
            cls="flex items-center gap-1",
        ),
        Div(
            create_icon("calendar", size=14, cls="opacity-60"),
            Span(
                f"Joined: {created_at.strftime('%Y-%m-%d')}",
                cls="text-xs text-base-content/50",
            ),
            cls="flex items-center gap-1",
        ),
        cls="flex gap-4 mt-2",
    )


def _create_role_select(user_id: int, current_role: Role) -> Div:
    """
    Create a role selection dropdown for the user card.

    Renders a select element populated with all available roles. The
    current role is pre-selected. When the user changes the selection,
    an Alpine.js handler stores the new value and opens the confirmation
    modal before any server request is issued.

    Parameters
    ----------
    user_id : int
        Primary key of the user record.
    current_role : Role
        Current access role of the user, used to pre-select the
        matching option in the dropdown.

    Returns
    -------
    Div
        FastHTML div containing the styled select element.
    """
    options = [
        Option(
            _ROLE_LABELS[role],
            value=role,
            selected=(role == current_role),
        )
        for role in _ALL_ROLES
    ]

    return Div(
        Select(
            *options,
            cls="select select-bordered select-sm w-full",
            **{
                "x-model": "pending_role",
                "@change": "if ($event.target.value !== current_role) open = true",
            },
        ),
        cls="w-48",
    )


def _create_action_buttons(user_id: int) -> Div:
    """
    Create the delete action button for the user card.

    Parameters
    ----------
    user_id : int
        Primary key of the user record.

    Returns
    -------
    Div
        FastHTML div containing the delete button.
    """
    return Div(
        Button(
            create_icon("trash", size=16, cls="mr-1"),
            "Delete Account",
            **{"@click": "open = true; pending_action = 'delete'"},
            cls="btn btn-sm btn-error",
        ),
    )


def _create_confirmation_modal(user_id: int) -> Div:
    """
    Create the DaisyUI confirmation modal for user actions.

    The modal is controlled by Alpine.js reactive state. Two conditional
    sections are rendered inside: one for role changes triggered by the
    select dropdown, and one for account deletion triggered by the delete
    button. Each section contains a confirm button bound to the
    appropriate HTMX endpoint and a shared cancel button.

    The pending_role Alpine.js value holds the target role string chosen
    in the dropdown. The pending_action value holds the action identifier
    for the delete flow. These are passed to HTMX requests via hx-vals
    so the server receives the chosen values without hidden form fields.

    Parameters
    ----------
    user_id : int
        Primary key of the user record, used to construct POST URLs.

    Returns
    -------
    Div
        FastHTML div containing the modal with conditional confirm
        sections and a cancel button.
    """
    return Div(
        Div(
            Div(
                H3(
                    "Confirm action",
                    cls="font-semibold text-lg",
                ),
                P(
                    "This action cannot be undone. Are you sure?",
                    cls="text-base-content/60 text-sm mt-2",
                ),
                Div(
                    Button(
                        create_icon("shield-check", size=16, cls="mr-1"),
                        "Change Role",
                        **{
                            "x-show": "pending_action !== 'delete'",
                            "@click": "open = false",
                            "hx-post": RoutePath.USER_ROLE.format(id=user_id),
                            ":hx-vals": "JSON.stringify({role: pending_role})",
                            "hx-swap": "outerHTML",
                            "hx-target": f"#user-{user_id}",
                        },
                        cls="btn btn-primary btn-sm",
                    ),
                    Button(
                        create_icon("trash", size=16, cls="mr-1"),
                        "Delete",
                        **{
                            "x-show": "pending_action === 'delete'",
                            "@click": "open = false",
                            "hx-post": RoutePath.USER_DELETE.format(id=user_id),
                            "hx-swap": "outerHTML",
                            "hx-target": f"#user-{user_id}",
                        },
                        cls="btn btn-error btn-sm",
                    ),
                    Button(
                        "Cancel",
                        **{
                            "@click": "open = false; pending_role = current_role",
                        },
                        cls="btn btn-ghost btn-sm",
                    ),
                    cls="flex gap-2 mt-4 justify-end",
                ),
                cls="bg-base-100 rounded-box p-6 w-96",
            ),
            cls="flex items-center justify-center",
        ),
        **{
            "x-show": "open",
            ":class": "{ 'modal-open': open }",
            "@keydown.escape.window": "open = false; pending_role = current_role",
        },
        cls="modal",
    )


def create_user_card(
    user_id: int,
    email: str,
    role: Role,
    inference_runs_count: int,
    created_at: datetime,
) -> FT:
    """
    Create a single user record card for the users page.

    Displays user details, a role selection dropdown, and a delete button.
    Changing the role via the dropdown opens a DaisyUI confirmation modal
    managed by Alpine.js before issuing an HTMX POST request. The delete
    button follows the same confirmation pattern.

    The Alpine.js x-data scope holds three reactive values: open controls
    modal visibility, current_role stores the initial role for reset on
    cancel, and pending_role tracks the dropdown selection. The
    pending_action value distinguishes between role change and delete
    flows inside the shared modal.

    Parameters
    ----------
    user_id : int
        Primary key of the user record, used to construct POST URLs.
    email : str
        Email address of the user account.
    role : Role
        Current access role of the user. Pre-selects the matching
        option in the role dropdown.
    inference_runs_count : int
        Total number of completed model inference runs for this account.
    created_at : datetime
        UTC timestamp when the account was registered.

    Returns
    -------
    FT
        Div containing the user card with role dropdown and modal.
    """
    return Div(
        Div(
            _create_user_header(email, role),
            _create_user_metadata(user_id, inference_runs_count, created_at),
            cls="mb-4",
        ),
        Div(
            _create_role_select(user_id, role),
            _create_action_buttons(user_id),
            cls="flex items-center gap-2",
        ),
        _create_confirmation_modal(user_id),
        id=f"user-{user_id}",
        cls="card bg-base-100 shadow-sm p-6 mb-4",
        **{
            "x-data": (
                "{ open: false, "
                "current_role: '" + role + "', "
                "pending_role: '" + role + "', "
                "pending_action: '' }"
            ),
        },
    )