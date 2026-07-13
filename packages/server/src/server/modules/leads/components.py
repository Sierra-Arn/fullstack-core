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

# packages/server/src/server/modules/leads/components.py
from fasthtml.common import Div, P, Span, Button, H3, FT
from postgres_lib import LeadStatus
from ...shared import create_icon


def _create_status_badge(status: LeadStatus) -> Span:
    """
    Create a colored badge displaying the lead status.

    Parameters
    ----------
    status : LeadStatus
        Current follow-up status of the lead.

    Returns
    -------
    Span
        FastHTML span element styled as a status badge.
    """
    styles: dict[LeadStatus, str] = {
        LeadStatus.NEW: "badge badge-warning",
        LeadStatus.IN_PROGRESS: "badge badge-info",
        LeadStatus.ANSWERED: "badge badge-success",
        LeadStatus.REJECTED: "badge badge-error",
    }

    return Span(
        status.value.replace("_", " ").title(),
        cls=styles[status],
    )


def _create_lead_header(name: str, status: LeadStatus) -> Div:
    """
    Create the lead card header with name and status badge.

    Parameters
    ----------
    name : str
        Name provided by the visitor on submission.
    status : LeadStatus
        Current follow-up status of the lead.

    Returns
    -------
    Div
        FastHTML div containing the name and status badge,
        arranged horizontally with space between.
    """
    return Div(
        H3(
            name,
            cls="font-semibold text-base-content",
        ),
        _create_status_badge(status),
        cls="flex items-center justify-between",
    )


def _create_lead_contact(email: str, company: str | None) -> Div:
    """
    Create the lead contact information section.

    Parameters
    ----------
    email : str
        Contact email provided by the visitor.
    company : str or None
        Optional organization name. When None, only the email is shown.

    Returns
    -------
    Div
        FastHTML div containing the contact details stacked vertically.
    """
    children = [
        Div(
            create_icon("envelope", size=14, cls="inline-block mr-1 opacity-60"),
            Span(
                email,
                cls="text-sm text-base-content/60",
            ),
            cls="flex items-center",
        ),
    ]

    if company:
        children.append(
            Div(
                create_icon("building-office", size=14, cls="inline-block mr-1 opacity-60"),
                Span(
                    company,
                    cls="text-sm text-base-content/60",
                ),
                cls="flex items-center",
            )
        )

    return Div(
        *children,
        cls="flex flex-col gap-1 mt-2",
    )


def _create_lead_message(message: str) -> Div:
    """
    Create the lead message section with label and content.

    Parameters
    ----------
    message : str
        Free-form description of the collaboration request.

    Returns
    -------
    Div
        FastHTML div containing the labeled message content.
    """
    return Div(
        Div(
            create_icon("chat-bubble-left", size=14, cls="inline-block mr-1"),
            Span(
                "Message",
                cls="text-xs font-semibold text-base-content/50 uppercase tracking-wide",
            ),
            cls="flex items-center",
        ),
        P(
            message,
            cls="text-base-content mt-1",
        ),
        cls="mb-4",
    )


def _create_action_buttons(
    lead_id: int,
    status: LeadStatus,
) -> list[Button] | None:
    """
    Create the status transition action buttons for the lead card.

    Only valid transitions for the current status are rendered. Terminal
    statuses (ANSWERED, REJECTED) return None, resulting in no buttons.

    Parameters
    ----------
    lead_id : int
        Primary key of the lead record.
    status : LeadStatus
        Current follow-up status of the lead.

    Returns
    -------
    list[Button] or None
        List of action buttons for valid transitions, or None if no
        transitions are available.
    """
    transitions: dict[LeadStatus, list[LeadStatus]] = {
        LeadStatus.NEW: [LeadStatus.IN_PROGRESS, LeadStatus.ANSWERED, LeadStatus.REJECTED],
        LeadStatus.IN_PROGRESS: [LeadStatus.ANSWERED, LeadStatus.REJECTED],
        LeadStatus.ANSWERED: [],
        LeadStatus.REJECTED: [],
    }

    labels: dict[LeadStatus, str] = {
        LeadStatus.IN_PROGRESS: "Start Processing",
        LeadStatus.ANSWERED: "Mark Answered",
        LeadStatus.REJECTED: "Reject",
    }

    icons: dict[LeadStatus, str] = {
        LeadStatus.IN_PROGRESS: "play",
        LeadStatus.ANSWERED: "check-circle",
        LeadStatus.REJECTED: "x-circle",
    }

    styles: dict[LeadStatus, str] = {
        LeadStatus.IN_PROGRESS: "btn btn-sm btn-info",
        LeadStatus.ANSWERED: "btn btn-sm btn-success",
        LeadStatus.REJECTED: "btn btn-sm btn-error",
    }

    available = transitions[status]

    if not available:
        return None

    return [
        Button(
            create_icon(icons[target], size=16, cls="mr-1"),
            labels[target],
            **{
                "@click": f"open = true; pending_status = '{target.value}'",
            },
            cls=styles[target],
        )
        for target in available
    ]


