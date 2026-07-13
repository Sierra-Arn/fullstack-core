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

# packages/server/src/server/shared/ui/confirmation_modal.py
from fasthtml.common import Div, H3, P, Button


def create_confirmation_modal(
    modal_id: str,
    title: str,
    message: str,
    confirm_label: str = "Confirm",
    cancel_label: str = "Cancel",
    *,
    confirm_action: str = "",
    confirm_hx_post: str | None = None,
    confirm_hx_target: str | None = None,
    confirm_hx_vals: str | None = None,
) -> Div:
    """
    Create a DaisyUI confirmation modal with Alpine.js state management.

    Renders a modal dialog controlled by Alpine.js reactive state. The
    modal is shown when the open flag is true and hidden otherwise.
    Includes confirm and cancel buttons with optional HTMX attributes
    for asynchronous server requests.

    Parameters
    ----------
    modal_id : str
        Unique identifier for the modal container. Used for Alpine.js
        state management and CSS targeting.
    title : str
        Heading text displayed at the top of the modal.
    message : str
        Descriptive text explaining the action being confirmed.
    confirm_label : str
        Text displayed on the confirm button. Default is "Confirm".
    cancel_label : str
        Text displayed on the cancel button. Default is "Cancel".
    confirm_action : str
        Alpine.js expression to execute when confirm is clicked.
        Typically sets open=false to close the modal. Default is "".
    confirm_hx_post : str or None
        HTMX POST endpoint for the confirm button. Default is None.
    confirm_hx_target : str or None
        HTMX target selector for the confirm button. Default is None.
    confirm_hx_vals : str or None
        HTMX values expression for the confirm button. Default is None.

    Returns
    -------
    Div
        FastHTML div containing the modal with confirm and cancel buttons.
    """
    confirm_attrs = {
        "@click": confirm_action or "open = false",
    }

    if confirm_hx_post:
        confirm_attrs["hx-post"] = confirm_hx_post
    if confirm_hx_target:
        confirm_attrs["hx-target"] = confirm_hx_target
    if confirm_hx_vals:
        confirm_attrs[":hx-vals"] = confirm_hx_vals
    if confirm_hx_post or confirm_hx_target:
        confirm_attrs["hx-swap"] = "outerHTML"

    return Div(
        Div(
            Div(
                H3(title, cls="font-semibold text-lg"),
                P(message, cls="text-base-content/60 text-sm mt-2"),
                Div(
                    Button(
                        confirm_label,
                        cls="btn btn-primary btn-sm",
                        **confirm_attrs,
                    ),
                    Button(
                        cancel_label,
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
        id=modal_id,
    )