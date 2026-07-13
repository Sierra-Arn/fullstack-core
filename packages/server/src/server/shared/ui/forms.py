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

# packages/server/src/server/shared/ui/forms.py
from fasthtml.common import Div, Label, P, FT


def create_form_control(
    label_text: str,
    field_id: str,
    field_element: FT,
    *,
    label_hint: str | None = None,
    margin_bottom: str = "mb-4",
) -> Div:
    """
    Create a standard form control consisting of a label and an input element.

    Encapsulates the repetitive boilerplate required to build accessible
    and consistently styled form fields. Automatically handles the
    correct attribute binding between the label and the input element.

    Parameters
    ----------
    label_text : str
        Primary text displayed inside the label element.
    field_id : str
        Unique identifier used for both the input element and the
        label to ensure proper accessibility binding.
    field_element : FT
        The actual input FastHTML element to be rendered below the label.
    label_hint : str or None
        Optional secondary text displayed next to the primary label
        to provide additional context, such as marking a field as
        optional. Default is None.
    margin_bottom : str
        Tailwind CSS class applied to the outer container to control
        vertical spacing. Default is "mb-4".

    Returns
    -------
    Div
        FastHTML div container holding the label and field element,
        styled as a standard form control.
    """
    label_children = [label_text]

    if label_hint:
        label_children.append(
            P(
                label_hint,
                cls="text-base-content/40 text-xs",
            )
        )

    label_classes = "label label-text"
    if label_hint:
        label_classes += " flex items-center gap-1"

    return Div(
        Label(
            *label_children,
            fr=field_id,
            cls=label_classes,
        ),
        field_element,
        cls=f"form-control {margin_bottom}",
    )


def create_form_card(*content: FT) -> Div:
    """
    Create a centered card container for form content.

    Provides consistent styling for form pages with a shadow, rounded
    corners, and constrained width. Used as the outer wrapper for
    authentication forms and other standalone form interfaces.

    Parameters
    ----------
    *content : FT
        One or more FastHTML elements to be rendered inside the card.

    Returns
    -------
    Div
        FastHTML div container styled as a centered card with shadow.
    """
    return Div(
        *content,
        cls="card bg-base-100 shadow-sm p-8 w-full max-w-md",
    )