def _create_confirmation_modal(lead_id: int) -> Div:
    """
    Create the DaisyUI confirmation modal for status changes.

    The modal is controlled by Alpine.js reactive state. When the
    administrator confirms, an HTMX POST request is issued with the
    target status passed via hx-vals.

    Parameters
    ----------
    lead_id : int
        Primary key of the lead record, used to construct the POST URL.

    Returns
    -------
    Div
        FastHTML div containing the modal with confirm and cancel buttons.
    """
    return Div(
        Div(
            Div(
                H3(
                    "Confirm status change",
                    cls="font-semibold text-lg",
                ),
                P(
                    "Are you sure you want to change the status of this request?",
                    cls="text-base-content/60 text-sm mt-2",
                ),
                Div(
                    Button(
                        "Confirm",
                        **{
                            "@click": "open = false",
                            "hx-post": f"/leads/{lead_id}/status",
                            ":hx-vals": "JSON.stringify({status: pending_status})",
                            "hx-swap": "outerHTML",
                            "hx-target": f"#lead-{lead_id}",
                        },
                        cls="btn btn-primary btn-sm",
                    ),
                    Button(
                        "Cancel",
                        **{"@click": "open = false"},
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
            "@keydown.escape.window": "open = false",
        },
        cls="modal",
    )


def create_lead_card(
    lead_id: int,
    name: str,
    email: str,
    company: str | None,
    message: str,
    status: LeadStatus,
) -> FT:
    """
    Create a single collaboration request card for the leads page.

    Displays all submitted fields and a context-sensitive set of status
    transition buttons. Each button opens a DaisyUI confirmation modal
    managed by Alpine.js before issuing an HTMX POST request to advance
    the lead status. Only valid transitions for the current status are
    rendered; terminal statuses (ANSWERED, REJECTED) show no action buttons.

    The Alpine.js x-data scope holds two reactive values: open controls
    modal visibility and pending_status carries the target status string
    to be submitted when the moderator or administrator confirms the action.
    The pending_status value is passed to the HTMX request via hx-vals so
    the server receives the chosen transition without a hidden form field.

    Parameters
    ----------
    lead_id : int
        Primary key of the lead record, used to construct the POST URL.
    name : str
        Name the visitor provided on submission.
    email : str
        Contact email the visitor provided on submission.
    company : str or None
        Optional organization name. When None the field is omitted.
    message : str
        Free-form description of the collaboration request.
    status : LeadStatus
        Current follow-up status of the request. Controls which transition
        buttons are rendered.

    Returns
    -------
    FT
        Div containing the lead card with confirmation modal.
    """
    children: list[FT] = [
        Div(
            _create_lead_header(name, status),
            _create_lead_contact(email, company),
            cls="mb-4",
        ),
        _create_lead_message(message),
    ]

    buttons = _create_action_buttons(lead_id, status)
    if buttons:
        children.append(
            Div(
                *buttons,
                cls="flex gap-2",
            )
        )

    children.append(_create_confirmation_modal(lead_id))

    return Div(
        *children,
        id=f"lead-{lead_id}",
        cls="card bg-base-100 shadow-sm p-6 mb-4",
        **{
            "x-data": "{ open: false, pending_status: '' }",
        },
    )